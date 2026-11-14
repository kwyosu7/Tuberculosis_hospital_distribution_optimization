"""Run the full pipeline: preprocessing -> no-age optimization -> age-weighted optimization.

Examples
--------
python scripts/run_pipeline.py                      # everything (9 years x 31 a values)
python scripts/run_pipeline.py --steps age --years 2022 --a-index 20
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor

from tbopt import config, data, optimize


def _parse_range(text: str, default):
    if text is None:
        return list(default)
    out = []
    for part in text.split(","):
        lo, _, hi = part.partition("-")
        out += list(range(int(lo), int(hi or lo) + 1))
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--steps", default="preprocess,no_age,age")
    p.add_argument("--years", help="e.g. 2014-2022 or 2015,2022")
    p.add_argument("--a-index", help=f"indices into A_GRID (0-{len(config.A_GRID) - 1}); default all")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-steps", type=int, default=config.MC_STEPS)
    p.add_argument("--workers", type=int, default=None)
    args = p.parse_args()

    steps = args.steps.split(",")
    years = _parse_range(args.years, config.YEARS)
    a_idx = _parse_range(args.a_index, range(len(config.A_GRID)))
    kw = dict(seed=args.seed, n_steps=args.n_steps)

    if "preprocess" in steps:
        for y in years:
            print("preprocess", data.save_processed(y))

    with ProcessPoolExecutor(args.workers) as ex:
        jobs = []
        if "no_age" in steps:
            jobs += [ex.submit(optimize.run_no_age, y, **kw) for y in years]
        if "age" in steps:
            jobs += [ex.submit(optimize.run_age, y, i, **kw) for y in years for i in a_idx]
        for n, job in enumerate(jobs, 1):
            print(f"[{n}/{len(jobs)}]", job.result())


if __name__ == "__main__":
    main()
