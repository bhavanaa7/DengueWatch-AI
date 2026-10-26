"""Optional MLflow experiment tracking. Skipped (with a message) if mlflow is not installed."""


def log_run(cfg, cv_agg, ho_df, best):
    tcfg = cfg.get("tracking", {})
    if not tcfg.get("enabled", True):
        return "tracking disabled in config"
    try:
        import mlflow
    except Exception:
        return "mlflow not installed - tracking skipped (pip install mlflow)"
    mlflow.set_tracking_uri((cfg["paths"]["artifacts_dir"] / "mlruns").resolve().as_uri())
    mlflow.set_experiment(tcfg.get("experiment", "denguewatch"))
    with mlflow.start_run() as run:
        mlflow.log_params({
            "seed": cfg["seed"], "horizons": str(cfg["horizons"]), "lags": str(cfg["features"]["lags"]),
            "rolling_windows": str(cfg["features"]["rolling_windows"]), "n_folds": cfg["validation"]["n_folds"],
            "holdout_fraction": cfg["validation"]["holdout_fraction"],
            **{f"rf_{k}": v for k, v in cfg["models"]["random_forest"].items()},
        })
        for r in ho_df.itertuples():
            for m in ("mae", "rmse", "f1"):
                v = getattr(r, m)
                if v == v and v is not None:
                    mlflow.log_metric(f"holdout_{m}__{r.city}_h{r.horizon}_{r.model}", float(v))
        for r in cv_agg.itertuples():
            if r.mae == r.mae:
                mlflow.log_metric(f"cv_mae__{r.city}_h{r.horizon}_{r.model}", float(r.mae))
        for rec in best:
            mlflow.set_tag(f"best__{rec['city']}_h{rec['horizon']}", rec["model"])
        for name in ("metrics_cv.csv", "metrics_holdout.csv", "best_models.json", "model_availability.json"):
            p = cfg["paths"]["reports_dir"] / name
            if p.exists():
                mlflow.log_artifact(str(p))
        return f"logged MLflow run {run.info.run_id} (view: mlflow ui --backend-store-uri {cfg['paths']['artifacts_dir'] / 'mlruns'})"
