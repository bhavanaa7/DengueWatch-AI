"""Exploratory cross-correlation between past climate and later dengue cases.

Uses ONLY the development period (before the final holdout). Limitations: Spearman correlation
captures monotonic association only, ignores autocorrelation in both series and says nothing
about causation. It is exploratory and is not used to select model features.
"""
import pandas as pd

from .feature_engineering import available_climate_vars
from .validation import holdout_start


def lag_correlations(df, cfg, max_lag=12):
    rows = []
    for city, g in df.sort_values(["city", "week_start_date"]).groupby("city"):
        g = g.reset_index(drop=True)
        dev = g.iloc[: holdout_start(len(g), cfg)]
        clim = dev[available_climate_vars(dev, cfg)].ffill()
        for var in clim.columns:
            for lag in range(0, max_lag + 1):
                pair = pd.concat([clim[var].shift(lag), dev["total_cases"]], axis=1).dropna()
                if len(pair) < 30:
                    continue
                rows.append({"city": city, "variable": var, "lag": lag,
                             "spearman": float(pair.iloc[:, 0].corr(pair.iloc[:, 1], method="spearman")),
                             "n": int(len(pair))})
    return pd.DataFrame(rows)
