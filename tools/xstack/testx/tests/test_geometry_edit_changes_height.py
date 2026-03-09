"""FAST test: EARTH-6 collision height updates after deterministic geometry edits."""

from __future__ import annotations

import sys


TEST_ID = "test_geometry_edit_changes_height"
TEST_TAGS = ["fast", "earth", "embodiment", "collision", "geometry_edit"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth6_testlib import geometry_edit_height_report

    report = geometry_edit_height_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-6 geometry-edit collision fixture did not complete"}
    if int(report.get("before_height_mm", 0) or 0) == int(report.get("after_height_mm", 0) or 0):
        return {"status": "fail", "message": "EARTH-6 collision height did not change after geometry edit"}
    return {"status": "pass", "message": "EARTH-6 geometry edit updates collision height"}
