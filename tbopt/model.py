"""Fatality model.

Expected (weighted) fatalities for a hospital configuration h:

    E(h) = sum_s sum_t w_t N_{s,t} exp(-(h_s / A_s) / eta_tilde_{s,t})

* no-age model: a single group per district, N_s and eta_tilde_s from totals.
* age model: t = 1..5 (40-49, ..., 80+), weights w_t = a t + b(a), with b(a)
  chosen so that E(current h) equals the observed 40+ fatalities.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import config


@dataclass(frozen=True)
class Objective:
    """E(h) = sum_s sum_t coef[s, t] * exp(-h_s * k[s, t])."""

    coef: np.ndarray  # (S, T)  w_t * N_{s,t}
    k: np.ndarray     # (S, T)  1 / (A_s * eta_tilde_{s,t})

    def district(self, h: np.ndarray) -> np.ndarray:
        """Per-district contribution E_s(h_s), shape (S,)."""
        return (self.coef * np.exp(-np.asarray(h, float)[:, None] * self.k)).sum(axis=1)

    def single(self, s: int, h_s: float) -> float:
        """E_s for one district at hospital count h_s."""
        return float(self.coef[s] @ np.exp(-h_s * self.k[s]))

    def __call__(self, h: np.ndarray) -> float:
        return float(self.district(h).sum())


def _age_arrays(df: pd.DataFrame, ages=config.AGE_GROUPS_40):
    N_t = df[[f"N_{a}" for a in ages]].to_numpy(float)
    eta_tilde_t = df[[f"eta_tilde_{a}" for a in ages]].to_numpy(float)
    A = df["A"].to_numpy(float)[:, None]
    return N_t, 1.0 / (A * eta_tilde_t)


def no_age_objective(df: pd.DataFrame) -> Objective:
    """Age-free model using district totals N and D."""
    N = df["N"].to_numpy(float)[:, None]
    k = 1.0 / (df["A"].to_numpy(float) * df["eta_tilde"].to_numpy(float))[:, None]
    return Objective(coef=N, k=k)


def b_normalized(df: pd.DataFrame, a: float, t=config.AGE_INDEX) -> float:
    """b(a) such that the weighted E at the current configuration equals sum D_t."""
    N_t, k = _age_arrays(df)
    Nphi = N_t * np.exp(-df["h"].to_numpy(float)[:, None] * k)  # = D_t
    E0 = Nphi.sum()
    return float((E0 - a * (t * Nphi).sum()) / E0)


def age_weights(df: pd.DataFrame, a: float, t=config.AGE_INDEX) -> np.ndarray:
    return a * np.asarray(t, float) + b_normalized(df, a, t)


def age_objective(df: pd.DataFrame, a: float = 0.0, t=config.AGE_INDEX) -> Objective:
    """Age-weighted model with w_t = a t + b(a)."""
    N_t, k = _age_arrays(df)
    return Objective(coef=age_weights(df, a, t)[None, :] * N_t, k=k)
