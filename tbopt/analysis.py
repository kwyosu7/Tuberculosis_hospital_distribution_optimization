"""Quantities derived from the optimization results (used by the figures)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config, data, model, optimize

AGES = config.AGE_GROUPS_40


def rho(df: pd.DataFrame) -> pd.DataFrame:
    """Patient density rho_{s,t} = N_{s,t} / A_s (columns = age groups)."""
    return pd.DataFrame({a: df[f"N_{a}"] / df["A"] for a in AGES})


def rho_over_eta_tilde(df: pd.DataFrame) -> pd.DataFrame:
    """Rescaled patient density rho_{s,t} / eta_tilde_{s,t}."""
    return pd.DataFrame({a: df[f"N_{a}"] / df["A"] / df[f"eta_tilde_{a}"] for a in AGES})


def rho_over_eta_tilde_total(df: pd.DataFrame) -> pd.Series:
    """Age-free counterpart rho_s / eta_tilde_s."""
    return df["N"] / df["A"] / df["eta_tilde"]


def a_bounds(df: pd.DataFrame, grid=config.A_GRID) -> tuple[int, int]:
    """Indices (i_min, i_max) of the a-range where all weights w_t = a t + b(a) are >= 0.

    a_min: first a with w_5 >= 0;  a_max: last a with w_1 >= 0.
    """
    w = np.array([model.age_weights(df, a) for a in grid])
    i_min = int(np.argmax(w[:, -1] >= 0))
    i_max = int(np.nonzero(w[:, 0] >= 0)[0].max())
    return i_min, i_max


def E_by_age(df: pd.DataFrame, h, a: float) -> np.ndarray:
    """Weighted fatalities per district and age group, shape (S, 5)."""
    obj = model.age_objective(df, a)
    return obj.coef * np.exp(-np.asarray(h, float)[:, None] * obj.k)


def E_min_by_age(year: int) -> pd.DataFrame:
    """sum_s E_{s,t} at the optimum, for every a in the grid (rows) and age (cols)."""
    df = data.load_processed(year)
    rows = {}
    for i, a in enumerate(config.A_GRID):
        h = optimize.load_result("age", year, i)["h"]
        rows[float(a)] = E_by_age(df, h, a).sum(axis=0)
    return pd.DataFrame.from_dict(rows, orient="index", columns=AGES)


def hospital_change_age_vs_noage(year: int, a_index: int = config.A_ZERO_INDEX) -> pd.Series:
    """(eta_age^(opt) - eta_x^(opt)) / eta per district."""
    df = data.load_processed(year)
    h_age = optimize.load_result("age", year, a_index)["h"]
    h_no = optimize.load_result("no_age", year)["h"]
    return pd.Series((h_age - h_no) / df["h"].to_numpy(), index=df.index)


def reduction_summary(years=config.YEARS) -> pd.DataFrame:
    """Per year: D_40, E_min at a=0 and a=a_min, relative reductions."""
    rows = []
    for y in years:
        df = data.load_processed(y)
        D40 = sum(df[f"D_{a}"].sum() for a in AGES)
        i_min, i_max = a_bounds(df)
        E0 = float(optimize.load_result("age", y, config.A_ZERO_INDEX)["E_final"])
        Emin = float(optimize.load_result("age", y, i_min)["E_final"])
        rows.append(dict(year=y, D_40=D40, a_min=config.A_GRID[i_min], a_max=config.A_GRID[i_max],
                         E_a0=E0, E_amin=Emin,
                         reduction_a0=(D40 - E0) / D40, reduction_amin=(D40 - Emin) / D40))
    return pd.DataFrame(rows).set_index("year")
