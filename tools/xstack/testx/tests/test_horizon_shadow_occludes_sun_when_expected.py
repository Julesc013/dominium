"""FAST test: EARTH-5 horizon-shadow approximation can occlude low sun when terrain relief is high."""

from __future__ import annotations

import sys


TEST_ID = "test_horizon_shadow_occludes_sun_when_expected"
TEST_TAGS = ["fast", "earth", "lighting", "shadow"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth5_testlib import horizon_shadow_report

    report = horizon_shadow_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-5 horizon shadow report did not complete"}
    if not bool(report.get("occludes_more_than_baseline")):
        return {"status": "fail", "message": "EARTH-5 exaggerated relief did not increase sun occlusion"}
    return {"status": "pass", "message": "EARTH-5 horizon shadow occludes low sun as expected"}
