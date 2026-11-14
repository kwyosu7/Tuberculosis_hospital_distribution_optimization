"""Paths and global constants.

Directories can be overridden with environment variables:
``TB_DATA_DIR`` (Dryad dataset), ``TB_RESULT_DIR`` (generated results),
``TB_FIG_DIR`` (figures).
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = Path(os.environ.get("TB_DATA_DIR", ROOT / "data"))
RESULT_DIR = Path(os.environ.get("TB_RESULT_DIR", ROOT / "results"))
FIG_DIR = Path(os.environ.get("TB_FIG_DIR", ROOT / "figures"))
AUX_DIR = ROOT / "data_aux"  # small public auxiliary tables shipped with the code
MAP_DIR = Path(os.environ.get("TB_MAP_DIR", ROOT / "data_aux" / "korea_map"))

YEARS = tuple(range(2014, 2023))

# 10-year age groups used in the source data
AGE_GROUPS = ("0_9", "10_19", "20_29", "30_39", "40_49", "50_59", "60_69", "70_79", "80_")
# age groups used in the model (t = 1, ..., 5)
AGE_GROUPS_40 = ("40_49", "50_59", "60_69", "70_79", "80_")
AGE_LABELS_40 = ("40-49", "50-59", "60-69", "70-79", "≥80")
AGE_INDEX = np.arange(1, len(AGE_GROUPS_40) + 1)  # t

# Monte Carlo defaults (as in the manuscript)
MC_STEPS = 100_000
MC_DH = 0.01

# age-weight slope grid: w_t = a t + b(a);  a = 0 is index 20
A_GRID = np.linspace(-2, 1, 31)
A_ZERO_INDEX = int(np.argmin(np.abs(A_GRID)))
