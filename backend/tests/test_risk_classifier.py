import numpy as np
from src.config import load_config
from src.risk_classifier import classify, compute_thresholds


def test_thresholds_from_training_values_only():
    cfg = load_config(); y = np.arange(1, 101)
    t = compute_thresholds(y, cfg)
    assert t["medium"] == np.percentile(y, 50) and t["high"] == np.percentile(y, 80)
    assert compute_thresholds(np.append(y, 10 ** 6), cfg)["high"] != t["high"]  # depends on supplied data only


def test_category_boundaries():
    t = {"medium": 10, "high": 20, "outbreak": 30}
    assert classify(9.99, t) == "Low" and classify(10, t) == "Medium"
    assert classify(19.99, t) == "Medium" and classify(20, t) == "High"
