"""FAST test: GEO-7 geometry edits emit deterministic coupling surfaces."""

from __future__ import annotations

import sys


TEST_ID = "test_coupling_updates_triggered"
TEST_TAGS = ["fast", "geo", "geometry", "coupling"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo7_testlib import geometry_cell_key, run_geometry_process, seed_geometry_state

    state = seed_geometry_state()
    result = run_geometry_process(
        state=state,
        process_id="process.geometry_remove",
        inputs={
            "target_cell_keys": [geometry_cell_key([0, 0, 0])],
            "volume_amount": 400,
        },
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "geometry remove process did not complete"}
    if int(result.get("coupling_hazard_count", 0)) <= 0:
        return {"status": "fail", "message": "geometry edit did not emit coupling hazard rows"}
    if int(result.get("coupling_flow_adjustment_count", 0)) <= 0:
        return {"status": "fail", "message": "geometry edit did not emit coupling flow adjustment rows"}
    hazard_rows = list(state.get("model_hazard_rows") or [])
    flow_rows = list(state.get("model_flow_adjustment_rows") or [])
    if not hazard_rows or not flow_rows:
        return {"status": "fail", "message": "geometry coupling surfaces were not persisted to state"}
    hazard_ext = dict(dict(hazard_rows[0]).get("extensions") or {})
    if str(hazard_ext.get("coupling_contract_id", "")).strip() != "coupling.geo_to_mech.instability_stub":
        return {"status": "fail", "message": "geometry hazard row missing MECH coupling contract id"}
    flow_contracts = {
        str(dict(row).get("extensions", {}).get("coupling_contract_id", "")).strip()
        for row in flow_rows
        if isinstance(row, dict)
    }
    if "coupling.geo_to_fluid.permeability_stub" not in flow_contracts or "coupling.geo_to_therm.conductance_stub" not in flow_contracts:
        return {"status": "fail", "message": "geometry edit did not emit both FLUID and THERM coupling contracts"}
    return {"status": "pass", "message": "GEO-7 geometry edits emit deterministic coupling surfaces"}
