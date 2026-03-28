"""FAST test: ledger refuses dimension mismatch for declared quantity types."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.ledger_dimension_mismatch_refusal"
TEST_TAGS = ["fast", "materials", "ledger"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from reality.ledger import begin_process_accounting, finalize_process_accounting, record_unaccounted_delta
    from tools.xstack.testx.tests.reality_rs2_ledger_testlib import build_policy_context

    policy_context = build_policy_context(
        "contracts.default.realistic",
        physics_profile_id="physics.default.realistic",
        include_quantity_type_registry=True,
    )
    begin_process_accounting(policy_context=policy_context, process_id="process.test.dimension_mismatch")
    record_unaccounted_delta(
        policy_context=policy_context,
        quantity_id="quantity.mass_energy_total",
        dimension_id="dim.mass",
        delta=1,
    )
    finalized = finalize_process_accounting(
        policy_context=policy_context,
        tick=7,
        process_id="process.test.dimension_mismatch",
    )
    if str(finalized.get("result", "")) != "refused":
        return {"status": "fail", "message": "expected refusal for mismatched ledger dimension"}
    if str(finalized.get("reason_code", "")) != "refusal.dimension.mismatch":
        return {"status": "fail", "message": "unexpected reason_code '{}'".format(finalized.get("reason_code", ""))}
    return {"status": "pass", "message": "ledger dimension mismatch refusal emitted"}
