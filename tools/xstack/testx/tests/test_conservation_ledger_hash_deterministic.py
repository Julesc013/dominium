"""STRICT test: ledger hash chain is deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "testx.reality.test_ledger_hash_deterministic"
TEST_TAGS = ["strict", "reality", "determinism", "ledger"]


def _run_chain() -> dict:
    from reality.ledger import (
        begin_process_accounting,
        emit_exception,
        finalize_noop_tick,
        finalize_process_accounting,
    )
    from tools.xstack.testx.tests.reality_rs2_ledger_testlib import build_policy_context

    policy_context = build_policy_context(
        "contracts.magic_relaxed",
        physics_profile_id="physics.test.magic_relaxed",
    )

    begin_process_accounting(policy_context=policy_context, process_id="process.test.chain_a")
    emit_exception(
        policy_context=policy_context,
        quantity_id="quantity.mass_energy_total",
        delta=5,
        exception_type_id="exception.creation_annihilation",
        domain_id="domain.test",
        process_id="process.test.chain_a",
        reason_code="test.chain.delta",
        evidence=["chain-a"],
    )
    first = finalize_process_accounting(
        policy_context=policy_context,
        tick=2,
        process_id="process.test.chain_a",
    )
    second = finalize_noop_tick(
        policy_context=policy_context,
        tick=3,
        process_id="process.test.chain_b",
    )
    return {
        "first": dict(first),
        "second": dict(second),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    left = _run_chain()
    right = _run_chain()

    if str((left.get("first") or {}).get("result", "")) != "complete":
        return {"status": "fail", "message": "first chain run failed before determinism check"}
    if str((right.get("first") or {}).get("result", "")) != "complete":
        return {"status": "fail", "message": "second chain run failed before determinism check"}
    if str((left.get("second") or {}).get("result", "")) != "complete":
        return {"status": "fail", "message": "first chain noop finalize failed"}
    if str((right.get("second") or {}).get("result", "")) != "complete":
        return {"status": "fail", "message": "second chain noop finalize failed"}

    left_first_hash = str((left.get("first") or {}).get("ledger_hash", ""))
    right_first_hash = str((right.get("first") or {}).get("ledger_hash", ""))
    left_second_hash = str((left.get("second") or {}).get("ledger_hash", ""))
    right_second_hash = str((right.get("second") or {}).get("ledger_hash", ""))
    if not left_first_hash or not left_second_hash:
        return {"status": "fail", "message": "deterministic chain emitted empty ledger hash"}
    if left_first_hash != right_first_hash or left_second_hash != right_second_hash:
        return {"status": "fail", "message": "ledger hash chain diverged for identical inputs"}

    left_second_prev = str(((left.get("second") or {}).get("ledger") or {}).get("previous_ledger_hash", ""))
    right_second_prev = str(((right.get("second") or {}).get("ledger") or {}).get("previous_ledger_hash", ""))
    if left_second_prev != left_first_hash or right_second_prev != right_first_hash:
        return {"status": "fail", "message": "previous_ledger_hash chain link mismatch"}
    return {"status": "pass", "message": "ledger hash chain is deterministic for repeated identical runs"}
