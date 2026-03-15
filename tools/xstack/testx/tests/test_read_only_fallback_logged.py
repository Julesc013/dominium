"""FAST test: DIST-6 read-only fallback is explicit and logged."""

from __future__ import annotations


TEST_ID = "test_read_only_fallback_logged"
TEST_TAGS = ["fast", "dist", "interop", "degrade"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist6_testlib import load_case

    report = load_case(repo_root, "contract_mismatch_read_only")
    negotiation = dict(report.get("negotiation") or {})
    save_open = dict(report.get("save_open") or {})
    surface_rows = [dict(row or {}) for row in list(report.get("surface_rows") or [])]
    if not report:
        return {"status": "fail", "message": "DIST-6 read-only report is missing"}
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "DIST-6 read-only case did not complete"}
    if str(negotiation.get("compatibility_mode_id", "")).strip() != "compat.read_only":
        return {"status": "fail", "message": "read-only case did not negotiate compat.read_only"}
    if not bool(save_open.get("read_only_required", False)):
        return {"status": "fail", "message": "save-open did not require read-only fallback"}
    if not list(save_open.get("degrade_reasons") or []):
        return {"status": "fail", "message": "save-open read-only fallback did not record degrade reasons"}
    if not any("compat.negotiation.result" in list(row.get("event_message_keys") or []) for row in surface_rows):
        return {"status": "fail", "message": "read-only interop did not log compat.negotiation.result"}
    return {"status": "pass", "message": "read-only fallback is explicit in negotiation and save-open output"}
