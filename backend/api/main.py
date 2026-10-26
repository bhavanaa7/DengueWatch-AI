"""FastAPI backend. Reads trained artifacts; never trains on request."""
import json
import os
from functools import lru_cache

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.artifact_manager import list_models, load_json, load_model
from src.config import load_config
from src.data_loader import load_clean
from src.explainability import global_importance, local_explanation
from src.forecasting import feature_table, forecast
from src.lag_analysis import lag_correlations
from src.prioritization import rank_locations

cfg = load_config()
CITY_NAMES = cfg["city_names"]
NAME_TO_CODE = {v.lower(): k for k, v in CITY_NAMES.items()} | {k: k for k in CITY_NAMES}

app = FastAPI(title="DengueWatch AI API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
                   allow_methods=["GET"], allow_headers=["*"])
cfg["paths"]["reports_dir"].mkdir(parents=True, exist_ok=True)
app.mount("/api/report-files", StaticFiles(directory=str(cfg["paths"]["reports_dir"])), name="report-files")


@lru_cache(maxsize=1)
def _feats():
    return feature_table(cfg)


@lru_cache(maxsize=1)
def _clean():
    return load_clean(cfg)


@lru_cache(maxsize=1)
def _lagcorr():
    return lag_correlations(_clean(), cfg)


@lru_cache(maxsize=64)
def _bundle(city, horizon, model):
    return load_model(cfg, city, horizon, model)


def records(df):
    return json.loads(df.to_json(orient="records", date_format="iso"))


def resolve(city, horizon):
    code = NAME_TO_CODE.get(city.lower())
    if code is None:
        raise HTTPException(422, f"Unknown city '{city}'. Use one of {list(CITY_NAMES.values())}.")
    if horizon not in cfg["horizons"]:
        raise HTTPException(422, f"Horizon must be one of {cfg['horizons']}.")
    return code


def guarded(fn):
    try:
        return fn()
    except FileNotFoundError as exc:
        raise HTTPException(503, str(exc))
    except KeyError as exc:
        raise HTTPException(404, str(exc))
    except ValueError as exc:
        raise HTTPException(422, str(exc))


@app.get("/api/health")
def health():
    ready = (cfg["paths"]["reports_dir"] / "best_models.json").exists()
    return {"status": "ok", "artifacts_ready": ready}


@app.get("/api/metadata")
def metadata():
    def run():
        df = _clean()
        ready = (cfg["paths"]["reports_dir"] / "best_models.json").exists()
        return {"app": "DengueWatch AI", "horizons": cfg["horizons"], "artifacts_ready": ready,
                "cities": [{"code": k, "name": v} for k, v in CITY_NAMES.items()],
                "models": sorted({m["model"] for m in list_models(cfg)}),
                "data_range": {"start": str(df.week_start_date.min().date()), "end": str(df.week_start_date.max().date())},
                "best_models": load_json(cfg, "best_models.json") if ready else [],
                "availability": load_json(cfg, "model_availability.json") if ready else {}}
    return guarded(run)


@app.get("/api/locations")
def locations():
    def run():
        df = _clean()
        return [{"code": c, "name": CITY_NAMES[c], "weeks": int(len(g)),
                 "start": str(g.week_start_date.min().date()), "end": str(g.week_start_date.max().date()),
                 "latest_cases": int(g.sort_values("week_start_date").total_cases.iloc[-1]),
                 **cfg.get("city_coords", {}).get(c, {})}
                for c, g in df.groupby("city")]
    return guarded(run)


@app.get("/api/forecast")
def get_forecast(city: str = "San Juan", horizon: int = 4, model: str | None = None, history_weeks: int = Query(156, ge=8, le=1000)):
    code = resolve(city, horizon)

    def run():
        f = forecast(cfg, _feats(), code, horizon, model_name=model)
        g = _clean()[_clean().city == code].sort_values("week_start_date").tail(history_weeks)
        hist = [{"week": d.date().isoformat(), "cases": c} for d, c in zip(g.week_start_date, g.total_cases)]
        pred = pd.read_csv(cfg["paths"]["reports_dir"] / "predictions.csv", parse_dates=["origin_week", "target_week"])
        bt = pred[(pred.city == code) & (pred.horizon == horizon) & (pred.model == f["model"]) & (pred.split == "holdout")]
        return {"forecast": {**f, "city_name": CITY_NAMES[code]}, "history": hist,
                "backtest_holdout": records(bt[["origin_week", "target_week", "y_true", "y_pred", "lower", "upper"]])}
    return guarded(run)


