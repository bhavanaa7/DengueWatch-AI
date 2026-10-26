"""Chronological per-city splits with a horizon-sized gap.

Origin index i (0-based within a city) has target at i+h. A training row is usable at a validation
block starting at origin index s only if its target is already observed: i + h < s, i.e. i <= s-h-1.
This gap prevents label overlap between training targets and validation origins.
"""
import numpy as np


def holdout_start(n_weeks, cfg):
    return int(n_weeks * (1 - cfg["validation"]["holdout_fraction"]))


def walk_forward_folds(n_weeks, horizon, cfg):
    """Expanding-window folds inside the development period [0, holdout_start)."""
    v = cfg["validation"]
    dev_end = holdout_start(n_weeks, cfg)
    first = v["min_train_weeks"] + horizon
    if dev_end <= first:
        raise ValueError("Not enough development data for walk-forward validation")
    edges = np.linspace(first, dev_end, v["n_folds"] + 1).astype(int)
    folds = []
    for k in range(v["n_folds"]):
        s, e = int(edges[k]), int(edges[k + 1])
        folds.append({"fold": k + 1, "train_end": s - horizon - 1, "val_start": s, "val_end": e - 1})
    return folds


def holdout_split(n_weeks, horizon, cfg):
    s = holdout_start(n_weeks, cfg)
    return {"fold": "holdout", "train_end": s - horizon - 1, "val_start": s, "val_end": n_weeks - 1 - horizon}
