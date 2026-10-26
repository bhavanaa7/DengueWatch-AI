"""Percentile-based risk categories and outbreak thresholds learned from training data only.

These are operational prototypes, not clinically validated outbreak definitions.
"""
import numpy as np


def compute_thresholds(train_cases, cfg):
    y = np.asarray(train_cases, dtype=float)
    y = y[~np.isnan(y)]
    if y.size == 0:
        raise ValueError("No training cases available to compute thresholds")
    r = cfg["risk"]
    return {
        "medium": float(np.percentile(y, r["medium_percentile"])),
        "high": float(np.percentile(y, r["high_percentile"])),
        "outbreak": float(np.percentile(y, r["outbreak_percentile"])),
        "n_train_weeks": int(y.size),
    }


def classify(value, thresholds):
    """Low < medium <= Medium < high <= High."""
    if value >= thresholds["high"]:
        return "High"
    if value >= thresholds["medium"]:
        return "Medium"
    return "Low"


def classify_array(values, thresholds):
    return [classify(v, thresholds) for v in values]
