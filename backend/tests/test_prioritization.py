from src.prioritization import rank_locations

TH = {"medium": 10, "high": 20, "outbreak": 40}


def _f(city, pred, risk):
    return {"city": city, "horizon": 4, "predicted_cases": pred, "risk": risk, "target_week": "2010-01-01", "model": "m", "thresholds": TH}


def test_without_population_no_incidence():
    out = rank_locations([_f("a", 5, "Low"), _f("b", 30, "High")])
    assert out[0]["city"] == "b" and out[0]["incidence_per_100k"] is None


def test_with_population_incidence_computed_and_used():
    out = rank_locations([_f("a", 10, "Medium"), _f("b", 10, "Medium")], {"a": 100000, "b": 1000000})
    byc = {r["city"]: r for r in out}
    assert byc["a"]["incidence_per_100k"] == 10.0 and byc["b"]["incidence_per_100k"] == 1.0
    assert byc["a"]["priority_score"] > byc["b"]["priority_score"]
