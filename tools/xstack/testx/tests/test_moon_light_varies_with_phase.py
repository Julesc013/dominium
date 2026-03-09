"""FAST test: EARTH-5 moon fill light changes with lunar phase."""

from __future__ import annotations

import sys


TEST_ID = "test_moon_light_varies_with_phase"
TEST_TAGS = ["fast", "earth", "lighting", "moon"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth5_testlib import moon_phase_report

    report = moon_phase_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-5 moon phase report did not complete"}
    if not bool(report.get("changed")):
        return {"status": "fail", "message": "EARTH-5 moon fill light did not change across lunar phases"}
    return {"status": "pass", "message": "EARTH-5 moon fill light varies with lunar phase"}
