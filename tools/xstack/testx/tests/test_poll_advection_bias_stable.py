"""FAST test: EARTH-7 wind-backed POLL advection bias remains deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_poll_advection_bias_stable"
TEST_TAGS = ["fast", "earth", "wind", "pollution"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth7_testlib import poll_advection_report

    report = poll_advection_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-7 POLL advection report did not complete"}
    if not bool(report.get("stable_across_repeated_runs")):
        return {"status": "fail", "message": "EARTH-7 POLL advection drifted across repeated runs"}
    if not bool(report.get("wind_effect_observed")):
        return {"status": "fail", "message": "EARTH-7 POLL advection report observed no wind effect"}
    return {"status": "pass", "message": "EARTH-7 POLL advection bias is deterministic and effective"}
