"""FAST test: EARTH-7 band directions vary deterministically by latitude."""

from __future__ import annotations

import sys


TEST_ID = "test_band_direction_changes_by_latitude"
TEST_TAGS = ["fast", "earth", "wind", "latitude"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth7_testlib import latitude_band_report

    report = latitude_band_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-7 latitude band report did not complete"}
    samples = dict(report.get("samples") or {})
    if str((dict(samples.get("hadley") or {})).get("wind_band_id", "")) != "wind.band.hadley":
        return {"status": "fail", "message": "EARTH-7 hadley sample did not resolve to wind.band.hadley"}
    if str((dict(samples.get("ferrel") or {})).get("wind_band_id", "")) != "wind.band.ferrel":
        return {"status": "fail", "message": "EARTH-7 ferrel sample did not resolve to wind.band.ferrel"}
    if str((dict(samples.get("polar") or {})).get("wind_band_id", "")) != "wind.band.polar":
        return {"status": "fail", "message": "EARTH-7 polar sample did not resolve to wind.band.polar"}
    return {"status": "pass", "message": "EARTH-7 wind bands vary deterministically by latitude"}
