"""Walk-forward evaluation, model selection (on development folds only), holdout report and final fit."""
import numpy as np
import pandas as pd

from .artifact_manager import save_json, save_model
from .evaluation import lead_time_metrics, mase_scale, outbreak_metrics, regression_metrics
from .tracking import log_run
from .feature_engineering import add_target, build_features, feature_columns
from .models import MODEL_NAMES, make_model
from .risk_classifier import classify, compute_thresholds
from .statistical_models import HAS_STATSMODELS, overdispersion_ratio
from .validation import holdout_split, walk_forward_folds


def _fit_predict(name, cfg, cols, frame, split):
    tr = frame.iloc[: split["train_end"] + 1]
    tr = tr[tr["y"].notna()]
    va = frame.iloc[split["val_start"]: split["val_end"] + 1]
    va = va[va["y"].notna()]
    model, reason = make_model(name, cfg, cols, int(frame["horizon"].iloc[0]))
    if model is None:
        return None, reason
    try:
        model.fit(tr, tr["y"].to_numpy())
        pred = np.clip(model.predict(va), 0, None)
    except Exception as exc:  # reported explicitly, never silently replaced
        return None, f"fit failed: {exc}"
    thr = compute_thresholds(tr["total_cases"], cfg)  # thresholds frozen from training data only
    rows = pd.DataFrame({
        "origin_week": va["week_start_date"].to_numpy(), "target_week": va["target_week_start"].to_numpy(),
        "y_true": va["y"].to_numpy(), "y_pred": pred, "outbreak_threshold": thr["outbreak"],
        "train_end_week": tr["week_start_date"].iloc[-1], "fold": split["fold"],
    })
    return (rows, tr, thr), None


def _metrics(rows, tr_cases, horizon):
    m = regression_metrics(rows["y_true"], rows["y_pred"], scale=mase_scale(tr_cases, horizon))
    m.update(outbreak_metrics(rows["y_true"], rows["y_pred"], rows["outbreak_threshold"].to_numpy()))
    m.update(lead_time_metrics(rows))
    m["n"] = int(len(rows))
    return m


def run_all(df, cfg, log=print):
    feats = build_features(df, cfg)
    cols = feature_columns(feats)
    cv_rows, ho_rows, pred_rows, availability, best, disp = [], [], [], {}, {}, {}
    for city in cfg["cities"]:
        cdf = feats[feats["city"] == city].reset_index(drop=True)
        n = len(cdf)
        disp[city] = overdispersion_ratio(cdf["total_cases"])
        for h in cfg["horizons"]:
            frame = add_target(cdf, h)
            folds = walk_forward_folds(n, h, cfg)
            ho = holdout_split(n, h, cfg)
            per_model = {}
            for name in MODEL_NAMES:
                oof = []
                for sp in folds:
                    res, reason = _fit_predict(name, cfg, cols, frame, sp)
                    if res is None:
                        availability[f"{city}|{h}|{name}"] = reason
                        break
                    rows, tr, _ = res
                    oof.append(rows)
                    cv_rows.append({"city": city, "horizon": h, "model": name, "fold": sp["fold"], **_metrics(rows, tr["y"], h)})
                if not oof:
                    continue
                oof = pd.concat(oof, ignore_index=True)
                dev_tr = frame.iloc[: folds[-1]["train_end"] + 1]
                per_model[name] = {"oof": oof, "mae": float(np.mean(np.abs(oof.y_true - oof.y_pred)))}
            if not per_model:
                continue
            sel = cfg["validation"]["selection_metric"]
            best_name = min(per_model, key=lambda k: per_model[k][sel])
            best[f"{city}|{h}"] = {"city": city, "horizon": h, "model": best_name, "dev_mae": per_model[best_name]["mae"]}
            q = (1 - cfg["uncertainty"]["coverage"]) / 2
            for name, info in per_model.items():
                res, reason = _fit_predict(name, cfg, cols, frame, ho)
                if res is None:
                    availability[f"{city}|{h}|{name}"] = reason
                    continue
                rows, tr, thr = res
                resid = info["oof"]["y_true"] - info["oof"]["y_pred"]
                lo_q, hi_q = np.quantile(resid, [q, 1 - q])
                rows["lower"] = np.clip(rows["y_pred"] + lo_q, 0, None)
                rows["upper"] = rows["y_pred"] + hi_q
                m = _metrics(rows, tr["y"], h)
                m["interval_coverage"] = float(np.mean((rows.y_true >= rows.lower) & (rows.y_true <= rows.upper)))
                m["interval_width"] = float(np.mean(rows.upper - rows.lower))
                ho_rows.append({"city": city, "horizon": h, "model": name, **m})
                for split_name, r in (("cv", info["oof"]), ("holdout", rows)):
                    r = r.copy()
                    r.insert(0, "split", split_name)
                    r.insert(0, "model", name); r.insert(0, "horizon", h); r.insert(0, "city", city)
                    pred_rows.append(r)
            log(f"{city} h={h}: best on dev folds = {best_name} (MAE {per_model[best_name]['mae']:.2f})")
            _final_fit(cfg, city, h, frame, cols, per_model, best_name, folds, ho, n)
    cv = pd.DataFrame(cv_rows)
    cv_agg = cv.groupby(["city", "horizon", "model"], as_index=False)[["mae", "rmse", "precision", "recall", "f1", "false_alarm_rate", "mean_lead_weeks"]].mean(numeric_only=True)
    ho_df = pd.DataFrame(ho_rows)
    rep = cfg["paths"]["reports_dir"]
    rep.mkdir(parents=True, exist_ok=True)
    cv.to_csv(rep / "metrics_cv_folds.csv", index=False)
    cv_agg.to_csv(rep / "metrics_cv.csv", index=False)
    ho_df.to_csv(rep / "metrics_holdout.csv", index=False)
    pd.concat(pred_rows).to_csv(rep / "predictions.csv", index=False)
    save_json(cfg, "best_models.json", list(best.values()))
    save_json(cfg, "model_availability.json", {
        "unavailable": availability, "statsmodels_installed": HAS_STATSMODELS,
        "overdispersion_var_over_mean": disp,
        "note": "var/mean >> 1 indicates overdispersion, so Poisson is unsuitable and Negative Binomial is preferred."})
    log(f"MLflow: {log_run(cfg, cv_agg, ho_df, best)}")
    return cv_agg, ho_df, best


def _final_fit(cfg, city, h, frame, cols, per_model, best_name, folds, ho, n):
    """Refit every available model on all labelled rows for operational forecasts (training cutoff = last labelled origin)."""
    full = frame[frame["y"].notna()]
    thr = compute_thresholds(frame["total_cases"], cfg)
    q = (1 - cfg["uncertainty"]["coverage"]) / 2
    for name, info in per_model.items():
        model, _ = make_model(name, cfg, cols, h)
        model.fit(full, full["y"].to_numpy())
        resid = info["oof"]["y_true"] - info["oof"]["y_pred"]
        lo_q, hi_q = [float(v) for v in np.quantile(resid, [q, 1 - q])]
        bundle = {"model": model, "cols": cols, "thresholds": thr, "resid_quantiles": [lo_q, hi_q]}
        meta = {"model": name, "city": city, "horizon": h, "n_features": len(cols), "is_best": name == best_name,
                "training_cutoff_origin": str(full["week_start_date"].iloc[-1].date()),
                "dev_cv_mae": info["mae"], "version": "v1", "feature_list": cols if name in ("random_forest", "xgboost") else None}
        save_model(cfg, city, h, name, bundle, meta)
