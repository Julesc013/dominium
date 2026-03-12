"""FAST test: EARTH-10 surface flags remain consistent with material proxy classification."""

from __future__ import annotations

import sys


TEST_ID = "test_surface_flags_consistent_with_material"
TEST_TAGS = ["fast", "earth", "material_proxy", "surface_flags"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.earth10_testlib import material_proxy_flag_report

    report = material_proxy_flag_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "EARTH-10 surface flags diverged from material proxy classification ({} violations)".format(
                int(report.get("violation_count", 0) or 0)
            ),
        }
    return {"status": "pass", "message": "EARTH-10 surface flags match material proxy rules"}
