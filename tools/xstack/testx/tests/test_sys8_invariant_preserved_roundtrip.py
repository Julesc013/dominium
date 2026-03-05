"""FAST test: SYS-8 preserves invariants across stress roundtrip."""

from __future__ import annotations

import sys


TEST_ID = "test_invariant_preserved_roundtrip_sys8"
TEST_TAGS = ["fast", "system", "sys8", "invariants"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys8_testlib import make_stress_scenario, run_stress_report

    scenario = make_stress_scenario(repo_root=repo_root, seed=88027)
    report = run_stress_report(repo_root=repo_root, scenario=scenario)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SYS-8 stress report did not complete"}
    assertions = dict(report.get("assertions") or {})
    if bool(assertions.get("invariants_preserved_roundtrip")) is not True:
        return {"status": "fail", "message": "SYS-8 invariant preservation assertion failed"}
    return {"status": "pass", "message": "SYS-8 invariants preserved across stress roundtrip"}