@app.get("/api/evaluation")
def evaluation():
    def run():
        rep = cfg["paths"]["reports_dir"]
        need = [rep / "metrics_cv.csv", rep / "metrics_holdout.csv"]
        if not all(p.exists() for p in need):
            raise FileNotFoundError("Evaluation reports missing. Run: python -m scripts.train_models")
        return {"validation_cv": records(pd.read_csv(need[0])), "holdout": records(pd.read_csv(need[1])),
                "best_models": load_json(cfg, "best_models.json"), "availability": load_json(cfg, "model_availability.json"),
                "notes": {"validation_cv": "Mean over expanding-window folds in the development period; used for model selection.",
                          "holdout": "Final chronological holdout, never used for model selection."}}
    return guarded(run)


@app.get("/api/weather")
def weather(city: str = "San Juan", weeks: int = Query(260, ge=8, le=1500)):
    code = resolve(city, cfg["horizons"][0])

    def run():
        g = _clean()[_clean().city == code].sort_values("week_start_date")
        cols = [c for c in ("precipitation_amt_mm", "reanalysis_avg_temp_k", "reanalysis_relative_humidity_percent") if c in g]
        s = g[["week_start_date", "weekofyear", "total_cases"] + cols].copy()
        s["precip_rmean4"] = s["precipitation_amt_mm"].rolling(4, min_periods=2).mean()
        s["avg_temp_c"] = s["reanalysis_avg_temp_k"] - 273.15
        seasonal = s.groupby("weekofyear").agg(cases=("total_cases", "mean"), precip=("precipitation_amt_mm", "mean")).reset_index()
        lc = _lagcorr()
        lc = lc[lc.city == code]
        return {"series": records(s.tail(weeks).rename(columns={"week_start_date": "week"})),
                "seasonal": records(seasonal), "lag_correlation": records(lc),
                "note": "Spearman correlations on the development period only; exploratory and not causal."}
    return guarded(run)


@app.get("/api/explanations")
def explanations(city: str = "San Juan", horizon: int = 4, model: str = "random_forest"):
    code = resolve(city, horizon)

    def run():
        bundle = _bundle(code, horizon, model)
        g = _feats()
        g = g[g.city == code].sort_values("week_start_date")
        bg = g.dropna(subset=["cases_lag0"]).tail(400)
        return {"city": CITY_NAMES[code], "horizon": horizon, "model": model,
                "origin_week": str(g.week_start_date.iloc[-1].date()),
                "global": global_importance(bundle["model"], bg),
                "local": local_explanation(bundle["model"], g.iloc[[-1]]),
                "warning": "Feature contributions describe the trained model, not causal effects of weather on outbreaks."}
    return guarded(run)


@app.get("/api/risk-ranking")
def risk_ranking(horizon: int = 4):
    resolve("San Juan", horizon)

    def run():
        fs = [forecast(cfg, _feats(), c, horizon) for c in cfg["cities"]]
        pop = {CITY_NAMES[c]: (cfg.get("population") or {}).get(c) for c in cfg["cities"]}
        ranking = rank_locations([{**f, "city": CITY_NAMES[f["city"]]} for f in fs], pop)
        normalised = all(r["incidence_per_100k"] is not None for r in ranking)
        return {"horizon": horizon, "ranking": ranking, "normalised": normalised,
                "population_note": (f"Incidence per 100,000 uses user-supplied population figures. Source: {cfg.get('population_source') or 'not stated'}."
                                    if normalised else
                                    "No population figures configured: the ranking uses raw case counts, not incidence. Set `population` in configs/config.yaml to enable per-100,000 normalisation."),
                "caveat": "Prototype ranking of two cities; not an intervention allocation policy."}
    return guarded(run)


@app.get("/api/figures")
def figures():
    """Index of generated EDA and evaluation figures (python -m scripts.generate_reports)."""
    out = []
    for sub in ("eda", "figures"):
        p = cfg["paths"]["reports_dir"] / sub / "index.json"
        if p.exists():
            with open(p) as fh:
                out.extend(json.load(fh))
    return {"plots": out}
