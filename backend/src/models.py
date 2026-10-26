"""Model factory. Returns (model, None) or (None, reason) when a model is unavailable."""
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from .baselines import RecentHistory, SeasonalNaive
from .statistical_models import HAS_STATSMODELS, NegativeBinomialModel, SarimaxModel
from .feature_engineering import feature_columns

MODEL_NAMES = ["seasonal_naive", "recent_mean4", "negbin", "sarimax", "random_forest"]
K_FEATURES = 60


class FeatureFrameModel:
    """Wraps a sklearn Pipeline so it accepts the full feature frame and selects columns itself."""

    def __init__(self, name, pipe, cols):
        self.name, self.pipe, self.cols = name, pipe, cols

    def fit(self, X, y):
        self.pipe.fit(X[self.cols], y)
        return self

    def predict(self, X):
        return self.pipe.predict(X[self.cols]).clip(min=0)


def make_model(name, cfg, cols, horizon=None):
    seed = cfg["seed"]
    if name == "seasonal_naive":
        return SeasonalNaive(), None
    if name == "recent_mean4":
        return RecentHistory(), None
    if name == "negbin":
        if not HAS_STATSMODELS:
            return None, "statsmodels not installed"
        return NegativeBinomialModel(), None
    if name == "sarimax":
        if not HAS_STATSMODELS:
            return None, "statsmodels not installed"
        if horizon is None:
            return None, "horizon required for sarimax"
        return SarimaxModel(horizon), None
    # imputation and feature selection are inside the pipeline, so they are fit on the training fold only
    if name == "random_forest":
        est = RandomForestRegressor(random_state=seed, **cfg["models"]["random_forest"])
    else:
        return None, f"unknown model {name}"
    pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("select", SelectKBest(f_regression, k=min(K_FEATURES, len(cols)))),
        ("est", est),
    ])
    return FeatureFrameModel(name, pipe, cols), None
