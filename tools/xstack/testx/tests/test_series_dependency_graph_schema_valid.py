"""FAST test: Π-0 series dependency graph exposes the expected structure."""

from __future__ import annotations


TEST_ID = "test_series_dependency_graph_schema_valid"
TEST_TAGS = ["fast", "pi", "blueprint", "series"]


def run(repo_root: str):
    from tools.xstack.testx.tests.meta_blueprint_testlib import committed_series_dependency_graph

    payload = committed_series_dependency_graph(repo_root)
    if str(payload.get("report_id", "")).strip() != "pi.0.series_dependency_graph.v1":
        return {"status": "fail", "message": "series dependency graph report_id drifted"}
    series = list(payload.get("series") or [])
    edges = list(payload.get("edges") or [])
    if len(series) < 6:
        return {"status": "fail", "message": "series dependency graph must contain the planned series set"}
    if not edges:
        return {"status": "fail", "message": "series dependency graph must contain prerequisite edges"}
    first = dict(series[0] or {})
    for key in ("series_id", "purpose", "prerequisites", "outputs", "risk_level"):
        if key not in first:
            return {"status": "fail", "message": f"series row missing '{key}'"}
    if not str(payload.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "series dependency graph missing deterministic_fingerprint"}
    return {"status": "pass", "message": "Π-0 series dependency graph exposes the expected structure"}
