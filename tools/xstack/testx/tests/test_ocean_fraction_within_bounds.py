"""FAST test: EARTH-0 macro ocean fraction stays within the configured Earth-like envelope."""

from __future__ import annotations

import sys


TEST_ID = "test_ocean_fraction_within_bounds"
TEST_TAGS = ["fast", "earth", "worldgen", "surface", "ocean"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth0_testlib import generate_earth_surface_report

    report = generate_earth_surface_report(repo_root)
    if not bool(report.get("ocean_ratio_within_bounds")):
        return {
            "status": "fail",
            "message": "EARTH-0 ocean ratio drifted outside bounds (observed {} permille)".format(
                report.get("ocean_ratio_permille", "<missing>")
            ),
        }
    return {"status": "pass", "message": "EARTH-0 ocean ratio remains within Earth-like bounds"}
