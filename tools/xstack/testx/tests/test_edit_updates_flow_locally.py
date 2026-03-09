"""FAST test: EARTH-1 geometry edits update hydrology locally without global recompute."""

from __future__ import annotations

import sys


TEST_ID = "test_edit_updates_flow_locally"
TEST_TAGS = ["fast", "earth", "hydrology", "geometry", "integration"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth1_testlib import verify_local_edit_hydrology_report

    report = verify_local_edit_hydrology_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-1 local geometry edit did not produce a hydrology update"}
    if not bool(report.get("local_update_ok")):
        return {"status": "fail", "message": "EARTH-1 geometry edit exceeded local hydrology update bounds"}
    if not list(report.get("changed_tile_ids") or []):
        return {"status": "fail", "message": "EARTH-1 geometry edit did not change any hydrology-backed tile artifact"}
    if int(report.get("recomputed_tile_count", 0) or 0) > int(report.get("window_tile_count", 0) or 0):
        return {"status": "fail", "message": "EARTH-1 geometry edit recomputed more tiles than the bounded window"}
    return {"status": "pass", "message": "EARTH-1 geometry edits update hydrology locally"}
