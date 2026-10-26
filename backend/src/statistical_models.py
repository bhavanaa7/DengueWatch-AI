"""Count regression (Negative Binomial GLM) with an explicit availability check."""
import numpy as np
import pandas as pd

try:
    import statsmodels.api as sm
    HAS_STATSMODELS = True
except Exception:  # pragma: no cover
    HAS_STATSMODELS = False

NB_FEATURES = ["sin_week", "cos_week", "log_cases_lag0", "log_cases_rmean4", "log_cases_rmean12"]
OPTIONAL = ["precipitation_amt_mm_rmean8", "reanalysis_specific_humidity_g_per_kg_rmean8", "reanalysis_avg_temp_k_rmean8"]


def overdispersion_ratio(y):
    y = np.asarray(y, float)
    y = y[~np.isnan(y)]
    return float(y.var(ddof=1) / max(y.mean(), 1e-9))


class NegativeBinomialModel:
    name = "negbin"

    def __init__(self):
        self.cols, self.res, self.mu, self.sd, self.alpha = None, None, None, None, None

    def _design(self, X):
        d = pd.DataFrame(index=X.index)
        d["sin_week"], d["cos_week"] = X["sin_week"], X["cos_week"]
        d["log_cases_lag0"] = np.log1p(X["cases_lag0"])
        d["log_cases_rmean4"] = np.log1p(X["cases_rmean4"])
        d["log_cases_rmean12"] = np.log1p(X["cases_rmean12"])
        for c in OPTIONAL:
            if c in X.columns:
                d[c] = X[c]
        return d

    def fit(self, X, y):
        d = self._design(X)
        self.fill = d.median()
        d = d.fillna(self.fill)
        self.mu, self.sd = d.mean(), d.std().replace(0, 1)
        Z = sm.add_constant((d - self.mu) / self.sd, has_constant="add")
        yv = np.asarray(y, float)
        pois = sm.GLM(yv, Z, family=sm.families.Poisson()).fit()
        mu = pois.mu
        # method-of-moments NB2 alpha from Poisson fit (Cameron-Trivedi auxiliary regression)
        self.alpha = float(max(np.sum(((yv - mu) ** 2 - mu)) / np.sum(mu ** 2), 1e-4))
        self.res = sm.GLM(yv, Z, family=sm.families.NegativeBinomial(alpha=self.alpha)).fit()
        self.cols = list(d.columns)
        return self

    def predict(self, X):
        d = self._design(X)[self.cols].fillna(self.fill)
        Z = sm.add_constant((d - self.mu) / self.sd, has_constant="add")
        return np.asarray(self.res.predict(Z))


def _fourier(dates):
    """Annual Fourier terms from calendar dates (known in advance, so no leakage)."""
    doy = pd.to_datetime(pd.Series(list(dates))).dt.dayofyear.to_numpy()
    ang = 2 * np.pi * doy / 365.25
    return np.column_stack([np.sin(ang), np.cos(ang)])


class SarimaxModel:
    """ARMA(2,1) on log1p(weekly cases) with annual Fourier exogenous terms (SARIMAX).

    Fit on the case history observed up to the training cutoff. At prediction time the filter is
    extended with cases observed up to each forecast origin (no future data), then forecasts h steps.
    Operational forecasts are only supported from origins after the training end (latest origin).
    """
    name = "sarimax"

    def __init__(self, horizon, order=(2, 0, 1)):
        self.h, self.order, self.res, self.end_date = int(horizon), order, None, None

    def fit(self, X, y):
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        h = self.h
        endog = np.concatenate([np.log1p(X["total_cases"].to_numpy(float)), np.log1p(np.asarray(y, float)[-h:])])
        dates = pd.concat([pd.Series(X["week_start_date"].to_numpy()), pd.Series(X["target_week_start"].to_numpy()[-h:])], ignore_index=True)
        mod = SARIMAX(endog, exog=_fourier(dates), order=self.order, trend="c",
                      enforce_stationarity=False, enforce_invertibility=False)
        self.res = mod.fit(disp=False, maxiter=200)
        self.end_date = pd.Timestamp(dates.iloc[-1])
        return self

    def predict(self, X):
        cur, last = self.res, self.end_date
        preds = np.empty(len(X))
        for pos in np.argsort(X["week_start_date"].to_numpy()):
            row = X.iloc[pos]
            d = pd.Timestamp(row["week_start_date"])
            if d > last:
                if (d - last).days > 10:
                    raise ValueError("SARIMAX needs consecutive weekly observations after the training end")
                cur = cur.extend(np.array([np.log1p(row["cases_lag0"])]), exog=_fourier([d]))
                last = d
            elif d < last:
                raise ValueError("SARIMAX can only forecast from origins at/after its training end (use the latest origin)")
            future = pd.date_range(d + pd.Timedelta(weeks=1), periods=self.h, freq="7D")
            preds[pos] = np.expm1(np.asarray(cur.forecast(steps=self.h, exog=_fourier(future)))[-1])
        return np.clip(preds, 0, None)
