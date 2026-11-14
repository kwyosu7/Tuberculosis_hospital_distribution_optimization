"""Monte Carlo optimization of the hospital configuration.

At each step a random ordered pair of districts (i, j) is drawn and dh hospitals
are moved from j to i (if h_j >= dh). The move is accepted only if E decreases.
Only the two affected district terms are recomputed.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from . import config, data, model


@dataclass
class MCResult:
    h: np.ndarray        # optimized hospital counts, shape (S,)
    E_trace: np.ndarray  # E before each step, shape (n_steps,)
    E_final: float       # E(h), recomputed from scratch
    n_accepted: int


def monte_carlo(objective: model.Objective, h0, n_steps: int = config.MC_STEPS,
                dh: float = config.MC_DH, seed=None) -> MCResult:
    rng = np.random.default_rng(seed)
    h = np.asarray(h0, float).copy()
    S = len(h)
    gain = rng.integers(S, size=n_steps)
    lose = rng.integers(S - 1, size=n_steps)
    lose += lose >= gain  # distinct pair

    f = objective.district(h)
    E = f.sum()
    trace = np.empty(n_steps)
    accepted = 0
    for step in range(n_steps):
        trace[step] = E
        i, j = gain[step], lose[step]
        if h[j] - dh < 0:
            continue
        fi = objective.single(i, h[i] + dh)
        fj = objective.single(j, h[j] - dh)
        delta = (fi + fj) - (f[i] + f[j])
        if delta < 0:
            h[i] += dh
            h[j] -= dh
            f[i], f[j] = fi, fj
            E += delta
            accepted += 1
    return MCResult(h=h, E_trace=trace, E_final=objective(h), n_accepted=accepted)


# ---------------------------------------------------------------------------
# runs on disk
# ---------------------------------------------------------------------------
def _seed(base: int, *keys: int) -> np.random.SeedSequence:
    return np.random.SeedSequence([base, *keys])


def result_path(kind: str, year: int, a_index: int | None = None, result_dir: Path | None = None) -> Path:
    root = Path(result_dir or config.RESULT_DIR) / "optimization" / kind
    name = f"{year}.npz" if a_index is None else f"{year}_a{a_index:02d}.npz"
    return root / name


def run_no_age(year: int, seed: int = 0, **kw) -> Path:
    df = data.load_processed(year)
    res = monte_carlo(model.no_age_objective(df), df["h"], seed=_seed(seed, year), **kw)
    path = result_path("no_age", year)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, h=res.h, E_trace=res.E_trace, E_final=res.E_final,
                        n_accepted=res.n_accepted, sigungu=(df["sido"] + "/" + df["sigungu"]).to_numpy(dtype=str))
    return path


def run_age(year: int, a_index: int, seed: int = 0, **kw) -> Path:
    df = data.load_processed(year)
    a = float(config.A_GRID[a_index])
    obj = model.age_objective(df, a)
    res = monte_carlo(obj, df["h"], seed=_seed(seed, year, a_index), **kw)
    path = result_path("age", year, a_index)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, h=res.h, E_trace=res.E_trace, E_final=res.E_final,
                        n_accepted=res.n_accepted, a=a, b=model.b_normalized(df, a),
                        sigungu=(df["sido"] + "/" + df["sigungu"]).to_numpy(dtype=str))
    return path


def load_result(kind: str, year: int, a_index: int | None = None) -> dict:
    with np.load(result_path(kind, year, a_index), allow_pickle=True) as z:
        return {k: z[k] for k in z.files}


def load_h_opt(kind: str, year: int, a_index: int | None = None) -> pd.Series:
    r = load_result(kind, year, a_index)
    return pd.Series(r["h"], name="h_opt")


def E_min_curve(year: int, a_indices=range(len(config.A_GRID))) -> pd.Series:
    """Minimum fatalities E_min(a) for one year."""
    vals = {float(config.A_GRID[i]): float(load_result("age", year, i)["E_final"]) for i in a_indices}
    return pd.Series(vals, name=year)
