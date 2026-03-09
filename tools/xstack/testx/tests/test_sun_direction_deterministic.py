"""FAST test: EARTH-4 sun direction proxy remains deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_sun_direction_deterministic"
TEST_TAGS = ["fast", "earth", "sky", "sun", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth4_testlib import sun_direction_report

    report = sun_direction_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-4 sun direction report did not complete"}
    if dict(report.get("sun_direction_a") or {}) != dict(report.get("sun_direction_b") or {}):
        return {"status": "fail", "message": "EARTH-4 sun direction drifted for identical inputs"}
    if int(report.get("sun_elevation_a", -1) or -1) != int(report.get("sun_elevation_b", -2) or -2):
        return {"status": "fail", "message": "EARTH-4 sun elevation drifted for identical inputs"}
    return {"status": "pass", "message": "EARTH-4 sun direction proxy is deterministic"}
