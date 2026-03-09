"""FAST test: EARTH-2 polar daylight varies across the seasonal year window."""

from __future__ import annotations

import sys


TEST_ID = "test_polar_daylight_variation"
TEST_TAGS = ["fast", "earth", "climate", "daylight", "polar"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth2_testlib import polar_daylight_report

    report = polar_daylight_report(repo_root)
    daylight_a = int(report.get("daylight_a", -1))
    daylight_b = int(report.get("daylight_b", -1))
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-2 polar daylight report did not complete"}
    if not bool(report.get("variation_detected")):
        return {"status": "fail", "message": "EARTH-2 polar daylight did not vary across seasons"}
    if daylight_a < 0 or daylight_b < 0:
        return {"status": "fail", "message": "EARTH-2 polar daylight report omitted daylight values"}
    return {"status": "pass", "message": "EARTH-2 polar daylight varies across the year"}
