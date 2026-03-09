"""FAST test: EARTH-7 seasonal shift changes wind band boundaries."""

from __future__ import annotations

import sys


TEST_ID = "test_seasonal_shift_changes_band_boundaries"
TEST_TAGS = ["fast", "earth", "wind", "seasonal"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth7_testlib import seasonal_shift_report

    report = seasonal_shift_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-7 seasonal shift report did not complete"}
    if int(report.get("changed_band_tile_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "EARTH-7 seasonal shift did not move any sampled band boundaries"}
    return {"status": "pass", "message": "EARTH-7 seasonal shift changes sampled band boundaries"}
