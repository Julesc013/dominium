"""FAST test: SYS-1 energy invariant must require ledger transform."""

from __future__ import annotations

import sys


TEST_ID = "test_invariant_validation_energy_requires_ledger"
TEST_TAGS = ["fast", "system", "sys1", "validation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from system import validate_boundary_invariants
    from tools.xstack.testx.tests.sys1_testlib import cloned_state, validation_payloads

    state = cloned_state()
    for row in list(state.get("system_boundary_invariant_rows") or []):
        if str((row or {}).get("invariant_id", "")).strip() != "invariant.energy_conserved":
            continue
        row["ledger_transform_required"] = False

    registries = validation_payloads(repo_root=repo_root)
    result = validate_boundary_invariants(
        system_id="system.engine.alpha",
        system_rows=state.get("system_rows") or [],
        boundary_invariant_rows=state.get("system_boundary_invariant_rows") or [],
        boundary_invariant_template_registry_payload=registries.get("boundary_invariant_template_registry_payload"),
        tolerance_policy_registry_payload=registries.get("tolerance_policy_registry_payload"),
        safety_pattern_registry_payload=registries.get("safety_pattern_registry_payload"),
    )
    if str(result.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "expected refused result when energy invariant lacks ledger transform"}
    failed = list(result.get("failed_checks") or [])
    check_ids = set(str(row.get("check_id", "")).strip() for row in failed if isinstance(row, dict))
    if "invariant.energy.requires_ledger.invariant.energy_conserved" not in check_ids:
        return {"status": "fail", "message": "missing explicit energy-ledger invariant failure check"}
    return {"status": "pass", "message": "energy invariant ledger requirement enforced"}
