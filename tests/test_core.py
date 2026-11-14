"""Consistency checks of tbopt against the original (manuscript) implementation."""
import numpy as np
import pandas as pd
import pytest

from tbopt import config, data, model, optimize

YEARS = [2015, 2022]
AGES = config.AGE_GROUPS_40


# --- original implementation (at_b_tau12345/at_b_optimization.py, no_age/optimization.py)
def legacy_E_age(d, h, a, b):
    eta = h / d["A"]
    E = 0
    for i, age in enumerate(AGES):
        phi_t = np.exp(-eta / d["eta_tilde_" + age])
        E += sum((a * (i + 1) + b) * d["N_" + age] * phi_t)
    return E


def legacy_b(d, a):
    eta = d["h"] / d["A"]
    E0 = atNp = 0
    for i, age in enumerate(AGES):
        E0 += d["D_" + age].sum()
        atNp += sum(a * (i + 1) * d["N_" + age] * np.exp(-eta / d["eta_tilde_" + age]))
    return (E0 - atNp) / E0


def legacy_mc(E_fn, h0, pairs, dh=0.01):
    h = pd.Series(h0, dtype=float).reset_index(drop=True)
    Ei = E_fn(h)
    for i, j in pairs:
        if h[j] - dh < 0:
            continue
        h[i] += dh
        h[j] -= dh
        Ef = E_fn(h)
        if Ei <= Ef:
            h[i] -= dh
            h[j] += dh
        else:
            Ei = Ef
    return h.to_numpy(), Ei


@pytest.fixture(scope="module", params=YEARS)
def year(request):
    return request.param


@pytest.fixture(scope="module")
def df(year):
    return data.preprocess(year)


def test_filter_matches_dryad_filtered(df, year):
    f = data.load_district(year, filtered=True)
    assert len(df) == len(f)
    for col in ["N", "D", "h"]:
        assert df[col].sum() == f[col].sum()


@pytest.mark.parametrize("a", [-2.0, -0.5, 0.0, 1.0])
def test_current_configuration_reproduces_observed_deaths(df, a):
    D40 = sum(df[f"D_{t}"].sum() for t in AGES)
    assert model.age_objective(df, a)(df["h"]) == pytest.approx(D40, rel=1e-12)
    assert model.no_age_objective(df)(df["h"]) == pytest.approx(df["D"].sum(), rel=1e-12)
    assert model.b_normalized(df, a) == pytest.approx(legacy_b(df, a), rel=1e-12)


@pytest.mark.parametrize("a", [-1.3, 0.0, 0.7])
def test_objective_matches_legacy(df, a):
    rng = np.random.default_rng(1)
    h = df["h"].to_numpy(float) * rng.uniform(0.5, 1.5, len(df))
    b = legacy_b(df, a)
    assert model.age_objective(df, a)(h) == pytest.approx(legacy_E_age(df, h, a, b), rel=1e-12)


@pytest.mark.parametrize("a", [-1.3, 0.0])
def test_monte_carlo_matches_legacy(df, a):
    n = 3000
    seed = 7
    res = optimize.monte_carlo(model.age_objective(df, a), df["h"], n_steps=n, seed=seed)

    rng = np.random.default_rng(seed)  # same pair sequence as monte_carlo
    S = len(df)
    gain = rng.integers(S, size=n)
    lose = rng.integers(S - 1, size=n)
    lose += lose >= gain
    b = legacy_b(df, a)
    h_leg, E_leg = legacy_mc(lambda h: legacy_E_age(df, h, a, b), df["h"], zip(gain, lose))

    np.testing.assert_allclose(res.h, h_leg, atol=1e-9)
    assert res.E_final == pytest.approx(E_leg, rel=1e-10)
    assert res.E_final < res.E_trace[0]
    assert res.h.sum() == pytest.approx(df["h"].sum())
