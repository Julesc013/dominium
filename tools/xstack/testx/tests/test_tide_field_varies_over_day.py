"""FAST test: EARTH-3 tide field changes over a day window."""

from __future__ import annotations

import sys


TEST_ID = "test_tide_field_varies_over_day"
TEST_TAGS = ["fast", "earth", "tide", "field", "time"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth3_testlib import tide_day_delta_report

    report = tide_day_delta_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-3 tide day-delta report did not complete"}
    if int(report.get("changed_tide_tile_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "EARTH-3 tide proxy did not change across the sampled day window"}
    return {"status": "pass", "message": "EARTH-3 tide field varies over the sampled day window"}
