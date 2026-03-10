"""FAST test: EARTH-9 deterministic stress scenario and harness remain stable."""

from __future__ import annotations

import sys


TEST_ID = "test_earth_stress_scenario_deterministic"
TEST_TAGS = ["fast", "earth", "stress", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth9_testlib import earth_stress_report, earth_stress_scenario

    scenario = earth_stress_scenario(repo_root)
    report = earth_stress_report(repo_root)
    if not str(scenario.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "EARTH-9 scenario omitted deterministic_fingerprint"}
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-9 stress harness did not complete"}
    if not bool(report.get("stable_across_repeated_runs")):
        return {"status": "fail", "message": "EARTH-9 stress harness drifted across repeated runs"}
    if not bool(dict(report.get("assertions") or {}).get("stress_scenario_deterministic")):
        return {"status": "fail", "message": "EARTH-9 scenario generation was not deterministic"}
    return {"status": "pass", "message": "EARTH-9 scenario generation and harness are deterministic"}
