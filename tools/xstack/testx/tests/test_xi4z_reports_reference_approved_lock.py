"""FAST test: XI-4z reports reference the approved lock canonically."""

from __future__ import annotations


TEST_ID = "test_xi4z_reports_reference_approved_lock"
TEST_TAGS = ["fast", "xi", "restructure", "reports"]


def run(repo_root: str):
    from tools.review.xi4z_structure_approval_common import (
        SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
        XI_4Z_DECISION_REPORT_REL,
        XI_4Z_FINAL_REL,
        XI_4Z_XI5_READINESS_REL,
    )
    from tools.xstack.testx.tests.xi4z_fix_testlib import committed_text

    for rel_path in (XI_4Z_DECISION_REPORT_REL, XI_4Z_XI5_READINESS_REL, XI_4Z_FINAL_REL):
        if SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL not in committed_text(repo_root, rel_path):
            return {"status": "fail", "message": f"{rel_path} must reference the approved lock canonically"}
    return {"status": "pass", "message": "XI-4z reports reference the approved lock canonically"}
