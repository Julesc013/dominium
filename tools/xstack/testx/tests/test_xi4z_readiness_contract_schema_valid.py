"""FAST test: XI-4z readiness contract remains explicit and bounded."""

from __future__ import annotations


TEST_ID = "test_xi4z_readiness_contract_schema_valid"
TEST_TAGS = ["fast", "xi", "restructure", "schema"]


def run(repo_root: str):
    from tools.xstack.testx.tests.xi4z_structure_approval_testlib import committed_readiness_contract

    payload = committed_readiness_contract(repo_root)
    if str(payload.get("report_id", "")).strip() != "xi.4z.xi5_readiness_contract.v1":
        return {"status": "fail", "message": "XI-4z readiness contract report_id drifted"}
    if str(payload.get("approved_lock_path", "")).strip() != "data/restructure/src_domain_mapping_lock_approved.json":
        return {"status": "fail", "message": "XI-4z readiness contract must point at the approved lock"}
    if str(payload.get("readiness_status", "")).strip() != "xi5_can_proceed_bounded":
        return {"status": "fail", "message": "XI-4z readiness contract readiness_status drifted"}
    for key in ("allowed_actions", "forbidden_actions", "gate_sequence_after_moves", "stop_conditions"):
        if not list(payload.get(key) or []):
            return {"status": "fail", "message": f"XI-4z readiness contract missing {key}"}
    if not str(payload.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-4z readiness contract missing deterministic_fingerprint"}
    return {"status": "pass", "message": "XI-4z readiness contract remains explicit and bounded"}
