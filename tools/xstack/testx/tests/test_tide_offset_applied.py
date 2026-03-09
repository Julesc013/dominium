"""FAST test: EARTH-8 applies nonzero tide visual offsets for water tiles."""

from __future__ import annotations

import sys


TEST_ID = "test_tide_offset_applied"
TEST_TAGS = ["fast", "earth", "water", "tide"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth8_testlib import tide_offset_report

    report = tide_offset_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "EARTH-8 tide offset visual did not produce nonzero water tiles",
        }
    return {"status": "pass", "message": "EARTH-8 tide visual offset is applied"}
