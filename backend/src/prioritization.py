"""Prototype ranking of available locations.

Without population data the burden term uses raw forecast case counts (NOT incidence). If a population
is supplied for EVERY location (config `population`), forecasts are converted to cases per 100,000 and
the burden term uses incidence instead. Population figures are user-supplied; none are bundled.
Cross-city incidence comparisons still assume comparable case reporting.
"""
RISK_SCORE = {"Low": 0.0, "Medium": 0.5, "High": 1.0}
MONITORING = {
    "High": "Priority review: forecast is in the upper historical range for this location",
    "Medium": "Elevated watch: continue close monitoring of case reports",
    "Low": "Routine monitoring",
}


def rank_locations(forecasts, population=None):
    """forecasts: dicts from forecasting.forecast(); population: {city key used in forecasts: people} or None."""
    population = population or {}
    pops = [population.get(f["city"]) for f in forecasts]
    normalised = bool(forecasts) and all(p is not None and p > 0 for p in pops)
    inc = [f["predicted_cases"] / p * 1e5 if normalised else None for f, p in zip(forecasts, pops)]
    burden = inc if normalised else [f["predicted_cases"] for f in forecasts]
    total = sum(burden) or 1.0
    ranked = []
    for f, b, i in zip(forecasts, burden, inc):
        rel = min(f["predicted_cases"] / max(f["thresholds"]["high"], 1e-9), 2.0) / 2.0
        share = b / total
        score = 100 * (0.5 * rel + 0.3 * RISK_SCORE[f["risk"]] + 0.2 * share)
        unit = f"; {i:.1f} cases per 100,000 people" if i is not None else ""
        ranked.append({
            **{k: f[k] for k in ("city", "horizon", "predicted_cases", "risk", "target_week", "model")},
            "incidence_per_100k": round(i, 2) if i is not None else None,
            "priority_score": round(score, 1), "monitoring": MONITORING[f["risk"]],
            "explanation": (f"Forecast {f['predicted_cases']:.1f} cases vs this location's own High threshold "
                            f"{f['thresholds']['high']:.1f}; share of combined {'incidence' if normalised else 'case'} burden {share:.0%}{unit}."),
        })
    ranked.sort(key=lambda r: r["priority_score"], reverse=True)
    for k, r in enumerate(ranked, 1):
        r["rank"] = k
    return ranked
