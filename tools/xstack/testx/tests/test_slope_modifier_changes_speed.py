"""FAST test: EARTH-6 slope response changes applied movement force deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_slope_modifier_changes_speed"
TEST_TAGS = ["fast", "earth", "embodiment", "collision", "slope"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth6_testlib import slope_modifier_report

    report = slope_modifier_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-6 slope-response fixture did not complete"}
    if str(report.get("uphill_direction_class", "")).strip() != "uphill":
        return {"status": "fail", "message": "EARTH-6 uphill classification missing from slope response"}
    if str(report.get("downhill_direction_class", "")).strip() != "downhill":
        return {"status": "fail", "message": "EARTH-6 downhill classification missing from slope response"}
    uphill_factor = int(report.get("uphill_factor_permille", 0) or 0)
    downhill_factor = int(report.get("downhill_factor_permille", 0) or 0)
    if not (uphill_factor < downhill_factor):
        return {"status": "fail", "message": "EARTH-6 slope response did not reduce uphill force relative to downhill assist"}
    return {"status": "pass", "message": "EARTH-6 slope modifier changes movement force"}
