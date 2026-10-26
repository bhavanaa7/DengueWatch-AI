"""Leakage-safe feature engineering.

Forecast origin t: row t holds only data observed up to week t (climate at t, cases at t).
Target for horizon h = total_cases at row t+h within the same city (shift(-h) per city).
Lags use shift(+k) per city; rolling stats use values up to and including t only.
Missing climate values are forward-filled within city (past-only) before lagging; leading NaNs
stay NaN and are imputed with train-fold medians inside the model pipeline.
"""
import numpy as np
import pandas as pd


def available_climate_vars(df, cfg):
    return [c for c in cfg["features"]["climate_vars"] if c in df.columns]


def build_features(df, cfg):
    fcfg = cfg["features"]
    cols = available_climate_vars(df, cfg)
    out = []
    for city, g in df.sort_values(["city", "week_start_date"]).groupby("city", sort=False):
        g = g.reset_index(drop=True)
        base = g[["city", "year", "weekofyear", "week_start_date", "total_cases"]].copy()
        feat = {}
        woy = g["weekofyear"].clip(upper=52)
        feat["sin_week"] = np.sin(2 * np.pi * woy / 52)
        feat["cos_week"] = np.cos(2 * np.pi * woy / 52)
        feat["year_feat"] = g["year"]
        clim = g[cols].ffill()  # past-only fill
        for c in cols:
            feat[f"{c}_lag0"] = clim[c]
            for k in fcfg["lags"]:
                feat[f"{c}_lag{k}"] = clim[c].shift(k)
            for w in fcfg["rolling_windows"]:
                roll = clim[c].rolling(w, min_periods=max(2, w // 2))
                feat[f"{c}_rmean{w}"] = roll.mean()
                if c in ("precipitation_amt_mm", "station_precip_mm"):
                    feat[f"{c}_rsum{w}"] = roll.sum()
                if w in (4, 8):
                    feat[f"{c}_rstd{w}"] = roll.std()
        cases = g["total_cases"]
        for k in fcfg["case_lags"]:
            feat[f"cases_lag{k}"] = cases.shift(k)
        for w in fcfg["rolling_windows"]:
            feat[f"cases_rmean{w}"] = cases.rolling(w, min_periods=2).mean()
        feat["cases_rstd4"] = cases.rolling(4, min_periods=2).std()
        out.append(pd.concat([base, pd.DataFrame(feat)], axis=1))
    return pd.concat(out, ignore_index=True)


def add_target(feats, horizon):
    """target_week and y = cases at t+h, shifted within city only."""
    f = feats.copy()
    g = f.groupby("city", sort=False)
    f["y"] = g["total_cases"].shift(-horizon)
    f["target_week_start"] = g["week_start_date"].shift(-horizon)
    f["horizon"] = horizon
    # Seasonal-naive reference: cases one year before the target week (index t+h-52), known at origin t when h<52.
    f["seasonal_ref"] = g["total_cases"].shift(52 - horizon)
    return f


def feature_columns(feats):
    meta = {"city", "year", "weekofyear", "week_start_date", "total_cases", "y", "target_week_start", "horizon", "seasonal_ref"}
    return [c for c in feats.columns if c not in meta]
