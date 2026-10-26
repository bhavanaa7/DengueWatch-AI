import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from src.models import make_model
from src.feature_engineering import add_target, build_features, feature_columns
from src.validation import holdout_split, walk_forward_folds
from tests.helpers import small_cfg, synthetic


def test_walk_forward_gap_and_order():
    cfg = small_cfg(); cfg["validation"]["min_train_weeks"] = 100
    for h in (1, 2, 4, 8):
        folds = walk_forward_folds(520, h, cfg)
        ho = holdout_split(520, h, cfg)
        for f in folds:
            assert f["train_end"] + h < f["val_start"]       # training targets known before first validation origin
            assert f["val_start"] <= f["val_end"]
        assert all(a["val_end"] < b["val_start"] for a, b in zip(folds, folds[1:]))
        assert folds[-1]["val_end"] < ho["val_start"]         # holdout stays separate from model selection


def test_training_rows_targets_precede_validation_origin():
    cfg = small_cfg(); n = 200
    f = add_target(build_features(synthetic(n), cfg), 4)
    g = f[f.city == "sj"].reset_index(drop=True)
    sp = {"train_end": 100 - 4 - 1, "val_start": 100}
    tr = g.iloc[: sp["train_end"] + 1]
    assert tr["target_week_start"].max() < g["week_start_date"].iloc[sp["val_start"]]


def test_imputer_fit_on_training_only():
    train = pd.DataFrame({"a": [1.0, 2.0, np.nan]}); val = pd.DataFrame({"a": [1000.0, np.nan]})
    imp = SimpleImputer(strategy="median").fit(train)
    assert imp.statistics_[0] == 1.5 and imp.transform(val)[1, 0] == 1.5


def test_model_pipeline_runs_and_is_deterministic():
    cfg = small_cfg(); cfg["models"]["random_forest"]["n_estimators"] = 20
    f = add_target(build_features(synthetic(200), cfg), 2)
    g = f[(f.city == "sj")].reset_index(drop=True); cols = feature_columns(g)
    tr = g.iloc[:120]; tr = tr[tr.y.notna()]
    preds = []
    for _ in range(2):
        m, _ = make_model("random_forest", cfg, cols); m.fit(tr, tr.y.to_numpy())
        preds.append(m.predict(g.iloc[130:140]))
    assert np.allclose(preds[0], preds[1])
