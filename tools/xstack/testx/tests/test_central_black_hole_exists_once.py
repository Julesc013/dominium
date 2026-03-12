"""FAST test: GAL-1 central black-hole stub exists exactly once."""

from __future__ import annotations

import sys


TEST_ID = "test_central_black_hole_exists_once"
TEST_TAGS = ["fast", "galaxy", "objects", "compact", "black_hole"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.gal1_testlib import central_black_hole_once_report

    report = central_black_hole_once_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "GAL-1 central black-hole replay report did not complete"}
    actual_count = int(report.get("central_black_hole_count", 0) or 0)
    if actual_count != 1:
        return {
            "status": "fail",
            "message": "GAL-1 central black-hole count drifted: expected 1, got {}".format(actual_count),
        }
    return {"status": "pass", "message": "GAL-1 central black-hole stub exists exactly once"}
