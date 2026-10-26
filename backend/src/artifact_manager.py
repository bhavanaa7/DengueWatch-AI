"""Save/load trained models and metadata (joblib + json). Models are never retrained on load."""
import json
import joblib


def _stem(city, horizon, model):
    return f"{city}_h{horizon}_{model}"


def save_model(cfg, city, horizon, model_name, bundle, metadata):
    d = cfg["paths"]["artifacts_dir"] / "models"
    d.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, d / f"{_stem(city, horizon, model_name)}.joblib")
    with open(d / f"{_stem(city, horizon, model_name)}.json", "w") as fh:
        json.dump(metadata, fh, indent=2, default=str)


def load_model(cfg, city, horizon, model_name):
    p = cfg["paths"]["artifacts_dir"] / "models" / f"{_stem(city, horizon, model_name)}.joblib"
    if not p.exists():
        raise FileNotFoundError(f"Model artifact missing: {p.name}. Run: python -m scripts.train_models")
    return joblib.load(p)


def list_models(cfg):
    d = cfg["paths"]["artifacts_dir"] / "models"
    if not d.exists():
        return []
    out = []
    for p in sorted(d.glob("*.json")):
        with open(p) as fh:
            out.append(json.load(fh))
    return out


def save_json(cfg, name, obj):
    d = cfg["paths"]["reports_dir"]
    d.mkdir(parents=True, exist_ok=True)
    with open(d / name, "w") as fh:
        json.dump(obj, fh, indent=2, default=str)


def load_json(cfg, name):
    p = cfg["paths"]["reports_dir"] / name
    if not p.exists():
        raise FileNotFoundError(f"Report missing: {name}. Run: python -m scripts.train_models")
    with open(p) as fh:
        return json.load(fh)
