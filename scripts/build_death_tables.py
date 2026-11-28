"""Build district all-cause death tables in the Dryad layout (one-off; outputs are committed).

Input (not in the repo):
  KOSIS_CSV   KOSIS 101_DT_1B80A18 export: deaths by district and 5-year age, both sexes, 2014-2022 (cp949)
  POP_DIR, RNRD_DIR   as in build_population_tables.py (Korean district names of the 228 Dryad districts)
Output:
  data_aux/sigungu_deaths/sigungu_deaths_age_{year}.csv
  columns: do/si, si/gun/gu, Deaths, q0_9, ..., q80_   (same rows and English names as sigungu_nd_age_{year}.csv)

python scripts/build_death_tables.py KOSIS_CSV POP_DIR RNRD_DIR

KOSIS rows have no province column. Cities with sub-districts (e.g. Suwon) appear both as a city total and
per sub-district; only the city row is kept, which matches the 228 Dryad districts. Names shared by several
provinces (Jung-gu, ...) are listed in administrative-code order, so the n-th occurrence belongs to the
n-th province (in code order) that has that name; this is checked against the neighbouring rows.
"""
import sys

import pandas as pd

from build_population_tables import korean_names, load_population
from tbopt import config, data

OUT = config.AUX_DIR / "sigungu_deaths"
RENAMED = {"남구(변동전)": "남구", "미추홀구": "남구", "군위군(변동전)": "군위군"}  # Incheon Nam-gu -> Michuhol-gu (2018)
FIXED = {"남구(변동전)": ("Incheon", "남구"), "미추홀구": ("Incheon", "남구"), "군위군(변동전)": ("Gyeongbuk", "군위군")}
AGE10 = {"0세": "0_9", "1 - 4세": "0_9", "5 - 9세": "0_9", "80세 이상": "80_"}
for lo in range(10, 80, 5):
    AGE10[f"{lo} - {lo + 4}세"] = f"{lo // 10 * 10}_{lo // 10 * 10 + 9}"


def target_names(pop_dir):
    """(sido, Korean name) of the 228 districts, in administrative-code order."""
    p = load_population(pop_dir, 2022).reset_index()
    return list(zip(p["sido"], p["sgg_ko"]))


def assign_sido(names, targets):
    """Province for each row of one age block (rows in KOSIS order)."""
    by_name = {}
    for sido, ko in targets:
        if (sido, ko) not in FIXED.values():  # renamed districts are placed by FIXED, not by order
            by_name.setdefault(ko, []).append(sido)
    seen, out, in_city = {}, [], False
    for n in names:
        # "-gu" rows right after a city row are its sub-districts (e.g. Pohang Nam-gu/Buk-gu): drop
        in_city = in_city and n.endswith("구") or (n.endswith("시") and n in by_name)
        if n in FIXED:
            out.append(FIXED[n][0])
            continue
        cands = by_name.get(n)
        if cands is None or (in_city and n.endswith("구")):
            out.append(None)  # sub-district or Sejong: dropped
            continue
        k = seen.get(n, 0)
        seen[n] = k + 1
        out.append(cands[k])
    # check: an ambiguous name sits next to an unambiguous row of the same province
    # check: KOSIS lists cities/gu, then counties (gun), each block in province-code order,
    # so the assigned province rank may step back exactly once
    rank = {s: r for r, s in enumerate(dict.fromkeys(s for s, _ in targets))}
    ranks = [rank[o] for o in out if o]
    assert sum(b < a for a, b in zip(ranks, ranks[1:])) == 1, "province order"
    assert sum(o is not None for o in out) == len(set(targets)) + 1, "row count"  # +1: Incheon Nam-gu appears twice (renamed)
    return out


def main(kosis_csv, pop_dir, rnrd_dir):
    k = pd.read_csv(kosis_csv, encoding="cp949", dtype=str)
    k = k.loc[:, ~k.columns.str.startswith("Unnamed")]
    years = {int(c.split()[0]): c for c in k.columns if c.endswith(" 년")}
    targets = target_names(pop_dir)

    k = k[k["연령(5세)별"].isin(AGE10)].copy()
    first_age = k["연령(5세)별"].iloc[0]
    sido = assign_sido(k.loc[k["연령(5세)별"] == first_age, "시군구별"].tolist(), targets)
    block = len(sido)
    assert len(k) == block * k["연령(5세)별"].nunique()
    k["sido"] = sido * k["연령(5세)별"].nunique()  # same region order in every age block
    k["ko"] = k["시군구별"].map(lambda n: RENAMED.get(n, n))
    k["age"] = k["연령(5세)별"].map(AGE10)
    k = k[k["sido"].notna()]
    for c in years.values():
        k[c] = pd.to_numeric(k[c])

    OUT.mkdir(parents=True, exist_ok=True)
    for year, col in years.items():
        counts = k.groupby(["sido", "ko", "age"])[col].sum(min_count=1).unstack("age")[list(config.AGE_GROUPS)]
        d = data.load_district(year)
        names = korean_names(rnrd_dir, year if year != 2019 else 2018)
        keys = [(s, names[(s, g)]) for s, g in zip(d["sido"], d["sigungu"])]
        c = counts.loc[keys].reset_index(drop=True)
        assert c.notna().all().all(), year
        total = c.sum(axis=1)
        out = pd.DataFrame({"do/si": d["sido"], "si/gun/gu": d["sigungu"], "Deaths": total.astype(int)})
        for a in config.AGE_GROUPS:
            out[f"q{a}"] = c[a] / total
        out.to_csv(OUT / f"sigungu_deaths_age_{year}.csv", index=False)
        print(year, len(out), int(total.sum()))


if __name__ == "__main__":
    main(*sys.argv[1:4])
