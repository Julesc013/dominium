"""FAST test: EARTH-4 starfield remains deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_starfield_deterministic_same_inputs"
TEST_TAGS = ["fast", "earth", "sky", "starfield", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth4_testlib import starfield_report

    report = starfield_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-4 starfield report did not complete"}
    if not bool(report.get("stable")):
        return {"status": "fail", "message": "EARTH-4 starfield drifted across identical inputs"}
    if int(report.get("star_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "EARTH-4 starfield fixture produced no visible stars"}
    if not str(report.get("artifact_fingerprint", "")).strip():
        return {"status": "fail", "message": "EARTH-4 starfield report omitted artifact fingerprint"}
    return {"status": "pass", "message": "EARTH-4 starfield is deterministic for identical inputs"}
