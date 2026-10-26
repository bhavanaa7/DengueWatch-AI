# DengueWatch AI

Explainable Dengue Forecasting & Early-Warning Intelligence. React + TypeScript (Vite, MUI, Recharts, React-Leaflet) frontend, FastAPI + Python ML backend, built on the DrivenData DengAI dataset (San Juan, Iquitos).

## Verification status (be honest in interviews)
- Executed once during development on the real DengAI files: data loading/cleaning, feature engineering, walk-forward training of the baselines and Random Forest, and the original 13 unit tests.
- Written but **never executed**: the FastAPI service, SHAP / XGBoost / Negative Binomial / SARIMAX paths, MLflow logging, the lead-time metric, EDA and evaluation plotting, population normalisation, and the entire React frontend (including the Leaflet map). Expect small fixes on first run; run `python -m pytest`, `npm run lint`, `npm test`, `npm run build` yourself.
- No metric is hardcoded. Every number in the UI comes from your own training run.

## What is implemented
Data validation/cleaning; leakage-safe lag and rolling features; per-city, per-horizon (1/2/4/8 wk) models: seasonal naive, 4-week mean, Negative Binomial, SARIMAX, Random Forest, XGBoost; expanding-window walk-forward CV with a horizon gap plus a final holdout; MAE/RMSE/R²/MASE, outbreak precision/recall/F1/false-alarm/missed weeks and **outbreak warning lead time**; residual-based prediction intervals with holdout coverage; percentile risk categories; SHAP (or built-in importance fallback); prototype area ranking with optional **population-normalised incidence**; **EDA plots + notebook**; **MLflow** tracking (optional); FastAPI + React dashboard with a **city-level map**.

## Forecasting assumptions
A forecast at origin week *t* for horizon *h* predicts cases in week *t+h* using only climate and case data observed up to *t*. No future weather is used. Targets are shifted within each city. Imputation/feature selection are fit on training folds; thresholds come from training data only.

## Setup (Windows PowerShell)
```powershell
# Data: download dengue_features_train.csv and dengue_labels_train.csv from
# https://www.drivendata.org/competitions/44/dengai-predicting-disease-spread/data/
# and copy them into backend\data\raw\

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1            # if blocked: Set-ExecutionPolicy -Scope Process Bypass
python -m pip install -r requirements.txt
python -m pytest
python -m scripts.train_models          # walk-forward evaluation, artifacts, reports (several minutes; SARIMAX is slowest)
python -m scripts.generate_reports      # EDA + evaluation PNGs in reports\eda and reports\figures
python -m scripts.run_forecast          # optional: reports\forecasts_latest.csv
uvicorn api.main:app --port 8000        # docs: http://localhost:8000/docs
mlflow ui --backend-store-uri artifacts/mlruns   # optional experiment browser

# new terminal
cd frontend
npm install
npm run dev                             # http://localhost:5173
npm run lint ; npm test ; npm run build
```
Linux/macOS: `source .venv/bin/activate`. Notebook: `notebooks/01_exploratory_analysis.ipynb` (run from `notebooks/`).

## Population-normalised ranking
DengAI contains no population data and none is bundled. To enable incidence per 100,000, put official population figures for **both** cities in `backend/configs/config.yaml` under `population` (and cite the source in `population_source`). Until then the ranking uses raw counts and the UI says so. Cross-city incidence comparisons assume comparable case reporting.

## Metric notes
- **Lead time:** an outbreak episode is a run of target weeks at/above the frozen outbreak threshold. It counts as warned only if a forecast flagged it (within 4 weeks before the episode or during it) and was *issued at or before* the episode's first week; lead = weeks between issue and episode start. Late flags do not count.
- **SARIMAX:** ARMA(2,1) on log cases with annual Fourier terms; it supports forecasts only from the latest origin in operational mode (earlier-origin requests return an error).
- **Intervals:** walk-forward residual quantiles; holdout coverage can fall below nominal.

## Troubleshooting
- 503 "Model artifact missing" → run `python -m scripts.train_models`.
- "Dataset files not found" → put the two CSVs in `backend/data/raw/`.
- Frontend cannot reach backend → start uvicorn on port 8000, or set `VITE_API_URL` in `frontend/.env`.
- CORS error → set `FRONTEND_ORIGIN` for the backend.
- A model shows "unavailable" → install `xgboost` / `statsmodels` / `shap` / `mlflow`; missing models are reported, never faked.
- Map tiles blank → the browser needs internet access to OpenStreetMap tiles.
- Use Python 3.11 or 3.12.

## Structure
`backend/src` (pipeline), `backend/api/main.py` (REST), `backend/scripts` (train, forecast, reports), `backend/tests`, `frontend/src` (pages, components, services), `notebooks/`.

## Ethics and limitations
Retrospective research prototype on two cities. Correlation and feature contributions do not establish causation; percentile risk bands are not clinical definitions; do not use for operational public-health decisions. Respect DrivenData's data terms and do not commit the raw data.
