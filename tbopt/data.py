"""Loading, filtering and age reconstruction of the district-level TB data.

Notation follows the manuscript: for district s and age group t,
``N_t = n_t * N`` and ``D_t = d_t * D`` (province age fractions n_t, d_t applied
to district totals), ``phi_t = D_t / N_t``, ``eta = H / A`` and
``eta_tilde_t = eta / -log(phi_t)`` so that ``phi_t = exp(-eta / eta_tilde_t)``
holds for the current hospital configuration.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import config

_DRYAD_COLUMNS = {
    "do/si": "sido",
    "si/gun/gu": "sigungu",
    "Number of hospitals": "h",
    "Area": "A",
    "Number of new patients": "N",
    "Number of fatalities": "D",
}

PHI_MIN = 1e-10

# spelling variants in the Dryad files -> canonical province name
_SIDO_FIX = {"Gwangwon": "Gangwon"}


# ---------------------------------------------------------------------------
# raw data
# ---------------------------------------------------------------------------
def load_district(year: int, filtered: bool = False, data_dir: Path | None = None) -> pd.DataFrame:
    """District table of the Dryad dataset (``sigungu_nd_age[_filtered]_{year}.csv``).

    Columns: sido, sigungu, h, A, N, D, n{age}, d{age}.
    """
    data_dir = Path(data_dir or config.DATA_DIR)
    name = f"sigungu_nd_age_filtered_{year}.csv" if filtered else f"sigungu_nd_age_{year}.csv"
    df = pd.read_csv(data_dir / name, encoding="utf-8-sig")
    return df.rename(columns=_DRYAD_COLUMNS)


def _load_sido_table(name: str, data_dir: Path | None) -> pd.DataFrame:
    data_dir = Path(data_dir or config.DATA_DIR)
    df = pd.read_csv(data_dir / name, encoding="utf-8-sig").rename(columns={"do/si": "sido"})
    df.columns = [int(c) if str(c).isdigit() else c for c in df.columns]
    df["sido"] = df["sido"].replace(_SIDO_FIX)
    return df


def load_sido_patients(data_dir: Path | None = None) -> pd.DataFrame:
    """Province new TB cases by 5-year age group (rows) and year (columns)."""
    return _load_sido_table("sido_patients_age_2014_2022.csv", data_dir)


def load_sido_fatalities(data_dir: Path | None = None) -> pd.DataFrame:
    """Province TB deaths by 5-year age group (rows) and year (columns)."""
    return _load_sido_table("sido_fatalities_age_2014_2022.csv", data_dir)


def load_sido_hospitals(data_dir: Path | None = None) -> pd.DataFrame:
    """Number of TB hospitals per province (rows) and year (columns)."""
    return _load_sido_table("sido_hospital_2014_2022.csv", data_dir)


def load_sido_population_2022() -> pd.DataFrame:
    """General population of each province by 10-year age group (2022)."""
    df = pd.read_csv(config.AUX_DIR / "sido_population_age_2022.csv", encoding="utf-8-sig")
    df = df.rename(columns={"sigungu": "sido"}).set_index("sido")
    return df.apply(lambda c: pd.to_numeric(c.astype(str).str.replace(r"[ ,]", "", regex=True)))


def _to_10yr(age: str) -> str:
    lo = int(age.split("_")[0])
    return "80_" if lo >= 80 else f"{lo // 10 * 10}_{lo // 10 * 10 + 9}"


def sido_age_fractions_from_counts(year: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Province age fractions n_t, d_t computed from the province count tables.

    This is how the district files' n/d columns were built (10-year groups,
    normalized within each province). Provinces without deaths give NaN.
    """
    out = []
    for tab in (load_sido_patients(), load_sido_fatalities()):
        t = tab.assign(age10=tab["age"].map(_to_10yr)).groupby(["sido", "age10"], sort=False)[year].sum()
        t = t.unstack()[list(config.AGE_GROUPS)]
        out.append(t.div(t.sum(axis=1), axis=0))
    return out[0], out[1]


