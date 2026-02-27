"""FAST test: ledger tracks mass deltas by material_id when quantity.mass is used."""

from __future__ import annotations

import sys


TEST_ID = "testx.materials.ledger_mass_tracking_by_material"
TEST_TAGS = ["fast", "materials", "ledger"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.reality.ledger import begin_process_accounting, finalize_process_accounting, record_unaccounted_delta
    from tools.xstack.testx.tests.reality_rs2_ledger_testlib import build_policy_context

    policy_context = build_policy_context(
        "contracts.default.realistic",
        physics_profile_id="physics.default.realistic",
        include_quantity_type_registry=True,
    )
    begin_process_accounting(policy_context=policy_context, process_id="process.test.material_mass")
    record_unaccounted_delta(
        policy_context=policy_context,
        quantity_id="quantity.mass",
        dimension_id="dim.mass",
        material_id="material.iron",
        delta=1024,
    )
    record_unaccounted_delta(
        policy_context=policy_context,
        quantity_id="quantity.mass",
        dimension_id="dim.mass",
        material_id="material.water",
        delta=256,
    )
    finalized = finalize_process_accounting(
        policy_context=policy_context,
        tick=19,
        process_id="process.test.material_mass",
    )
    if str(finalized.get("result", "")) != "complete":
        return {"status": "fail", "message": "ledger finalize refused for quantity.mass tracking path"}
    ledger = dict(finalized.get("ledger") or {})
    extensions = dict(ledger.get("extensions") or {})
    totals = {
        str(row.get("material_id", "")): int(row.get("net_delta", 0) or 0)
        for row in list(extensions.get("material_mass_totals") or [])
        if isinstance(row, dict)
    }
    if int(totals.get("material.iron", 0)) != 1024 or int(totals.get("material.water", 0)) != 256:
        return {"status": "fail", "message": "material mass totals mismatch in ledger extensions"}
    return {"status": "pass", "message": "ledger material mass tracking passed"}
