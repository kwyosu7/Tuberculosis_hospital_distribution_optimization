# Age structure and optimal TB hospital allocation in South Korea (2014–2022)

Code for the manuscript

> Y. Kwon, D.-S. Lee, S.-W. Son, M. J. Lee,
> *Age structure alters optimal hospital allocation for reducing tuberculosis
> fatalities in South Korea* (arXiv:2602.16437).

The repository reproduces the data preprocessing, the hospital-allocation
optimization (with and without age weighting), and the manuscript figures.

> **Status:** the `revision-scirep` branch contains work in progress for the
> Scientific Reports revision. Paths and some scripts will change on this branch
> until it is merged into `main` and archived with a DOI.

------------------------------------------------------------------------

## Repository structure

| Path | Description |
|---|---|
| `data_preproccess/preproccess_filtering_40over.py` | Filters districts and computes the age-specific parameters (η̃) used by the model. Output: `data_result/data_over40/{year}_40.txt` |
| `data_preproccess/rate_generate.ipynb` | Builds age-specific patient/fatality ratios from province-level data |
| `no_age/optimization.py` | Optimization without age weighting |
| `at_b_tau12345/at_b_optimization.py` | **Age-weighted optimization used in the manuscript** (age groups t = 1..5 for 40–49, …, 80+; weight a·t + b, a ∈ [−2, 1]) |
| `at_b/` | Earlier version of the age-weighted model (kept for reference) |
| `article_figure*.ipynb` | Manuscript figures |
| `check_basic_properties.ipynb`, `check_z.py`, `*/result_check.ipynb` | Auxiliary checks |
| `*.sh` | Batch scripts used to run the optimizations on a cluster |

Generated files (`data_result/`) are not tracked; regenerate them with the
scripts above.

------------------------------------------------------------------------

## Data

The input dataset is publicly available on Dryad:
https://doi.org/10.5061/dryad.b2rbnzss4

It contains

- province-level (si/do) files: `sido_patients_age_2014_2022.csv`,
  `sido_fatalities_age_2014_2022.csv`, `sido_hospital_2014_2022.csv`
- district-level (si/gun/gu) files: `sigungu_nd_age_{2014..2022}.csv` and the
  filtered versions `sigungu_nd_age_filtered_{2014..2022}.csv`

See the Dryad README for variable definitions and filtering procedures.

------------------------------------------------------------------------

## Requirements

Python 3 with `numpy`, `pandas`, `matplotlib` (and Jupyter for the notebooks).

------------------------------------------------------------------------

## How to run

1. Download the Dryad dataset and set the data path in the scripts.
2. Preprocess: `python data_preproccess/preproccess_filtering_40over.py`
3. Optimize:
   - without age weighting: `no_age/optimization.py`
   - age-weighted: `at_b_tau12345/at_b_optimization.py`
   (Monte Carlo, 10^5 steps per year; see the `.sh` files for the arguments used.)
4. Run the `article_figure*.ipynb` notebooks to produce the figures.

> Note: some scripts still contain absolute paths from the original computing
> environment. These are being replaced with configurable paths in the revision.

------------------------------------------------------------------------

## Citation

Please cite the manuscript and the Dryad dataset
(doi:10.5061/dryad.b2rbnzss4). A code DOI (Zenodo) will be added upon release.

## License

Code is released under the MIT License (see `LICENSE`). The dataset on Dryad
has its own license.

## Contact

Please open a GitHub Issue for questions.
