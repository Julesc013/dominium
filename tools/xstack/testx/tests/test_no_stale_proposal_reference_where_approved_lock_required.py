"""FAST test: XI-4z canonical surfaces do not point at the proposal lock."""

from __future__ import annotations


TEST_ID = "test_no_stale_proposal_reference_where_approved_lock_required"
TEST_TAGS = ["fast", "xi", "restructure", "reports"]


def run(repo_root: str):
    from tools.review.xi4z_structure_approval_common import (
        SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL,
        XI4Z_DECISION_MANIFEST_REL,
        XI5_READINESS_CONTRACT_REL,
        XI_4Z_APPROVED_LAYOUT_REL,
        XI_4Z_DECISION_REPORT_REL,
        XI_4Z_FINAL_REL,
        XI_4Z_XI5_READINESS_REL,
    )
    from tools.xstack.testx.tests.xi4z_fix_testlib import committed_text
    import json
    import os

    proposal_marker = "src_domain_mapping_lock_proposal.json"
    for rel_path in (XI_4Z_DECISION_REPORT_REL, XI_4Z_XI5_READINESS_REL, XI_4Z_APPROVED_LAYOUT_REL, XI_4Z_FINAL_REL):
        if proposal_marker in committed_text(repo_root, rel_path):
            return {"status": "fail", "message": f"{rel_path} still references the proposal lock"}

    manifest_path = os.path.join(os.path.abspath(repo_root), XI4Z_DECISION_MANIFEST_REL.replace("/", os.sep))
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if str(manifest.get("approved_lock_path", "")).strip() != SRC_DOMAIN_MAPPING_LOCK_APPROVED_REL:
        return {"status": "fail", "message": "XI-4z decision manifest approved_lock_path drifted"}
    if str(manifest.get("readiness_contract_path", "")).strip() != XI5_READINESS_CONTRACT_REL:
        return {"status": "fail", "message": "XI-4z decision manifest readiness_contract_path drifted"}
    return {"status": "pass", "message": "XI-4z canonical surfaces no longer reference the proposal lock"}
