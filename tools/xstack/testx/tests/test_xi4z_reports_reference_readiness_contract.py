"""FAST test: XI-4z reports reference the readiness contract canonically."""

from __future__ import annotations


TEST_ID = "test_xi4z_reports_reference_readiness_contract"
TEST_TAGS = ["fast", "xi", "restructure", "reports"]


def run(repo_root: str):
    from tools.review.xi4z_structure_approval_common import (
        XI5_READINESS_CONTRACT_REL,
        XI_4Z_DECISION_REPORT_REL,
        XI_4Z_FINAL_REL,
        XI_4Z_XI5_READINESS_REL,
    )
    from tools.xstack.testx.tests.xi4z_fix_testlib import committed_text

    for rel_path in (XI_4Z_DECISION_REPORT_REL, XI_4Z_XI5_READINESS_REL, XI_4Z_FINAL_REL):
        if XI5_READINESS_CONTRACT_REL not in committed_text(repo_root, rel_path):
            return {"status": "fail", "message": f"{rel_path} must reference the readiness contract canonically"}
    return {"status": "pass", "message": "XI-4z reports reference the readiness contract canonically"}
