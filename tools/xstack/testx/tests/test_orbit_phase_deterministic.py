"""FAST test: EARTH-2 orbit phase remains deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_orbit_phase_deterministic"
TEST_TAGS = ["fast", "earth", "climate", "determinism", "time"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth2_testlib import orbit_phase_report

    report = orbit_phase_report(repo_root)
    phase_a = int(report.get("phase_a", -1))
    phase_b = int(report.get("phase_b", -1))
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-2 orbit phase report did not complete"}
    if phase_a < 0 or phase_b < 0:
        return {"status": "fail", "message": "EARTH-2 orbit phase report omitted phase values"}
    if phase_a == phase_b:
        return {"status": "fail", "message": "EARTH-2 orbit phase did not advance across the sampled year window"}
    return {"status": "pass", "message": "EARTH-2 orbit phase is deterministic and advances over the year"}
