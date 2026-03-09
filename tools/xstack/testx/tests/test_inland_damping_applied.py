"""FAST test: EARTH-3 inland tide damping remains stronger over ocean tiles than land tiles."""

from __future__ import annotations

import sys


TEST_ID = "test_inland_damping_applied"
TEST_TAGS = ["fast", "earth", "tide", "damping", "surface"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth3_testlib import inland_damping_report

    report = inland_damping_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-3 inland damping report did not complete"}
    if not bool(report.get("inland_damping_applied")):
        return {"status": "fail", "message": "EARTH-3 inland damping did not reduce land tide amplitude below ocean amplitude"}
    return {"status": "pass", "message": "EARTH-3 inland damping reduces land tide amplitude"}
