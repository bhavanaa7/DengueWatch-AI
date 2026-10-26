"""python -m scripts.run_forecast [--origin YYYY-MM-DD]  — forecasts for every city/horizon from saved artifacts."""
import argparse
import pandas as pd
from src.config import load_config
from src.forecasting import feature_table, forecast


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origin", default=None, help="Forecast origin (default: latest observed week)")
    a = ap.parse_args()
    cfg = load_config()
    feats = feature_table(cfg)
    rows = [forecast(cfg, feats, c, h, origin=a.origin) for c in cfg["cities"] for h in cfg["horizons"]]
    out = pd.DataFrame(rows).drop(columns=["thresholds"])
    path = cfg["paths"]["reports_dir"] / "forecasts_latest.csv"
    out.to_csv(path, index=False)
    print(out.to_string(index=False))
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
