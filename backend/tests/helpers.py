import numpy as np
import pandas as pd
from src.config import load_config


def synthetic(n=120, seed=0):
    """Synthetic fixture for unit tests only; never presented as DengAI results."""
    rng = np.random.default_rng(seed)
    parts = []
    for city, off in (("sj", 0), ("iq", 1000)):
        d = pd.date_range("2000-01-02", periods=n, freq="7D")
        parts.append(pd.DataFrame({
            "city": city, "year": d.year, "weekofyear": d.isocalendar().week.astype(int).to_numpy(),
            "week_start_date": d, "precipitation_amt_mm": rng.gamma(2, 10, n) + off,
            "reanalysis_avg_temp_k": 298 + rng.normal(0, 1, n),
            "total_cases": np.arange(n) + off}))  # cases encode row index and city -> easy alignment checks
    return pd.concat(parts, ignore_index=True)


def small_cfg():
    cfg = load_config()
    cfg["features"]["climate_vars"] = ["precipitation_amt_mm", "reanalysis_avg_temp_k"]
    cfg["features"]["lags"] = [1, 2, 4]
    cfg["features"]["case_lags"] = [0, 1, 4, 52]
    return cfg
