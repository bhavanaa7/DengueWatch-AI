"""Exploratory data analysis plots, saved as PNG under reports/eda with an index.json.

All plots describe associations in observed data; correlation is not causation. Outbreak-vs-normal
comparisons and lag correlations use only the development period (before the final holdout).
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .feature_engineering import available_climate_vars  # noqa: E402
from .lag_analysis import lag_correlations  # noqa: E402
from .risk_classifier import compute_thresholds  # noqa: E402
from .validation import holdout_start  # noqa: E402

CLIMATE = (("precipitation_amt_mm", "Rainfall (mm)"), ("reanalysis_avg_temp_k", "Avg temperature (°C)"),
           ("reanalysis_relative_humidity_percent", "Relative humidity (%)"))
NON_FEATURE = ("city", "year", "weekofyear", "week_start_date", "total_cases")


class _Saver:
    def __init__(self, outdir):
        self.dir = outdir
        self.dir.mkdir(parents=True, exist_ok=True)
        self.index = []

    def save(self, fig, name, title, caption):
        fig.suptitle(title, fontsize=13, fontweight="bold")
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        fig.savefig(self.dir / f"{name}.png", dpi=130)
        plt.close(fig)
        self.index.append({"file": f"eda/{name}.png", "title": title, "caption": caption, "group": "eda"})


def _val(g, col):
    return g[col] - 273.15 if col.endswith("_k") else g[col]


def _climate(df):
    return [(c, l) for c, l in CLIMATE if c in df.columns]


def generate_all(df, cfg, outdir=None):
    outdir = outdir or cfg["paths"]["reports_dir"] / "eda"
    sv = _Saver(outdir)
    df = df.sort_values(["city", "week_start_date"])
    cities = [c for c in cfg["cities"] if c in set(df["city"])]
    name = lambda c: cfg["city_names"].get(c, c)  # noqa: E731
    clim = _climate(df)
    n = len(cities)

    fig, axes = plt.subplots(n, 1, figsize=(11, 3.2 * n), squeeze=False)
    for ax, c in zip(axes[:, 0], cities):
        g = df[df.city == c]
        ax.plot(g.week_start_date, g.total_cases, color="#141A46", lw=1)
        ax.set_title(name(c)); ax.set_ylabel("Weekly cases"); ax.set_xlabel("Week start date")
    sv.save(fig, "01_weekly_cases", "Weekly dengue cases", "Observed weekly case counts per city; note large epidemic years.")

    if clim:
        fig, axes = plt.subplots(len(clim), n, figsize=(6 * n, 2.8 * len(clim)), squeeze=False)
        for j, c in enumerate(cities):
            g = df[df.city == c]
            for i, (col, lab) in enumerate(clim):
                axes[i, j].plot(g.week_start_date, _val(g, col), lw=0.8, color="#5B5BD6")
                axes[i, j].set_ylabel(lab); axes[i, j].set_title(name(c) if i == 0 else "")
        sv.save(fig, "02_climate_trends", "Rainfall, temperature and humidity", "Weekly climate series (reanalysis temperature converted to °C).")

    fig, axes = plt.subplots(1, n, figsize=(6.5 * n, 4), squeeze=False)
    for ax, c in zip(axes[0], cities):
        g = df[df.city == c]
        months = sorted(g.week_start_date.dt.month.unique())
        ax.boxplot([g.total_cases[g.week_start_date.dt.month == m] for m in months], showfliers=False)
        ax.set_xticklabels(months); ax.set_xlabel("Month"); ax.set_ylabel("Weekly cases"); ax.set_title(name(c))
    sv.save(fig, "03_seasonality", "Seasonal distribution of dengue cases", "Case counts by calendar month (outliers hidden).")

    if clim:
        fig, axes = plt.subplots(n, len(clim), figsize=(5 * len(clim), 3.6 * n), squeeze=False)
        for i, c in enumerate(cities):
            g = df[df.city == c]
            for j, (col, lab) in enumerate(clim):
                x = _val(g, col)
                rho = pd.concat([x, g.total_cases], axis=1).dropna().corr(method="spearman").iloc[0, 1]
                axes[i, j].scatter(x, g.total_cases, s=6, alpha=0.4, color="#14B8A6")
                axes[i, j].set_xlabel(lab); axes[i, j].set_ylabel("Weekly cases"); axes[i, j].set_title(f"{name(c)} (Spearman {rho:.2f})")
        sv.save(fig, "04_cases_vs_climate", "Dengue cases vs same-week climate", "Same-week associations only; lagged relationships are on the lag plot. Not causal.")

    ccols = available_climate_vars(df, cfg) + ["total_cases"]
    fig, axes = plt.subplots(1, n, figsize=(7 * n, 6.5), squeeze=False)
    for ax, c in zip(axes[0], cities):
        cm = df[df.city == c][ccols].corr(method="spearman")
        im = ax.imshow(cm, vmin=-1, vmax=1, cmap="coolwarm")
        ax.set_xticks(range(len(ccols))); ax.set_xticklabels(ccols, rotation=90, fontsize=7)
        ax.set_yticks(range(len(ccols))); ax.set_yticklabels(ccols, fontsize=7); ax.set_title(name(c))
        fig.colorbar(im, ax=ax, fraction=0.046)
    sv.save(fig, "07_correlation_heatmap", "Spearman correlation heatmap", "Pairwise rank correlations of climate variables and cases (same week). Association, not causation.")

    lc = lag_correlations(df, cfg)
    if not lc.empty:
        fig, axes = plt.subplots(1, n, figsize=(7 * n, 5), squeeze=False)
        for ax, c in zip(axes[0], cities):
            piv = lc[lc.city == c].pivot(index="variable", columns="lag", values="spearman")
            im = ax.imshow(piv, aspect="auto", vmin=-0.6, vmax=0.6, cmap="coolwarm")
            ax.set_xticks(range(piv.shape[1])); ax.set_xticklabels(piv.columns)
            ax.set_yticks(range(piv.shape[0])); ax.set_yticklabels(piv.index, fontsize=7)
            ax.set_xlabel("Lag (weeks): climate at t-lag vs cases at t"); ax.set_title(name(c))
            fig.colorbar(im, ax=ax, fraction=0.046)
        sv.save(fig, "08_lag_correlation", "Climate lag correlation with dengue cases (development period only)", "Spearman ρ by lag. Ignores autocorrelation and confounding; exploratory only.")

    fig, axes = plt.subplots(1, n, figsize=(6.5 * n, 4), squeeze=False)
    for ax, c in zip(axes[0], cities):
        g = df[df.city == c].reset_index(drop=True)
        dev = g.iloc[: holdout_start(len(g), cfg)]
        t = compute_thresholds(dev.total_cases, cfg)
        ax.hist(g.total_cases.dropna(), bins=40, color="#5B5BD6")
        for k, col in (("medium", "#F59E0B"), ("high", "#DC2626"), ("outbreak", "#141A46")):
            ax.axvline(t[k], color=col, ls="--", label=f"{k} ≥ {t[k]:.0f}")
        ax.set_yscale("log"); ax.set_xlabel("Weekly cases"); ax.set_ylabel("Weeks (log)"); ax.set_title(name(c)); ax.legend(fontsize=8)
    sv.save(fig, "09_case_distribution", "Distribution of weekly case counts", "Right-skewed counts; dashed lines are percentile thresholds from the development period.")

    if clim:
        fig, axes = plt.subplots(n, len(clim), figsize=(4.5 * len(clim), 3.6 * n), squeeze=False)
        for i, c in enumerate(cities):
            g = df[df.city == c].reset_index(drop=True)
            dev = g.iloc[: holdout_start(len(g), cfg)]
            flag = dev.total_cases >= compute_thresholds(dev.total_cases, cfg)["outbreak"]
            for j, (col, lab) in enumerate(clim):
                x = _val(dev, col)
                axes[i, j].boxplot([x[~flag].dropna(), x[flag].dropna()], showfliers=False)
                axes[i, j].set_xticklabels(["Non-outbreak", "Outbreak"]); axes[i, j].set_ylabel(lab); axes[i, j].set_title(name(c))
        sv.save(fig, "10_outbreak_vs_normal", "Climate in outbreak vs non-outbreak weeks", "Outbreak = at/above the development-period outbreak percentile. Same-week climate; descriptive only.")

    with open(outdir / "index.json", "w") as fh:
        json.dump(sv.index, fh, indent=2)
    return sv.index
