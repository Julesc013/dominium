"""FAST test: EARTH-5 horizon-shadow sampling remains bounded."""

from __future__ import annotations

import sys


TEST_ID = "test_sampling_bounded"
TEST_TAGS = ["fast", "earth", "lighting", "bounded"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth5_testlib import sampling_bounded_report

    report = sampling_bounded_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-5 bounded-shadow report did not complete"}
    if not bool(report.get("sampling_bounded")):
        return {"status": "fail", "message": "EARTH-5 bounded-shadow report omitted bounded marker"}
    if int(report.get("sample_count", 0) or 0) > 8:
        return {"status": "fail", "message": "EARTH-5 shadow sample count exceeded bounded policy"}
    return {"status": "pass", "message": "EARTH-5 shadow sampling is bounded"}
