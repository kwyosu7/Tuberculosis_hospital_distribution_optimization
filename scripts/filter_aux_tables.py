"""Write the analysed-district subsets of the auxiliary tables (as Dryad's *_filtered_{year}.csv).

Rows = districts kept by tbopt.data.filter_districts (same rows as sigungu_nd_age_filtered_{year}.csv).
python scripts/filter_aux_tables.py
"""
import pandas as pd

from tbopt import config, data

for name in ("sigungu_population", "sigungu_deaths"):
    stem = f"{name}_age"
    for year in config.YEARS:
        full = pd.read_csv(config.AUX_DIR / name / f"{stem}_{year}.csv")
        keep = data.preprocess(year)[["sido", "sigungu"]].rename(columns={"sido": "do/si", "sigungu": "si/gun/gu"})
        out = keep.merge(full, on=["do/si", "si/gun/gu"], how="left", validate="one_to_one")
        assert out.notna().all().all() and len(out) == len(keep), (name, year)
        out.to_csv(config.AUX_DIR / name / f"{stem}_filtered_{year}.csv", index=False)
        print(name, year, len(out))
