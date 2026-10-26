import numpy as np
import pandas as pd
from src.evaluation import lead_time_metrics, outbreak_metrics, regression_metrics


def _rows(y_true, y_pred, h=2, thr=5.0):
    target = pd.date_range("2020-01-05", periods=len(y_true), freq="7D")
    return pd.DataFrame({"target_week": target, "origin_week": target - pd.Timedelta(weeks=h),
                         "y_true": y_true, "y_pred": y_pred, "outbreak_threshold": thr})


def test_lead_time_counts_only_timely_flags():
    y_true = [1, 1, 6, 7, 1, 1, 8, 1, 1, 1]
    y_pred = [0, 0, 6, 0, 0, 5.5, 0, 0, 0, 0]
    m = lead_time_metrics(_rows(y_true, y_pred))
    assert m["episodes"] == 2 and m["episodes_detected"] == 2
    assert np.isclose(m["mean_lead_weeks"], 2.5)  # episode 1: lead 2 wk; episode 2: flagged one week early, lead 3 wk


def test_lead_time_missed_episode_is_nan():
    m = lead_time_metrics(_rows([1, 6, 1], [0, 0, 0]))
    assert m["episodes"] == 1 and m["episodes_detected"] == 0 and np.isnan(m["mean_lead_weeks"])


def test_outbreak_and_regression_metrics():
    o = outbreak_metrics([1, 6, 7, 1], [1, 6, 1, 6], 5)
    assert (o["tp"], o["fp"], o["fn"], o["tn"]) == (1, 1, 1, 1)
    assert regression_metrics([1, 2, 3], [1, 2, 3])["mae"] == 0
