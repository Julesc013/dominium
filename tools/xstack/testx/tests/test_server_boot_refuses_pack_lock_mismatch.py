"""FAST test: SERVER-MVP-0 boot refuses pack-lock mismatch."""

from __future__ import annotations


TEST_ID = "test_server_boot_refuses_pack_lock_mismatch"
TEST_TAGS = ["fast", "server", "pack"]


def run(repo_root: str):
    from tools.xstack.testx.tests.server_mvp0_testlib import boot_fixture, mutate_session_field

    fixture = boot_fixture(
        repo_root,
        suffix="pack_lock_mismatch",
        session_mutator=mutate_session_field("pack_lock_hash", "1" * 64),
    )
    boot = dict(fixture.get("boot") or {})
    if str(boot.get("result", "")) != "refused":
        return {"status": "fail", "message": "server boot should refuse mismatched pack_lock_hash"}
    reason_code = str((dict(boot.get("refusal") or {})).get("reason_code", "")).strip()
    if reason_code != "refusal.session.pack_lock_mismatch":
        return {
            "status": "fail",
            "message": "expected refusal.session.pack_lock_mismatch, got '{}'".format(reason_code),
        }
    return {"status": "pass", "message": "server boot pack-lock mismatch refusal is deterministic"}
