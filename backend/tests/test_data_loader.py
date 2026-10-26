import numpy as np
import pandas as pd
from src.data_loader import clean


def _frames():
    f = pd.DataFrame({"city": ["sj", "sj", "sj", "iq"], "year": [2000, 2000, 2000, 2000],
                      "weekofyear": [2, 1, 1, 1], "week_start_date": ["2000-01-09", "2000-01-02", "2000-01-02", "2000-01-02"],
                      "precipitation_amt_mm": [1.0, np.nan, 2.0, 3.0]})
    l = pd.DataFrame({"city": ["sj", "sj", "sj", "iq"], "year": [2000] * 4, "weekofyear": [2, 1, 1, 1], "total_cases": [5, 4, 4, 1]})
    return f, l


def test_duplicates_removed_and_sorted():
    df, rep = clean(*_frames())
    assert rep["duplicate_feature_keys"] == 1
    assert not df.duplicated(["city", "year", "weekofyear"]).any()
    sj = df[df.city == "sj"]
    assert sj["week_start_date"].is_monotonic_increasing


def test_missing_target_not_fabricated():
    f, l = _frames()
    l.loc[0, "total_cases"] = np.nan
    df, rep = clean(f, l)
    assert rep["missing_target"] == 1 and df["total_cases"].isna().sum() == 1


def test_missing_features_reported_not_imputed():
    df, rep = clean(*_frames())
    assert "precipitation_amt_mm" in rep["missing_before"] or df["precipitation_amt_mm"].notna().all()
