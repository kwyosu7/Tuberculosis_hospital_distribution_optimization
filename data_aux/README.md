# Auxiliary tables

| File | Content | Source |
|---|---|---|
| `sido_population_age_2022.csv` | Resident population by province and 10-year age group, 2022 | Statistics Korea (KOSIS) |
| `sigungu_average_age_2022.csv` | Average age of residents by district, 2022 | Statistics Korea (KOSIS) |
| `sido_code.csv` | Province administrative codes | Statistics Korea |
| `sigungu_population/sigungu_population_age_{2014..2022}.csv` | Resident population by district and 10-year age group, in the Dryad layout (`do/si`, `si/gun/gu`, `Population`, `g0_9`…`g80_` fractions; same rows as `sigungu_nd_age_{year}.csv`). Built by `scripts/build_population_tables.py`. 2022 district sums equal `sido_population_age_2022.csv` for every province. | Statistics Korea (KOSIS), resident registration population |
| `sigungu_deaths/sigungu_deaths_age_{2014..2022}.csv` | All-cause deaths by district and 10-year age group (both sexes, place of residence), Dryad layout (`do/si`, `si/gun/gu`, `Deaths`, `q0_9`…`q80_` fractions). Built by `scripts/build_death_tables.py` from KOSIS table 101_DT_1B80A18. Cities with sub-districts use the city total; Incheon Nam-gu = 남구(변동전) 2014–17 + 미추홀구 2018–22. National total + Sejong is 18–71 below the published annual totals (deaths with unknown district/age). | Statistics Korea (KOSIS), vital statistics — deaths |
| `*_filtered_{year}.csv` (both folders) | Same tables restricted to the analysed districts (rows of Dryad `sigungu_nd_age_filtered_{year}.csv`). Built by `scripts/filter_aux_tables.py`. | — |
