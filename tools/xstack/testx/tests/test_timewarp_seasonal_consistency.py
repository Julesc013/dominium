"""FAST test: EARTH-9 time warp preserves seasonal, daylight, tide, and moon-phase consistency."""

from __future__ import annotations

import sys


TEST_ID = "test_timewarp_seasonal_consistency"
TEST_TAGS = ["fast", "earth", "timewarp", "season", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth9_testlib import earth_timewarp_report

    report = earth_timewarp_report(repo_root)
    climate_year = dict(report.get("climate_year_delta") or {})
    polar = dict(report.get("polar_daylight") or {})
    tide = dict(report.get("tide_day_delta") or {})
    moon = dict(report.get("lighting_moon_phase") or {})
    if int(climate_year.get("changed_temperature_tile_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "EARTH-9 climate season delta did not change temperature tiles"}
    if int(climate_year.get("changed_daylight_tile_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "EARTH-9 climate season delta did not change daylight tiles"}
    if not bool(polar.get("variation_detected")):
        return {"status": "fail", "message": "EARTH-9 polar daylight variation was not detected"}
    if int(tide.get("changed_tide_tile_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "EARTH-9 tide delta did not change tide tiles"}
    if not bool(moon.get("changed")):
        return {"status": "fail", "message": "EARTH-9 moon lighting phase did not change across time warp"}
    return {"status": "pass", "message": "EARTH-9 time warp remains seasonally consistent"}
