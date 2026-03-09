"""FAST test: EARTH-0 retains bounded polar ice coverage."""

from __future__ import annotations

import sys


TEST_ID = "test_polar_ice_present"
TEST_TAGS = ["fast", "earth", "worldgen", "surface", "ice"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth0_testlib import generate_earth_surface_report

    report = generate_earth_surface_report(repo_root)
    if not bool(report.get("polar_ice_present")):
        return {
            "status": "fail",
            "message": "EARTH-0 polar ice coverage drifted outside bounds (observed {} permille)".format(
                report.get("polar_ice_ratio_permille", "<missing>")
            ),
        }
    return {"status": "pass", "message": "EARTH-0 polar ice remains present and bounded"}
