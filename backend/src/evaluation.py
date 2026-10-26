"""Forecast and outbreak-detection metrics (no MAPE)."""
import numpy as np


def regression_metrics(y, p, scale=None):
    y, p = np.asarray(y, float), np.asarray(p, float)
    err = y - p
    mae = float(np.mean(np.abs(err)))
    out = {"mae": mae, "rmse": float(np.sqrt(np.mean(err ** 2)))}
    ss_tot = np.sum((y - y.mean()) ** 2)
    out["r2"] = float(1 - np.sum(err ** 2) / ss_tot) if ss_tot > 0 and len(y) > 2 else None
    out["mase"] = float(mae / scale) if scale and scale > 0 else None
    return out


def outbreak_metrics(y, p, threshold):
    ya, pa = np.asarray(y) >= threshold, np.asarray(p) >= threshold
    tp, fp = int(np.sum(ya & pa)), int(np.sum(~ya & pa))
    fn, tn = int(np.sum(ya & ~pa)), int(np.sum(~ya & ~pa))
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    f1 = 2 * prec * rec / (prec + rec) if prec and rec else (0.0 if tp + fp + fn else None)
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": prec, "recall": rec, "f1": f1,
            "specificity": tn / (tn + fp) if tn + fp else None,
            "false_alarm_rate": fp / (fp + tn) if fp + tn else None, "missed_outbreak_weeks": fn,
            "outbreak_weeks": int(ya.sum())}


def mase_scale(train_y_series, horizon):
    """MAE of a persistence forecast at this horizon on training data (scaling denominator)."""
    y = np.asarray(train_y_series, float)
    if len(y) <= horizon:
        return None
    return float(np.nanmean(np.abs(y[horizon:] - y[:-horizon])))


def lead_time_metrics(rows, lookback_weeks=4):
    """Outbreak warning lead time for one evaluation block (fold or holdout).

    Episode = run of consecutive target weeks with actual cases >= the frozen threshold. An episode is
    'warned' if some forecast flagged (pred >= threshold) a target week in [start-lookback, end]
    (not overlapping the previous episode) and was ISSUED at or before the episode start week.
    Lead time = weeks between the earliest such issue date and the episode's first target week.
    Late flags (issued after the episode began) do not count as timely warnings.
    """
    import pandas as pd
    r = rows.sort_values("target_week").reset_index(drop=True)
    thr = r["outbreak_threshold"].to_numpy()
    actual, flagged = r["y_true"].to_numpy() >= thr, r["y_pred"].to_numpy() >= thr
    tw, ow = pd.to_datetime(r["target_week"]), pd.to_datetime(r["origin_week"])
    episodes, i = [], 0
    while i < len(r):
        if actual[i]:
            j = i
            while j + 1 < len(r) and actual[j + 1]:
                j += 1
            episodes.append((i, j))
            i = j + 1
        else:
            i += 1
    leads, prev_end = [], -1
    for s, e in episodes:
        lo = max(prev_end + 1, s - lookback_weeks)
        idx = [k for k in range(lo, e + 1) if flagged[k] and ow.iloc[k] <= tw.iloc[s]]
        if idx:
            first = min(idx, key=lambda k: ow.iloc[k])
            leads.append((tw.iloc[s] - ow.iloc[first]).days / 7)
        prev_end = e
    return {"episodes": len(episodes), "episodes_detected": len(leads),
            "mean_lead_weeks": float(np.mean(leads)) if leads else float("nan")}
