# Auxiliary tables

| File | Content | Source |
|---|---|---|
| `sido_population_age_2022.csv` | Resident population by province and 10-year age group, 2022 | Statistics Korea (KOSIS) |
| `sigungu_average_age_2022.csv` | Average age of residents by district, 2022 | Statistics Korea (KOSIS) |
| `sido_code.csv` | Province administrative codes | Statistics Korea |
| `sigungu_population/sigungu_population_age_{2014..2022}.csv` | Resident population by district and 10-year age group, in the Dryad layout (`do/si`, `si/gun/gu`, `Population`, `g0_9`…`g80_` fractions; same rows as `sigungu_nd_age_{year}.csv`). Built by `scripts/build_population_tables.py`. 2022 district sums equal `sido_population_age_2022.csv` for every province. | Statistics Korea (KOSIS), resident registration population |
