"""FAST test: EARTH-1 river threshold marks channels deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_river_threshold_applied"
TEST_TAGS = ["fast", "earth", "hydrology", "worldgen", "river"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth1_testlib import verify_river_threshold_report

    report = verify_river_threshold_report(repo_root)
    candidate = dict(report.get("candidate") or {})
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-1 hydrology river threshold fixture did not produce a river-marked tile"}
    if not bool(candidate.get("river_flag", False)):
        return {"status": "fail", "message": "EARTH-1 hydrology threshold candidate omitted river_flag"}
    if int(candidate.get("drainage_accumulation_proxy", 0) or 0) < int(report.get("threshold", 0) or 0):
        return {"status": "fail", "message": "EARTH-1 hydrology threshold candidate fell below accumulation threshold"}
    return {"status": "pass", "message": "EARTH-1 river threshold marks channels deterministically"}
