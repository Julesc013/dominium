"""FAST test: EARTH bucketed climate and tide updates remain deterministic across replay."""

from __future__ import annotations

import sys


TEST_ID = "test_bucket_update_deterministic"
TEST_TAGS = ["fast", "earth", "climate", "tide", "bucket", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth2_testlib import bucket_update_report as climate_bucket_update_report
    from tools.xstack.testx.tests.earth3_testlib import bucket_update_report as tide_bucket_update_report

    climate_report = climate_bucket_update_report(repo_root)
    if str(climate_report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-2 climate replay report did not complete"}
    if not bool(climate_report.get("stable_across_repeated_runs")):
        return {"status": "fail", "message": "EARTH-2 climate bucket replay drifted across repeated runs"}
    if not str(climate_report.get("climate_window_hash", "")).strip():
        return {"status": "fail", "message": "EARTH-2 climate replay omitted climate_window_hash"}

    tide_report = tide_bucket_update_report(repo_root)
    if str(tide_report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-3 tide replay report did not complete"}
    if not bool(tide_report.get("stable_across_repeated_runs")):
        return {"status": "fail", "message": "EARTH-3 tide bucket replay drifted across repeated runs"}
    if not str(tide_report.get("tide_window_hash", "")).strip():
        return {"status": "fail", "message": "EARTH-3 tide replay omitted tide_window_hash"}
    return {"status": "pass", "message": "EARTH bucketed climate and tide updates are deterministic"}
