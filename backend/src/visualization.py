"""Model-evaluation figures built from saved reports (predictions.csv, metrics_holdout.csv, best_models.json)."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402


def generate_all(cfg):
    rep = cfg["paths"]["reports_dir"]
    need = [rep / "predictions.csv", rep / "metrics_holdout.csv", rep / "best_models.json"]
    if not all(p.exists() for p in need):
        return []
    pred = pd.read_csv(need[0], parse_dates=["origin_week", "target_week"])
    met = pd.read_csv(need[1])
    best = {(b["city"], b["horizon"]): b["model"] for b in json.load(open(need[2]))}
    out = rep / "figures"
    out.mkdir(parents=True, exist_ok=True)
    cities, hs = cfg["cities"], cfg["horizons"]
    names = cfg["city_names"]
    index = []

    def grid(title):
        fig, axes = plt.subplots(len(cities), len(hs), figsize=(4.2 * len(hs), 3.2 * len(cities)), squeeze=False)
        return fig, axes

    def save(fig, fname, title, caption):
        fig.suptitle(title, fontsize=13, fontweight="bold")
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        fig.savefig(out / f"{fname}.png", dpi=130)
        plt.close(fig)
        index.append({"file": f"figures/{fname}.png", "title": title, "caption": caption, "group": "evaluation"})

    def hold(c, h):
        m = best.get((c, h))
        return pred[(pred.city == c) & (pred.horizon == h) & (pred.model == m) & (pred.split == "holdout")].sort_values("target_week")

    fig, axes = grid("")
    for i, c in enumerate(cities):
        for j, h in enumerate(hs):
            d, ax = hold(c, h), axes[i, j]
            ax.plot(d.target_week, d.y_true, color="#141A46", lw=1, label="Actual")
            ax.plot(d.target_week, d.y_pred, color="#5B5BD6", lw=1, label="Predicted")
            ax.fill_between(d.target_week, d.lower, d.upper, color="#5B5BD6", alpha=0.15)
            ax.set_title(f"{names[c]}, h={h}", fontsize=9); ax.tick_params(labelsize=7)
    axes[0, 0].legend(fontsize=7)
    save(fig, "actual_vs_predicted", "Actual vs predicted (final holdout, best validated model)", "Shaded band = walk-forward residual interval.")

    fig, axes = grid("")
    for i, c in enumerate(cities):
        for j, h in enumerate(hs):
            d, ax = hold(c, h), axes[i, j]
            ax.scatter(d.y_pred, d.y_true - d.y_pred, s=8, alpha=0.5, color="#14B8A6"); ax.axhline(0, color="k", lw=0.8)
            ax.set_title(f"{names[c]}, h={h}", fontsize=9); ax.set_xlabel("Predicted", fontsize=7); ax.set_ylabel("Residual", fontsize=7)
    save(fig, "residuals", "Residuals vs predicted (final holdout)", "Residual = actual − predicted; look for bias and heteroscedasticity.")

    fig, axes = plt.subplots(1, len(cities), figsize=(5.5 * len(cities), 4), squeeze=False)
    for ax, c in zip(axes[0], cities):
        piv = met[met.city == c].pivot_table(index="horizon", columns="model", values="mae")
        piv.plot(ax=ax, marker="o"); ax.set_title(names[c]); ax.set_xlabel("Horizon (weeks)"); ax.set_ylabel("Holdout MAE")
    save(fig, "mae_by_horizon", "Holdout MAE by forecast horizon", "Lower is better; compare ML models against baselines.")

    fig, axes = grid("")
    for i, c in enumerate(cities):
        for j, h in enumerate(hs):
            r = met[(met.city == c) & (met.horizon == h) & (met.model == best.get((c, h)))]
            ax = axes[i, j]
            if r.empty:
                ax.axis("off"); continue
            r = r.iloc[0]
            cm = np.array([[r.tn, r.fp], [r.fn, r.tp]])
            ax.imshow(cm, cmap="Blues")
            for (a, b), v in np.ndenumerate(cm):
                ax.text(b, a, int(v), ha="center", va="center")
            ax.set_xticks([0, 1]); ax.set_xticklabels(["No outbreak", "Outbreak"], fontsize=7)
            ax.set_yticks([0, 1]); ax.set_yticklabels(["No outbreak", "Outbreak"], fontsize=7)
            ax.set_xlabel("Predicted", fontsize=7); ax.set_ylabel("Actual", fontsize=7); ax.set_title(f"{names[c]}, h={h}", fontsize=9)
    save(fig, "confusion_matrices", "Outbreak-detection confusion matrices (final holdout)", "Outbreak = at/above a training-derived percentile threshold frozen before evaluation.")

    with open(out / "index.json", "w") as fh:
        json.dump(index, fh, indent=2)
    return index
