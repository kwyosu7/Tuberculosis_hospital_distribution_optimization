"""Shared plotting style and helpers for the manuscript figures."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from . import config

_BASE_COLORS = [
    (237, 74, 184), (158, 95, 253), (255, 206, 81), (119, 200, 236), (24, 218, 210),
    (111, 237, 155), (102, 0, 51), (0, 0, 0), (211, 196, 147), (186, 159, 72),
    (89, 80, 65), (231, 85, 0), (0, 138, 148), (223, 105, 98),
]
COLORS = ["#{:02x}{:02x}{:02x}".format(*c) for c in _BASE_COLORS] * 2
MARKERS = ["o", "v", "^", "<", ">", "8", "s", "p", "*", "h", "H", "D", "d", "P", "X"] * 2

# fixed colours used across figures
C_A0 = COLORS[5]      # a = 0
C_AMIN = COLORS[1]    # a = a_min
C_GRID = COLORS[10]   # other a values
AGE_COLORS = ["#8ec579", "#c6e2bc", "#ffffff", "#c0a5c8", "#804b90"]
T_LABELS = [f"$t={t}$" for t in config.AGE_INDEX]

LABEL_SIZE = 20
TICK_SIZE = 14


def style():
    plt.rcParams.update({
        "mathtext.fontset": "cm",
        "font.family": ["Helvetica", "Arial", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "xtick.labelsize": TICK_SIZE,
        "ytick.labelsize": TICK_SIZE,
        "axes.labelsize": LABEL_SIZE,
    })


def panel_label(ax, letter: str, pos=(-0.15, 1.1), size=20):
    ax.text(*pos, f"({letter})", fontsize=size, ha="center", va="center", transform=ax.transAxes)


def sido_styles(names):
    """Consistent (color, marker) per province, skipping the slot used by Sejong."""
    return {n: (COLORS[i], MARKERS[i]) for i, n in enumerate(names)}


def savefig(fig, name: str, fig_dir: Path | None = None, **kw):
    fig_dir = Path(fig_dir or config.FIG_DIR)
    fig_dir.mkdir(parents=True, exist_ok=True)
    path = fig_dir / name
    kw.setdefault("bbox_inches", "tight")
    kw.setdefault("dpi", 300)
    fig.savefig(path, **kw)
    return path
