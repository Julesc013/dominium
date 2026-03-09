"""FAST test: EARTH-8 river mask preserves EARTH-1 hydrology flags and flow-derived ribbons."""

from __future__ import annotations

import sys


TEST_ID = "test_river_mask_matches_hydrology_flags"
TEST_TAGS = ["fast", "earth", "water", "hydrology"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth8_testlib import river_mask_report

    report = river_mask_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "EARTH-8 river mask diverged from hydrology signals: expected hydrology {}, got visual {}".format(
                report.get("expected_tile_ids"),
                report.get("actual_tile_ids"),
            ),
        }
    return {"status": "pass", "message": "EARTH-8 river mask preserves hydrology flags and bounded flow-derived ribbons"}