def sido_age_fractions(year: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Province age fractions (n_t, d_t) for all 9 age groups, as used in the reconstruction."""
    df = load_district(year).drop_duplicates("sido").set_index("sido")
    n = df[[f"n{a}" for a in config.AGE_GROUPS]].set_axis(config.AGE_GROUPS, axis=1)
    d = df[[f"d{a}" for a in config.AGE_GROUPS]].set_axis(config.AGE_GROUPS, axis=1)
    return n, d


# ---------------------------------------------------------------------------
# age reconstruction and filtering
# ---------------------------------------------------------------------------
def reconstruct_age(df: pd.DataFrame, ages=config.AGE_GROUPS_40) -> pd.DataFrame:
    """Add reconstructed ``N_t``, ``D_t`` and ``phi_t`` columns.

    Current method: province age fractions applied to district totals
    (manuscript Eq. 3).
    """
    out = df.copy()
    for age in ages:
        out[f"N_{age}"] = out["N"] * out[f"n{age}"]
        out[f"D_{age}"] = out["D"] * out[f"d{age}"]
        with np.errstate(divide="ignore", invalid="ignore"):
            out[f"phi_{age}"] = out[f"D_{age}"] / out[f"N_{age}"]
    return out


def filter_districts(df: pd.DataFrame, ages=config.AGE_GROUPS_40) -> pd.DataFrame:
    """Districts used in the analysis.

    Keeps districts with at least one hospital (h > 0), at least one TB death
    (D > 0), and a positive reconstructed fatality rate in every age group
    40+ (phi_t > 1e-10, i.e. D_t > 0 and N_t > 0).
    """
    df = reconstruct_age(df, ages) if f"phi_{ages[0]}" not in df else df
    mask = (df["h"] > 0) & (df["D"] > 0) & (df["d40_49"] > 0)
    for age in ages:
        mask &= df[f"phi_{age}"] > PHI_MIN
    return df[mask].reset_index(drop=True)


def add_eta_tilde(df: pd.DataFrame, ages=config.AGE_GROUPS_40) -> pd.DataFrame:
    """Add ``eta`` and the calibrated ``eta_tilde_t`` (and age-free ``eta_tilde``)."""
    out = df.copy()
    out["eta"] = out["h"] / out["A"]
    for age in ages:
        out[f"eta_tilde_{age}"] = out["eta"] / -np.log(out[f"phi_{age}"])
    out["eta_tilde"] = out["eta"] / np.abs(np.log(out["D"] / out["N"]))
    return out


def preprocess(year: int, data_dir: Path | None = None) -> pd.DataFrame:
    """Raw Dryad table -> filtered table with all model inputs."""
    df = load_district(year, data_dir=data_dir)
    return add_eta_tilde(filter_districts(reconstruct_age(df)))


# ---------------------------------------------------------------------------
# processed data on disk
# ---------------------------------------------------------------------------
def processed_path(year: int, result_dir: Path | None = None) -> Path:
    return Path(result_dir or config.RESULT_DIR) / "processed" / f"{year}.csv"


def save_processed(year: int, result_dir: Path | None = None, data_dir: Path | None = None) -> Path:
    path = processed_path(year, result_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    preprocess(year, data_dir=data_dir).to_csv(path, index=False)
    return path


def load_processed(year: int, result_dir: Path | None = None) -> pd.DataFrame:
    """Processed table; built from the raw data if it does not exist yet."""
    path = processed_path(year, result_dir)
    if not path.exists():
        save_processed(year, result_dir)
    return pd.read_csv(path)


def summary_table(years=config.YEARS) -> pd.DataFrame:
    """Manuscript Table 2: S, N, D (all ages), D_40 (40+), H per year."""
    rows = []
    for year in years:
        df = load_processed(year)
        rows.append({
            "year": year,
            "S": len(df),
            "N": int(df["N"].sum()),
            "D": int(df["D"].sum()),
            "D_40": float(sum(df[f"D_{a}"].sum() for a in config.AGE_GROUPS_40)),
            "H": int(df["h"].sum()),
        })
    return pd.DataFrame(rows).set_index("year")


def sido_summary_table(years=config.YEARS) -> pd.DataFrame:
    """Manuscript Table 1: national totals per year.

    N, D: Dryad province tables. H: sum over the Dryad district files (hospitals are
    recorded at district level; the province hospital table disagrees by +-1).
    """
    years = list(years)
    return pd.DataFrame({
        "N": load_sido_patients()[years].sum(),
        "D": load_sido_fatalities()[years].sum(),
        "H": pd.Series({y: int(load_district(y)["h"].sum()) for y in years}),
    }).rename_axis("year")


def table_to_latex(df: pd.DataFrame, float_fmt: str = "{:,.1f}") -> str:
    """Rows as LaTeX ``year & ... \\\\`` lines with thin-space thousands separators."""
    def fmt(v):
        if isinstance(v, (float, np.floating)) and not float(v).is_integer():
            return float_fmt.format(v).replace(",", " ")
        return f"{int(v):,}".replace(",", " ")
    return "\n".join(f"{y} & " + " & ".join(fmt(v) for v in row) + r" \\" for y, row in df.iterrows())


def load_district_population(year: int) -> pd.DataFrame:
    """District population in the Dryad layout: sido, sigungu, P (total), g{age} fractions.

    Same rows and names as ``load_district(year)``; Sejong (no districts) is absent as in Dryad.
    """
    df = pd.read_csv(config.AUX_DIR / "sigungu_population" / f"sigungu_population_age_{year}.csv")
    return df.rename(columns={"do/si": "sido", "si/gun/gu": "sigungu", "Population": "P"})


def load_district_deaths(year: int, filtered: bool = False) -> pd.DataFrame:
    """District all-cause deaths in the Dryad layout: sido, sigungu, Deaths, q{age} fractions (KOSIS)."""
    name = f"sigungu_deaths_age_filtered_{year}.csv" if filtered else f"sigungu_deaths_age_{year}.csv"
    df = pd.read_csv(config.AUX_DIR / "sigungu_deaths" / name)
    return df.rename(columns={"do/si": "sido", "si/gun/gu": "sigungu"})
