"""FAST test: EARTH-0 daylight proxy changes across seasonal ticks due to axial tilt."""

from __future__ import annotations

import sys


TEST_ID = "test_axial_tilt_affects_daylight"
TEST_TAGS = ["fast", "earth", "worldgen", "surface", "daylight", "temp"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth0_testlib import generate_earth_seasonal_pair

    first, second = generate_earth_seasonal_pair(repo_root)
    first_summary = dict(first.get("surface_summary") or {})
    second_summary = dict(second.get("surface_summary") or {})
    first_daylight = int(first_summary.get("daylight_value", 0) or 0)
    second_daylight = int(second_summary.get("daylight_value", 0) or 0)
    if first_daylight == second_daylight:
        return {"status": "fail", "message": "EARTH-0 seasonal daylight probe did not change across seasonal ticks"}
    return {"status": "pass", "message": "EARTH-0 axial tilt changes daylight across seasonal ticks"}
