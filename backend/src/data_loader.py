"""Load, validate and clean the DengAI training files into one record per city-week."""
import json
import numpy as np
import pandas as pd

KEYS = ["city", "year", "weekofyear"]
REQUIRED_FEATURE_COLS = KEYS + ["week_start_date"]
REQUIRED_LABEL_COLS = KEYS + ["total_cases"]

DOWNLOAD_HELP = (
    "Dataset files not found. Download dengue_features_train.csv and dengue_labels_train.csv from "
    "https://www.drivendata.org/competitions/44/dengai-predicting-disease-spread/data/ "
    "and place them in backend/data/raw/."
)


def load_raw(cfg):
    raw = cfg["paths"]["raw_dir"]
    fpath, lpath = raw / cfg["files"]["features"], raw / cfg["files"]["labels"]
    if not fpath.exists() or not lpath.exists():
        raise FileNotFoundError(DOWNLOAD_HELP)
    feats, labels = pd.read_csv(fpath), pd.read_csv(lpath)
    missing = [c for c in REQUIRED_FEATURE_COLS if c not in feats.columns]
    missing += [c for c in REQUIRED_LABEL_COLS if c not in labels.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return feats, labels


def clean(feats, labels):
    """Join, de-duplicate, sort chronologically per city. Does NOT impute (done later, past-only).

    Irregular week gaps in the source are reported, not interpolated. total_cases is never filled.
    """
    report = {"rows_features": len(feats), "rows_labels": len(labels)}
    report["duplicate_feature_keys"] = int(feats.duplicated(KEYS).sum())
    report["duplicate_label_keys"] = int(labels.duplicated(KEYS).sum())
    feats = feats.drop_duplicates(KEYS, keep="first")
    labels = labels.drop_duplicates(KEYS, keep="first")
    df = feats.merge(labels, on=KEYS, how="inner", validate="one_to_one")
    report["rows_joined"] = len(df)
    df["week_start_date"] = pd.to_datetime(df["week_start_date"], errors="coerce")
    report["invalid_dates"] = int(df["week_start_date"].isna().sum())
    df = df.dropna(subset=["week_start_date"]).copy()
    num = [c for c in df.columns if c not in ("city", "week_start_date")]
    df[num] = df[num].apply(pd.to_numeric, errors="coerce")
    report["negative_cases"] = int((df["total_cases"] < 0).sum())
    df.loc[df["total_cases"] < 0, "total_cases"] = np.nan
    report["missing_target"] = int(df["total_cases"].isna().sum())
    df = df.sort_values(["city", "week_start_date"]).reset_index(drop=True)
    report["missing_before"] = {k: int(v) for k, v in df.isna().sum().items() if v}
    gaps = {}
    for city, g in df.groupby("city"):
        d = g["week_start_date"].diff().dt.days.dropna().astype(int)
        gaps[city] = {
            "weeks": len(g), "start": str(g.week_start_date.min().date()), "end": str(g.week_start_date.max().date()),
            "step_days_counts": {str(k): int(v) for k, v in d.value_counts().items()},
        }
    report["cities"] = gaps
    return df, report


def build_clean_dataset(cfg, save=True):
    feats, labels = load_raw(cfg)
    df, report = clean(feats, labels)
    if save:
        out = cfg["paths"]["processed_dir"]
        out.mkdir(parents=True, exist_ok=True)
        df.to_csv(out / "dengue_clean.csv", index=False)
        with open(out / "data_quality_report.json", "w") as fh:
            json.dump(report, fh, indent=2)
    return df, report


def load_clean(cfg):
    p = cfg["paths"]["processed_dir"] / "dengue_clean.csv"
    if not p.exists():
        return build_clean_dataset(cfg)[0]
    return pd.read_csv(p, parse_dates=["week_start_date"])
