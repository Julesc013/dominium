"""FAST test: DIST-6 pack-lock drift refuses save-open deterministically."""

from __future__ import annotations


TEST_ID = "test_pack_lock_mismatch_refuses"
TEST_TAGS = ["fast", "dist", "interop", "pack_compat"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist6_testlib import load_case

    report = load_case(repo_root, "pack_lock_mismatch")
    save_open = dict(report.get("save_open") or {})
    if not report:
        return {"status": "fail", "message": "DIST-6 pack-lock mismatch report is missing"}
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "DIST-6 pack-lock mismatch case did not complete"}
    if str(save_open.get("refusal_code", "")).strip() != "refusal.save.pack_lock_mismatch":
        return {"status": "fail", "message": "pack-lock mismatch did not refuse with refusal.save.pack_lock_mismatch"}
    return {"status": "pass", "message": "pack-lock mismatch is refused deterministically"}
