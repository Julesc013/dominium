"""FAST test: GAL-0 galactic region thresholds remain stable for the canonical fixture cells."""

from __future__ import annotations

import sys


TEST_ID = "test_region_id_thresholds_stable"
TEST_TAGS = ["fast", "galaxy", "proxy", "regions"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.gal0_testlib import galaxy_region_threshold_report

    report = galaxy_region_threshold_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "GAL-0 galactic region thresholds drifted ({} mismatches)".format(int(report.get("mismatch_count", 0) or 0)),
        }
    return {"status": "pass", "message": "GAL-0 galactic region thresholds are stable"}
