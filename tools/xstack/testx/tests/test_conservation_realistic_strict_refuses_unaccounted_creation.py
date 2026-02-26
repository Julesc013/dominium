"""STRICT test: realistic strict contract refuses unaccounted mass-energy creation."""

from __future__ import annotations

import sys


TEST_ID = "testx.reality.test_realistic_strict_refuses_unaccounted_creation"
TEST_TAGS = ["strict", "reality", "determinism", "ledger"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.reality.ledger import (
        begin_process_accounting,
        finalize_process_accounting,
        record_unaccounted_delta,
    )
    from tools.xstack.testx.tests.reality_rs2_ledger_testlib import build_policy_context

    policy_context = build_policy_context(
        "contracts.default.realistic",
        physics_profile_id="physics.default.realistic",
    )
    begin_process_accounting(
        policy_context=policy_context,
        process_id="process.test.strict_unaccounted",
    )
    record_unaccounted_delta(
        policy_context=policy_context,
        quantity_id="quantity.mass_energy_total",
        delta=12,
    )
    finalized = finalize_process_accounting(
        policy_context=policy_context,
        tick=4,
        process_id="process.test.strict_unaccounted",
    )
    if str(finalized.get("result", "")) != "refused":
        return {"status": "fail", "message": "strict realistic contract should refuse unaccounted creation"}
    reason_code = str(finalized.get("reason_code", "")).strip()
    expected = "refusal.conservation_violation.quantity.mass_energy_total"
    if reason_code != expected:
        return {"status": "fail", "message": "unexpected refusal reason '{}'".format(reason_code)}
    if not str(finalized.get("ledger_hash", "")).strip():
        return {"status": "fail", "message": "refusal payload must include deterministic ledger_hash"}
    return {"status": "pass", "message": "strict realistic contract refused unaccounted creation as expected"}
