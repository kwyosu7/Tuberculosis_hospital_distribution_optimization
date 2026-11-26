"""Build district population tables in the Dryad layout (one-off; outputs are committed).

Input (not in the repo):
  POP_DIR/{year}_population_sigungu_age.csv   resident population by district and 10-year age (Korean names)
  RNRD_DIR/{year}_RNRD.txt                     pre-Dryad district files with Korean names, same row order as Dryad
Output:
  data_aux/sigungu_population/sigungu_population_age_{year}.csv
  columns: do/si, si/gun/gu, Population, g0_9, ..., g80_   (same rows and English names as sigungu_nd_age_{year}.csv)

python scripts/build_population_tables.py POP_DIR RNRD_DIR
"""
import sys

import pandas as pd

from tbopt import config, data

OUT = config.AUX_DIR / "sigungu_population"


def load_population(pop_dir, year):
    p = pd.read_csv(f"{pop_dir}/{year}_population_sigungu_age.csv", encoding="utf-8-sig", dtype=str)
    p.columns = ["sido", "sgg_ko", *p.columns[2:]]
    p["sgg_ko"] = p["sgg_ko"].str.strip()
    for c in config.AGE_GROUPS:
        p[c] = pd.to_numeric(p[c].str.replace(r"[ ,]", "", regex=True))
    return p.set_index(["sido", "sgg_ko"])[list(config.AGE_GROUPS)]


def korean_names(rnrd_dir, year):
    """Dryad (sido, English name) -> Korean district name, via the row-aligned pre-Dryad file."""
    d = data.load_district(year)
    rn = pd.read_csv(f"{rnrd_dir}/{year}_RNRD.txt", sep="\t")
    assert (rn[["h", "A", "N", "D"]].values == d[["h", "A", "N", "D"]].values).all(), year
    return dict(zip(zip(d["sido"], d["sigungu"]), rn["sigungu"].str.strip()))


def main(pop_dir, rnrd_dir):
    OUT.mkdir(parents=True, exist_ok=True)
    # the 2019 pre-Dryad file has English names; borrow the 2018 mapping
    names = {y: korean_names(rnrd_dir, y) for y in config.YEARS if y != 2019}
    names[2019] = names[2018]
    for year in config.YEARS:
        d = data.load_district(year)
        keys = [(s, names[year][(s, g)]) for s, g in zip(d["sido"], d["sigungu"])]
        counts = load_population(pop_dir, year).loc[keys].reset_index(drop=True)
        total = counts.sum(axis=1)
        out = pd.DataFrame({"do/si": d["sido"], "si/gun/gu": d["sigungu"], "Population": total})
        for a in config.AGE_GROUPS:
            out[f"g{a}"] = counts[a] / total
        out.to_csv(OUT / f"sigungu_population_age_{year}.csv", index=False)
        print(year, len(out), int(total.sum()))


if __name__ == "__main__":
    main(*sys.argv[1:3])
