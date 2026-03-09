"""FAST test: EARTH-1 drainage accumulation is monotonic along downstream edges."""

from __future__ import annotations

import sys


TEST_ID = "test_drainage_accumulation_monotonic"
TEST_TAGS = ["fast", "earth", "hydrology", "worldgen", "invariant"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth1_testlib import verify_window_monotonicity_report

    report = verify_window_monotonicity_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-1 hydrology window violated downstream accumulation monotonicity"}
    if int(report.get("violation_count", 0) or 0) != 0:
        return {"status": "fail", "message": "EARTH-1 monotonicity report contained violations"}
    return {"status": "pass", "message": "EARTH-1 drainage accumulation stays monotonic downstream"}
