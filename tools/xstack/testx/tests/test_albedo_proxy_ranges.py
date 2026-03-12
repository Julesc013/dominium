"""FAST test: EARTH-10 albedo proxy values stay within the canonical range."""

from __future__ import annotations

import sys


TEST_ID = "test_albedo_proxy_ranges"
TEST_TAGS = ["fast", "earth", "material_proxy", "albedo"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth10_testlib import material_proxy_albedo_report

    report = material_proxy_albedo_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "EARTH-10 albedo proxy values left the 0..1000 range ({} violations)".format(
                int(report.get("violation_count", 0) or 0)
            ),
        }
    return {"status": "pass", "message": "EARTH-10 albedo proxy values stay within range"}
