"""FAST test: EARTH-5 illumination artifact remains deterministic for the same inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_illumination_deterministic"
TEST_TAGS = ["fast", "earth", "lighting", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth5_testlib import illumination_report

    report = illumination_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-5 illumination report did not complete"}
    if not bool(report.get("stable")):
        return {"status": "fail", "message": "EARTH-5 illumination artifact drifted across repeated runs"}
    return {"status": "pass", "message": "EARTH-5 illumination artifact is deterministic"}
