"""FAST test: EARTH-9 geometry edits update hydrology locally and predictably."""

from __future__ import annotations

import sys


TEST_ID = "test_geometry_edit_updates_hydrology_locally"
TEST_TAGS = ["fast", "earth", "hydrology", "geometry_edit", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth9_testlib import earth_geometry_edit_report

    report = earth_geometry_edit_report(repo_root)
    hydrology = dict(report.get("hydrology_local_edit") or {})
    geometry = dict(report.get("geometry_edit_report") or {})
    if not bool(hydrology.get("local_update_ok")):
        return {"status": "fail", "message": "EARTH-9 hydrology local update check failed"}
    if int(hydrology.get("recomputed_tile_count", 0) or 0) <= 0:
        return {"status": "fail", "message": "EARTH-9 hydrology local edit recomputed zero tiles"}
    if int(hydrology.get("recomputed_tile_count", 0) or 0) > int(hydrology.get("window_tile_count", 0) or 0):
        return {"status": "fail", "message": "EARTH-9 hydrology local edit exceeded its window size"}
    if int(geometry.get("before_height_mm", 0) or 0) == int(geometry.get("after_height_mm", 0) or 0):
        return {"status": "fail", "message": "EARTH-9 geometry edit did not change terrain height"}
    return {"status": "pass", "message": "EARTH-9 geometry edits update hydrology locally"}
