# Age structure and optimal TB hospital allocation in South Korea (2014–2022)

Code for the manuscript

> Y. Kwon, D.-S. Lee, S.-W. Son, M. J. Lee,
> *Age structure alters optimal hospital allocation for reducing tuberculosis
> fatalities in South Korea* (arXiv:2602.16437).

> **Status:** the `revision-scirep` branch contains work in progress for the
> Scientific Reports revision. It will be merged into `main` and archived with a
> DOI on release.

------------------------------------------------------------------------

## Layout

```
tbopt/                 Python package (all computations)
  config.py            paths, age groups, a-grid, Monte Carlo defaults
  data.py              Dryad loaders, age reconstruction, filtering, eta_tilde, Table 2
  model.py             fatality model E(h) (no-age and age-weighted, w_t = a t + b(a))
  optimize.py          Monte Carlo optimization and result I/O
  analysis.py          derived quantities used in the figures
  plotting.py          figure style and helpers
scripts/run_pipeline.py  preprocessing + all optimizations (parallel)
notebooks/
  01_data_and_tables.ipynb   Tables 1–2 (+ LaTeX rows), filter steps, data checks
  02_figures.ipynb           manuscript figures
tests/                 consistency tests (incl. agreement with the original implementation)
data_aux/              small public auxiliary tables (population by age, province codes)
```

Generated files go to `results/` and `figures/` (not tracked).

------------------------------------------------------------------------

## Data

Download the dataset from Dryad (https://doi.org/10.5061/dryad.b2rbnzss4) and
place the CSV files in `data/` (or a symbolic link named `data`, or set
`TB_DATA_DIR`). Expected files:

- `sigungu_nd_age_{2014..2022}.csv` (district level; input of the pipeline)
- `sigungu_nd_age_filtered_{2014..2022}.csv` (used only for cross-checks)
- `sido_patients_age_2014_2022.csv`, `sido_fatalities_age_2014_2022.csv`,
  `sido_hospital_2014_2022.csv` (province level)

District boundary files for the map panels (Fig. 1b, Fig. 5a) go to
`data_aux/korea_map/` (to be added).

------------------------------------------------------------------------

## Usage

```bash
conda env create -f environment.yml
conda activate tbopt
python scripts/run_pipeline.py      # ~30 s: preprocessing + 9 years x 31 values of a
pytest                              # optional checks
jupyter lab notebooks/
```

`run_pipeline.py` options: `--steps preprocess,no_age,age`, `--years 2015,2022`,
`--a-index 20`, `--seed`, `--n-steps`, `--workers`.

### Model in brief

For district *s* and age group *t* (40–49, …, 80+), the expected fatalities for
hospital counts *h* are
`E(h) = Σ_s Σ_t w_t N_{s,t} exp(-(h_s/A_s)/η̃_{s,t})`, with η̃ calibrated so that
the current allocation reproduces the observed deaths, and weights
`w_t = a t + b(a)` normalized so that E(current) = observed 40+ deaths.
The Monte Carlo moves Δh = 0.01 hospitals between two random districts and
accepts the move if E decreases (10^5 steps per year).

------------------------------------------------------------------------

## Citation

Please cite the manuscript and the Dryad dataset
(doi:10.5061/dryad.b2rbnzss4). A code DOI (Zenodo) will be added upon release.

## License

Code is released under the MIT License (see `LICENSE`). The dataset on Dryad
has its own license.

## Contact

Please open a GitHub Issue for questions.
