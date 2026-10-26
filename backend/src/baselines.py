"""Baselines using only information available at the forecast origin."""
import numpy as np


class SeasonalNaive:
    """Prediction = cases one year before target week; falls back to last observed cases if unavailable."""
    name = "seasonal_naive"

    def fit(self, X, y):
        return self

    def predict(self, X):
        ref = X["seasonal_ref"].to_numpy(dtype=float)
        fallback = X["cases_lag0"].to_numpy(dtype=float)
        out = np.where(np.isnan(ref), fallback, ref)
        return np.nan_to_num(out, nan=0.0)


class RecentHistory:
    """Prediction = mean of the last 4 observed weeks (persistence-style baseline)."""
    name = "recent_mean4"

    def fit(self, X, y):
        self.fallback = float(np.nanmedian(y))
        return self

    def predict(self, X):
        return np.nan_to_num(X["cases_rmean4"].to_numpy(dtype=float), nan=self.fallback)
