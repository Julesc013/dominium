"""FAST test: EARTH-2 temperature fields shift over the seasonal year window."""

from __future__ import annotations

import sys


TEST_ID = "test_temperature_field_changes_over_year"
TEST_TAGS = ["fast", "earth", "climate", "temperature", "time"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth2_testlib import climate_year_delta_report

    report = climate_year_delta_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-2 climate year delta report did not complete"}
    if int(report.get("changed_temperature_tile_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "EARTH-2 seasonal climate did not change any sampled tile temperatures"}
    if int(report.get("changed_daylight_tile_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "EARTH-2 seasonal climate did not change any sampled tile daylight values"}
    return {"status": "pass", "message": "EARTH-2 sampled temperature/daylight fields shift over the year"}
