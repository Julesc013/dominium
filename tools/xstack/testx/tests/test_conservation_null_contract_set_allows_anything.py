"""STRICT test: contracts.null permits deterministic conservation deltas."""

from __future__ import annotations

import sys


TEST_ID = "testx.reality.test_null_contract_set_allows_anything"
TEST_TAGS = ["strict", "reality", "determinism", "ledger"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.reality.ledger import (
        begin_process_accounting,
        finalize_process_accounting,
        last_ledger_hash,
        record_unaccounted_delta,
    )
    from tools.xstack.testx.tests.reality_rs2_ledger_testlib import build_policy_context

    policy_context = build_policy_context("contracts.null", physics_profile_id="physics.test.null")
    begin_process_accounting(policy_context=policy_context, process_id="process.test.null_contract")
    record_unaccounted_delta(
        policy_context=policy_context,
        quantity_id="quantity.mass_energy_total",
        delta=77,
    )
    finalized = finalize_process_accounting(
        policy_context=policy_context,
        tick=1,
        process_id="process.test.null_contract",
    )
    if str(finalized.get("result", "")) != "complete":
        return {"status": "fail", "message": "contracts.null should not refuse unaccounted deltas"}
    ledger_hash = str(finalized.get("ledger_hash", "")).strip()
    if not ledger_hash:
        return {"status": "fail", "message": "ledger hash missing for contracts.null finalize"}
    if str(last_ledger_hash(policy_context=policy_context, shard_id="shard.0")) != ledger_hash:
        return {"status": "fail", "message": "runtime last_ledger_hash did not match finalized ledger hash"}
    return {"status": "pass", "message": "contracts.null accepted deterministic delta accounting without refusal"}
