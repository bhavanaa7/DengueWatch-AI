import pandas as pd
import pytest
from src.config import load_config
from src.artifact_manager import load_model


def test_missing_artifact_raises_helpful_error(tmp_path):
    cfg = load_config(); cfg["paths"]["artifacts_dir"] = tmp_path
    with pytest.raises(FileNotFoundError, match="train_models"):
        load_model(cfg, "sj", 4, "random_forest")


def test_rank_locations_orders_by_score():
    from src.prioritization import rank_locations
    th = {"medium": 10, "high": 20, "outbreak": 40}
    f = lambda c, p, r: {"city": c, "horizon": 4, "predicted_cases": p, "risk": r, "target_week": "2010-01-01", "model": "m", "thresholds": th}
    out = rank_locations([f("a", 5, "Low"), f("b", 30, "High")])
    assert out[0]["city"] == "b" and out[0]["rank"] == 1
