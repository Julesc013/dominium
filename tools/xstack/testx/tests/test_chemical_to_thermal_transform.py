"""FAST test: CHEM-1 combustion emits transform.chemical_to_thermal ledger entries."""

from __future__ import annotations

import sys


TEST_ID = "test_chemical_to_thermal_transform"
TEST_TAGS = ["fast", "chem", "energy", "ledger"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.chem_testlib import execute_combustion_tick, seed_combustion_state

    state = seed_combustion_state(initial_fuel=1000, material_id="material.fuel_oil_stub")
    result = execute_combustion_tick(
        repo_root=repo_root,
        state=state,
        inputs={"target_id": "node.therm.source", "material_id": "material.fuel_oil_stub"},
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process.fire_tick failed: {}".format(result)}

    ledger_rows = [dict(row) for row in list(state.get("energy_ledger_entries") or []) if isinstance(row, dict)]
    transform_ids = set(
        str(row.get("transformation_id", "")).strip()
        for row in ledger_rows
        if str(row.get("transformation_id", "")).strip()
    )
    if "transform.chemical_to_thermal" not in transform_ids:
        return {"status": "fail", "message": "missing transform.chemical_to_thermal ledger entry"}

    combustion_rows = [dict(row) for row in list(state.get("combustion_event_rows") or []) if isinstance(row, dict)]
    if not combustion_rows:
        return {"status": "fail", "message": "missing combustion_event_rows after fire_tick"}
    if int(max(0, int(combustion_rows[-1].get("thermal_energy_out", 0) or 0))) <= 0:
        return {"status": "fail", "message": "combustion did not emit thermal_energy_out"}
    return {"status": "pass", "message": "combustion transform.chemical_to_thermal ledger pathway verified"}
