"""FAST test: EARTH-7 wind field replay remains deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_wind_field_deterministic"
TEST_TAGS = ["fast", "earth", "wind", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth7_testlib import wind_field_report

    report = wind_field_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-7 wind replay report did not complete"}
    if not bool(report.get("stable_across_repeated_runs")):
        return {"status": "fail", "message": "EARTH-7 wind replay drifted across repeated runs"}
    if not str(report.get("wind_window_hash", "")).strip():
        return {"status": "fail", "message": "EARTH-7 wind replay omitted wind_window_hash"}
    return {"status": "pass", "message": "EARTH-7 wind replay is deterministic"}
