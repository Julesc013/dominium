"""FAST test: CHEM-1 combustion emissions are logged as pollutant rows and RECORD artifacts."""

from __future__ import annotations

import sys


TEST_ID = "test_emission_logged"
TEST_TAGS = ["fast", "chem", "emission", "logging"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.chem_testlib import execute_combustion_tick, seed_combustion_state

    state = seed_combustion_state(initial_fuel=1100, material_id="material.fuel_oil_stub")
    result = execute_combustion_tick(
        repo_root=repo_root,
        state=state,
        inputs={"target_id": "node.therm.source", "material_id": "material.fuel_oil_stub"},
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process.fire_tick failed: {}".format(result)}

    emission_rows = [dict(row) for row in list(state.get("combustion_emission_rows") or []) if isinstance(row, dict)]
    if not emission_rows:
        return {"status": "fail", "message": "missing combustion_emission_rows after burn"}
    if not any(int(max(0, int(row.get("mass_value", 0) or 0))) > 0 for row in emission_rows):
        return {"status": "fail", "message": "combustion_emission_rows did not include positive pollutant mass"}

    pollutant_rows = [dict(row) for row in list(state.get("pollutant_species_pool_rows") or []) if isinstance(row, dict)]
    if not pollutant_rows:
        return {"status": "fail", "message": "missing pollutant_species_pool_rows after emission"}
    if not any(str(row.get("material_id", "")).strip() == "material.pollutant_coarse_stub" for row in pollutant_rows):
        return {"status": "fail", "message": "pollutant species pool missing material.pollutant_coarse_stub"}

    info_rows = [dict(row) for row in list(state.get("info_artifact_rows") or []) if isinstance(row, dict)]
    if not any(
        str((dict(row.get("extensions") or {})).get("artifact_type_id", "")).strip() == "artifact.record.combustion_emission"
        for row in info_rows
    ):
        return {"status": "fail", "message": "missing combustion emission RECORD artifact"}
    return {"status": "pass", "message": "combustion emissions logged and pooled for POLL hook"}
