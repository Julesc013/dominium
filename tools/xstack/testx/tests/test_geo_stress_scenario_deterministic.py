"""FAST test: GEO-10 stress scenario remains deterministic across repeated runs."""

from __future__ import annotations


TEST_ID = "test_geo_stress_scenario_deterministic"
TEST_TAGS = ["fast", "geo", "stress", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.geo10_testlib import geo10_stress_report

    report = geo10_stress_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "GEO-10 stress report did not complete"}
    if not bool(report.get("stable_across_repeated_runs", False)):
        return {"status": "fail", "message": "GEO-10 stress report drifted across repeated runs"}
    if not all(bool(value) for value in dict(report.get("assertions") or {}).values()):
        return {"status": "fail", "message": "GEO-10 stress assertions were not all satisfied"}
    if not str(dict(report.get("proof_summary") or {}).get("cross_platform_determinism_hash", "")).strip():
        return {"status": "fail", "message": "GEO-10 stress report missing cross-platform determinism hash"}
    return {"status": "pass", "message": "GEO-10 stress scenario deterministic across repeated runs"}
