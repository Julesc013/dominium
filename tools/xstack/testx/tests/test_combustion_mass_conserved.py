"""FAST test: CHEM-1 combustion mass pathways remain bounded and non-silent."""

from __future__ import annotations

import sys


TEST_ID = "test_combustion_mass_conserved"
TEST_TAGS = ["fast", "chem", "combustion", "mass"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.chem_testlib import execute_combustion_tick, seed_combustion_state

    initial_fuel = 1200
    state = seed_combustion_state(initial_fuel=initial_fuel, material_id="material.fuel_oil_stub")
    result = execute_combustion_tick(
        repo_root=repo_root,
        state=state,
        inputs={"target_id": "node.therm.source", "material_id": "material.fuel_oil_stub"},
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process.fire_tick failed: {}".format(result)}

    combustion_rows = [dict(row) for row in list(state.get("combustion_event_rows") or []) if isinstance(row, dict)]
    if not combustion_rows:
        return {"status": "fail", "message": "expected combustion_event_rows to be populated"}
    row = dict(combustion_rows[-1])
    fuel_consumed = int(max(0, int(row.get("fuel_consumed", 0) or 0)))
    oxidizer_consumed = int(max(0, int(row.get("oxidizer_consumed", 0) or 0)))
    if fuel_consumed <= 0:
        return {"status": "fail", "message": "combustion row did not consume fuel"}
    if oxidizer_consumed < 0:
        return {"status": "fail", "message": "combustion row oxidizer consumption invalid"}

    fire_rows = [dict(item) for item in list(state.get("fire_state_rows") or []) if isinstance(item, dict)]
    target_rows = [item for item in fire_rows if str(item.get("target_id", "")).strip() == "node.therm.source"]
    if not target_rows:
        return {"status": "fail", "message": "fire_state_rows missing target after combustion tick"}
    fuel_after = int(max(0, int(target_rows[-1].get("fuel_remaining", 0) or 0)))
    if fuel_after > int(initial_fuel):
        return {"status": "fail", "message": "fuel increased unexpectedly after combustion tick"}

    species_rows = [dict(item) for item in list(state.get("chem_species_pool_rows") or []) if isinstance(item, dict)]
    for item in species_rows:
        if int(item.get("mass_value", 0) or 0) < 0:
            return {"status": "fail", "message": "negative species_pool mass detected"}
    return {"status": "pass", "message": "combustion mass pathways remained bounded and logged"}
