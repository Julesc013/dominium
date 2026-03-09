"""FAST test: EARTH-8 water view replay remains deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_water_view_deterministic"
TEST_TAGS = ["fast", "earth", "water", "replay", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth8_testlib import water_view_report

    report = water_view_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-8 water replay report did not complete"}
    if not bool(report.get("stable_across_repeated_runs")):
        return {"status": "fail", "message": "EARTH-8 water replay drifted across repeated runs"}
    if not str(report.get("artifact_fingerprint", "")).strip():
        return {"status": "fail", "message": "EARTH-8 water replay report omitted artifact fingerprint"}
    return {"status": "pass", "message": "EARTH-8 water replay remains deterministic"}
