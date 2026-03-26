"""FAST test: XI-4z approved lock exposes the expected schema."""

from __future__ import annotations


TEST_ID = "test_xi4z_approved_lock_schema_valid"
TEST_TAGS = ["fast", "xi", "restructure", "lock"]


def run(repo_root: str):
    from tools.xstack.testx.tests.xi4z_structure_approval_testlib import committed_lock

    payload = committed_lock(repo_root)
    if str(payload.get("report_id", "")).strip() != "xi.4z.src_domain_mapping_lock_approved.v1":
        return {"status": "fail", "message": "XI-4z approved lock report_id drifted"}
    if str(payload.get("selected_layout_option", "")).strip() != "C":
        return {"status": "fail", "message": "XI-4z approved lock must retain Option C"}
    if str(payload.get("stability_class", "")).strip() != "provisional":
        return {"status": "fail", "message": "XI-4z approved lock must remain provisional"}
    if payload.get("mapping_version") != 0:
        return {"status": "fail", "message": "XI-4z approved lock mapping_version drifted"}
    total = 0
    for key in ("approved_for_xi5", "approved_to_attic", "deferred_to_xi5b"):
        rows = list(payload.get(key) or [])
        if key != "deferred_to_xi5b" and not rows:
            return {"status": "fail", "message": f"XI-4z approved lock missing rows for {key}"}
        total += len(rows)
    if total <= 0:
        return {"status": "fail", "message": "XI-4z approved lock must classify at least one row"}
    if not str(payload.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-4z approved lock missing deterministic_fingerprint"}
    return {"status": "pass", "message": "XI-4z approved lock exposes the expected schema"}
