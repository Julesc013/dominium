"""FAST test: GAL-1 galaxy object generation remains bounded per cell."""

from __future__ import annotations

import sys


TEST_ID = "test_objects_bounded_per_cell"
TEST_TAGS = ["fast", "galaxy", "objects", "bounded"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.gal1_testlib import bounded_galaxy_object_generation_report

    report = bounded_galaxy_object_generation_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "GAL-1 bounded generation report did not complete"}
    max_objects = int(report.get("max_objects_per_cell", 0) or 0)
    max_allowed = int(report.get("max_allowed_objects_per_cell", 0) or 0)
    if max_objects > max_allowed:
        return {
            "status": "fail",
            "message": "GAL-1 object count exceeded the declared bound: {} > {}".format(max_objects, max_allowed),
        }
    return {"status": "pass", "message": "GAL-1 galaxy object generation remains bounded per cell"}
