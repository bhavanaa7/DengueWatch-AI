import numpy as np
from src.feature_engineering import add_target, build_features, feature_columns
from tests.helpers import small_cfg, synthetic


def test_target_alignment_within_city():
    cfg = small_cfg(); f = build_features(synthetic(), cfg)
    for h in (1, 4, 8):
        t = add_target(f, h)
        for city, g in t.groupby("city"):
            g = g.reset_index(drop=True)
            assert (g["y"].iloc[:-h].to_numpy() == g["total_cases"].iloc[h:].to_numpy()).all()
            assert g["y"].iloc[-h:].isna().all()          # no wrap-around into the other city
            assert (g["target_week_start"].iloc[:-h].to_numpy() == g["week_start_date"].iloc[h:].to_numpy()).all()


def test_case_lags_do_not_cross_city_boundaries():
    cfg = small_cfg(); f = build_features(synthetic(), cfg)
    iq = f[f.city == "iq"].reset_index(drop=True)
    assert np.isnan(iq["cases_lag1"].iloc[0])
    assert iq["cases_lag1"].iloc[1] == iq["total_cases"].iloc[0]


def test_rolling_features_use_only_past_and_present():
    cfg = small_cfg(); df = synthetic()
    f1 = build_features(df, cfg)
    df2 = df.copy()
    cut = 60
    df2.loc[df2.groupby("city").cumcount() > cut, ["precipitation_amt_mm", "total_cases"]] = 9999  # perturb the future
    f2 = build_features(df2, cfg)
    cols = feature_columns(f1)
    a = f1[f1.groupby("city").cumcount() <= cut][cols].to_numpy(float)
    b = f2[f2.groupby("city").cumcount() <= cut][cols].to_numpy(float)
    assert np.allclose(a, b, equal_nan=True)  # features at origin <= cut unchanged by future changes
