"""FAST test: EARTH-6 body tick sets grounded state when terrain contact occurs."""

from __future__ import annotations

import sys


TEST_ID = "test_grounded_state_set_correctly"
TEST_TAGS = ["fast", "earth", "embodiment", "collision", "grounded"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth6_testlib import ground_contact_report

    report = ground_contact_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EARTH-6 grounded-state fixture did not complete"}
    if not bool(report.get("grounded", False)):
        return {"status": "fail", "message": "EARTH-6 body tick failed to mark grounded contact"}
    if int(report.get("terrain_height_mm", 0) or 0) <= 0:
        return {"status": "fail", "message": "EARTH-6 grounded-state fixture omitted terrain height"}
    return {"status": "pass", "message": "EARTH-6 grounded state set correctly"}
