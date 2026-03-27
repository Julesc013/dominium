"""FAST test: XI-4z-fix1 v2 lock exposes the expected schema."""

from __future__ import annotations


TEST_ID = "test_xi4z_v2_lock_schema_valid"
TEST_TAGS = ["fast", "xi", "restructure", "lock"]


def run(repo_root: str):
    from tools.xstack.testx.tests.xi4z_fix1_testlib import committed_lock_v2

    payload = committed_lock_v2(repo_root)
    if str(payload.get("report_id", "")).strip() != "xi.4z.src_domain_mapping_lock_approved.v2":
        return {"status": "fail", "message": "XI-4z-fix1 v2 lock report_id drifted"}
    if str(payload.get("selected_layout_option", "")).strip() != "C":
        return {"status": "fail", "message": "XI-4z-fix1 v2 lock must retain Option C"}
    if payload.get("mapping_version") != 1:
        return {"status": "fail", "message": "XI-4z-fix1 v2 lock mapping_version drifted"}
    if str(payload.get("stability_class", "")).strip() != "provisional":
        return {"status": "fail", "message": "XI-4z-fix1 v2 lock must remain provisional"}
    if not list(payload.get("approved_for_xi5") or []):
        return {"status": "fail", "message": "XI-4z-fix1 v2 lock must expose approved rows"}
    if not str(payload.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-4z-fix1 v2 lock missing deterministic_fingerprint"}
    return {"status": "pass", "message": "XI-4z-fix1 v2 lock exposes the expected schema"}
