"""FAST test: EARTH-8 replay regenerates the same water-view artifact fingerprint."""

from __future__ import annotations

import sys


TEST_ID = "test_replay_water_view_fingerprint_match"
TEST_TAGS = ["fast", "earth", "water", "replay", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth8_testlib import water_view_report

    report = water_view_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-8 replay report did not complete"}
    if not bool(report.get("stable_across_repeated_runs")):
        return {"status": "fail", "message": "EARTH-8 replay drifted across repeated runs"}
    if not str(report.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "EARTH-8 replay report omitted deterministic fingerprint"}
    return {"status": "pass", "message": "EARTH-8 replay reproduces the same water-view artifact fingerprint"}
