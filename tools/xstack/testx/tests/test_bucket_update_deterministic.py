"""FAST test: EARTH-2 bucketed climate updates remain deterministic across replay."""

from __future__ import annotations

import sys


TEST_ID = "test_bucket_update_deterministic"
TEST_TAGS = ["fast", "earth", "climate", "bucket", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth2_testlib import bucket_update_report

    report = bucket_update_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-2 climate replay report did not complete"}
    if not bool(report.get("stable_across_repeated_runs")):
        return {"status": "fail", "message": "EARTH-2 climate bucket replay drifted across repeated runs"}
    if not str(report.get("climate_window_hash", "")).strip():
        return {"status": "fail", "message": "EARTH-2 climate replay omitted climate_window_hash"}
    return {"status": "pass", "message": "EARTH-2 bucketed climate updates are deterministic"}
