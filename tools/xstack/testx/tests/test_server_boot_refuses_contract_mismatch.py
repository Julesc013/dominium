"""FAST test: SERVER-MVP-0 boot refuses session contract mismatch."""

from __future__ import annotations


TEST_ID = "test_server_boot_refuses_contract_mismatch"
TEST_TAGS = ["fast", "server", "compat"]


def run(repo_root: str):
    from tools.xstack.testx.tests.server_mvp0_testlib import boot_fixture, mutate_session_field

    fixture = boot_fixture(
        repo_root,
        suffix="contract_mismatch",
        session_mutator=mutate_session_field("contract_bundle_hash", "0" * 64),
    )
    boot = dict(fixture.get("boot") or {})
    if str(boot.get("result", "")) != "refused":
        return {"status": "fail", "message": "server boot should refuse mismatched contract bundle hash"}
    reason_code = str((dict(boot.get("refusal") or {})).get("reason_code", "")).strip()
    if reason_code != "refusal.session.contract_mismatch":
        return {
            "status": "fail",
            "message": "expected refusal.session.contract_mismatch, got '{}'".format(reason_code),
        }
    return {"status": "pass", "message": "server boot contract mismatch refusal is deterministic"}
