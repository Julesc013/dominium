"""FAST test: EARTH-3 lunar phase remains deterministic for identical ticks."""

from __future__ import annotations

import sys


TEST_ID = "test_lunar_phase_deterministic"
TEST_TAGS = ["fast", "earth", "tide", "phase", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth3_testlib import lunar_phase_report

    report = lunar_phase_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-3 lunar phase report did not complete"}
    if int(report.get("lunar_phase_a", -1) or -1) != int(report.get("lunar_phase_b", -2) or -2):
        return {"status": "fail", "message": "EARTH-3 lunar phase drifted for identical tick inputs"}
    return {"status": "pass", "message": "EARTH-3 lunar phase deterministic for identical ticks"}
