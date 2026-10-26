"""SHAP for tree models, falling back to built-in importances when shap is unavailable.

Contributions describe how the trained model produced its output; they do not show that a
weather variable caused an outbreak.
"""
import re
import numpy as np

try:
    import shap
    HAS_SHAP = True
except Exception:  # pragma: no cover
    HAS_SHAP = False

_PAT = re.compile(r"^(?P<var>.+?)_(?P<kind>lag|rmean|rsum|rstd)(?P<n>\d+)$")


def parse_feature(name):
    m = _PAT.match(name)
    if not m:
        return {"variable": name, "kind": "other", "lag": None}
    return {"variable": m["var"], "kind": m["kind"], "lag": int(m["n"])}


def _prepare(model, X):
    pipe = model.pipe
    Xi = pipe.named_steps["impute"].transform(X[model.cols])
    sel = pipe.named_steps["select"]
    return sel.transform(Xi), np.array(model.cols)[sel.get_support()], pipe.named_steps["est"]


def global_importance(model, X_background):
    if not hasattr(model, "pipe"):
        return {"available": False, "reason": "Explanations are supported for tree models only."}
    Xs, names, est = _prepare(model, X_background)
    method = None
    imp = None
    if HAS_SHAP:
        try:
            imp = np.abs(shap.TreeExplainer(est).shap_values(Xs)).mean(axis=0)
            method = "mean |SHAP|"
        except Exception:
            pass
    if imp is None and hasattr(est, "get_booster"):
        try:
            import xgboost as xgb
            contribs = est.get_booster().predict(xgb.DMatrix(Xs, feature_names=list(names)), pred_contribs=True)
            imp = np.abs(contribs[:, :-1]).mean(axis=0)
            method = "mean |SHAP| (TreeSHAP)"
        except Exception:
            pass
    if imp is None:
        imp = np.asarray(est.feature_importances_)
        method = "built-in impurity importance" if HAS_SHAP else "built-in impurity importance (install shap for SHAP values)"
    feats = [{"feature": n, **parse_feature(n), "importance": float(v)} for n, v in zip(names, imp)]
    feats.sort(key=lambda r: r["importance"], reverse=True)
    by_var, by_lag = {}, {}
    for f in feats:
        by_var[f["variable"]] = by_var.get(f["variable"], 0.0) + f["importance"]
        if f["lag"] is not None and f["kind"] == "lag":
            by_lag[f["lag"]] = by_lag.get(f["lag"], 0.0) + f["importance"]
    return {"available": True, "method": method, "features": feats[:30],
            "by_variable": sorted(({"variable": k, "importance": v} for k, v in by_var.items()), key=lambda r: -r["importance"]),
            "by_lag": sorted(({"lag": k, "importance": v} for k, v in by_lag.items()), key=lambda r: r["lag"])}


def local_explanation(model, row, top=12):
    if not hasattr(model, "pipe"):
        return {"available": False, "reason": "Explanations are supported for tree models only."}
    Xs, names, est = _prepare(model, row)
    vals, base = None, None
    if HAS_SHAP:
        try:
            ex = shap.TreeExplainer(est)
            vals = ex.shap_values(Xs)[0]
            base = float(np.ravel(ex.expected_value)[0])
        except Exception:
            pass
    if (vals is None or base is None) and hasattr(est, "get_booster"):
        try:
            import xgboost as xgb
            contribs = est.get_booster().predict(xgb.DMatrix(Xs, feature_names=list(names)), pred_contribs=True)[0]
            vals = contribs[:-1]
            base = float(contribs[-1])
        except Exception:
            pass
    if vals is None or base is None:
        return {"available": False, "reason": "Install the shap package to see per-prediction contributions."}
    order = np.argsort(-np.abs(vals))[:top]
    return {"available": True, "base_value": base,
            "contributions": [{"feature": str(names[i]), "value": float(Xs[0][i]), "contribution": float(vals[i]),
                               **parse_feature(str(names[i]))} for i in order]}
