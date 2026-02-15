# Tuberculosis Hospital Optimization (South Korea, 2014–2022)

This repository provides the code used for the age-sensitive
tuberculosis (TB) hospital distribution and optimization analysis in
South Korea.  
The purpose of this repository is to ensure computational
reproducibility of the study and to support reuse of the accompanying
high-resolution dataset.

------------------------------------------------------------------------

## Repository Structure

The recommended structure of this repository is as follows:

-   README.md  
-   notebooks/ (Jupyter notebooks for preprocessing, optimization, and
    visualization)  
-   src/ (optional reusable Python modules, if applicable)  
-   data/ (downloaded dataset files; not tracked by git)  
-   results/ or data_result/ (generated outputs; not tracked by git)

If your workflow generates outputs into `data_result/`, that is
acceptable. These directories should remain excluded from version
control.

------------------------------------------------------------------------

## Data Availability

The dataset used in this study is publicly available on Dryad.

**Public DOI (post-publication):**  


**Reviewer (private share link; pre-publication):**  


The Dryad dataset includes its own README file describing variables,
filtering procedures, and file formats in detail.

------------------------------------------------------------------------

## Data Download & Placement

1.  Download the dataset from Dryad using the DOI or reviewer link.  
2.  Extract the downloaded archive.  
3.  Place all extracted files into the `data` directory located at the
    root of this repository.

After extraction, the directory should contain files similar to:

**Province-level (Si/Do) summaries:** -
sido_fatalities_age_2014_2022.csv  
- sido_patients_age_2014_2022.csv  
- sido_hospital_2014_2022.csv

**District-level (Si/Gun/Gu) annual files:** - sigungu_nd_age_2014.csv
through sigungu_nd_age_2022.csv  
- sigungu_nd_age_filtered_2014.csv through
sigungu_nd_age_filtered_2022.csv

If you prefer to store the dataset in a different location, modify the
path variables inside the notebooks accordingly. It is recommended to
define a single `DATA_DIR` variable near the top of each notebook.


------------------------------------------------------------------------

## How to Run

1.  Create and activate your Python environment.  

2.  Ensure the Dryad dataset is correctly placed in the `data`
    directory.  

3.  Execute the notebooks in the following logical order:

    1)  Data preprocessing  
    2)  Optimization analysis  
    3)  Visualization and figure generation

Notebook filenames may differ. Please execute them according to the
analysis flow described above.

------------------------------------------------------------------------

## Outputs

Generated outputs such as intermediate tables, optimization results, and
figures are typically written to:

-   `results/`  
-   `data_result/`

These directories are intended for local outputs and should not be
tracked by git.

------------------------------------------------------------------------

## Notes on Reproducibility

-   This repository is designed to reproduce the analysis results given
    the Dryad dataset.  
-   Exact numerical reproduction may depend on the Python version and
    package versions used.  
-   If path-related errors occur, verify that:
    -   the dataset files are located in the `data` directory  
    -   path variables inside notebooks are correctly defined

------------------------------------------------------------------------

## Citation

If you use this dataset or code, please cite the Dryad dataset and the
associated manuscript.

**Dryad dataset DOI:**  
https://datadryad.org/dataset/doi:10.5061/dryad.b2rbnzss4

The manuscript citation can be added here after publication.

------------------------------------------------------------------------

## License

A license file (e.g., MIT License) should be added to clarify reuse
permissions.  
If no license is provided, standard copyright restrictions apply.

------------------------------------------------------------------------

## Contact

For questions or issues, please open a GitHub Issue in this repository.
