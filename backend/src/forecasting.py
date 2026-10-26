"""Operational forecasts using only data available at the chosen forecast origin."""
import pandas as pd

from .artifact_manager import load_json, load_model
from .data_loader import load_clean
from .feature_engineering import build_features
from .risk_classifier import classify


def feature_table(cfg):
    return build_features(load_clean(cfg), cfg)


def best_model_name(cfg, city, horizon):
    for rec in load_json(cfg, "best_models.json"):
        if rec["city"] == city and rec["horizon"] == horizon:
            return rec["model"]
    raise KeyError(f"No best model recorded for {city}, horizon {horizon}")


def _seasonal_ref(g, horizon):
    idx = len(g) - 1 + horizon - 52  # same week one year before the target week
    return float(g["total_cases"].iloc[idx]) if 0 <= idx < len(g) else float("nan")


def forecast(cfg, feats, city, horizon, model_name=None, origin=None):
    """Forecast for `horizon` weeks after `origin` (default: latest observed week of the city)."""
    model_name = model_name or best_model_name(cfg, city, horizon)
    bundle = load_model(cfg, city, horizon, model_name)
    g = feats[feats["city"] == city].sort_values("week_start_date").reset_index(drop=True)
    if g.empty:
        raise ValueError(f"Unknown city '{city}'")
    if origin is not None:
        g = g[g["week_start_date"] <= pd.Timestamp(origin)].reset_index(drop=True)
        if g.empty:
            raise ValueError("Origin is before the first observation")
    row = g.iloc[[-1]].copy()
    row["seasonal_ref"] = _seasonal_ref(g, horizon)
    pred = float(max(bundle["model"].predict(row)[0], 0.0))
    lo_q, hi_q = bundle["resid_quantiles"]
    thr = bundle["thresholds"]
    origin_week = row["week_start_date"].iloc[0]
    return {
        "city": city, "horizon": horizon, "model": model_name,
        "origin_week": origin_week.date().isoformat(),
        "target_week": (origin_week + pd.Timedelta(weeks=horizon)).date().isoformat(),
        "predicted_cases": round(pred, 2),
        "lower": round(max(pred + lo_q, 0.0), 2), "upper": round(pred + hi_q, 2),
        "risk": classify(pred, thr), "thresholds": thr,
        "interval_note": "Walk-forward residual interval; empirical holdout coverage can be below nominal.",
    }
