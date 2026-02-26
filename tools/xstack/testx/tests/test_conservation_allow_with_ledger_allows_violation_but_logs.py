"""STRICT test: allow_with_ledger permits accounted creation-annihilation deltas."""

from __future__ import annotations

import sys


TEST_ID = "testx.reality.test_allow_with_ledger_allows_violation_but_logs"
TEST_TAGS = ["strict", "reality", "determinism", "ledger"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.reality.ledger import (
        begin_process_accounting,
        emit_exception,
        finalize_process_accounting,
    )
    from tools.xstack.testx.tests.reality_rs2_ledger_testlib import build_policy_context

    policy_context = build_policy_context(
        "contracts.magic_relaxed",
        physics_profile_id="physics.test.magic_relaxed",
    )
    begin_process_accounting(policy_context=policy_context, process_id="process.test.relaxed_spawn")
    emit_exception(
        policy_context=policy_context,
        quantity_id="quantity.mass_energy_total",
        delta=33,
        exception_type_id="exception.creation_annihilation",
        domain_id="domain.test",
        process_id="process.test.relaxed_spawn",
        reason_code="test.creation",
        evidence=["spawned_test_entity"],
    )
    finalized = finalize_process_accounting(
        policy_context=policy_context,
        tick=9,
        process_id="process.test.relaxed_spawn",
    )
    if str(finalized.get("result", "")) != "complete":
        return {"status": "fail", "message": "allow_with_ledger should permit accounted creation deltas"}
    ledger = dict(finalized.get("ledger") or {})
    entries = list(ledger.get("entries") or [])
    if len(entries) != 1:
        return {"status": "fail", "message": "expected one exception ledger entry, got {}".format(len(entries))}
    entry = dict(entries[0])
    if str(entry.get("exception_type_id", "")) != "exception.creation_annihilation":
        return {"status": "fail", "message": "unexpected exception type logged for relaxed contract"}
    totals = dict((str(row.get("quantity_id", "")), int(row.get("net_delta", 0) or 0)) for row in list(ledger.get("totals") or []))
    if int(totals.get("quantity.mass_energy_total", 0)) != 33:
        return {"status": "fail", "message": "mass-energy total delta was not logged deterministically"}
    return {"status": "pass", "message": "allow_with_ledger accepted accounted violation and emitted ledger entry"}
