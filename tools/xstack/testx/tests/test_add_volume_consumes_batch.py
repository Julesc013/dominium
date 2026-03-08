"""FAST test: GEO-7 add-volume process consumes declared MAT batches deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_add_volume_consumes_batch"
TEST_TAGS = ["fast", "geo", "geometry", "materials"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo7_testlib import geometry_cell_key, geometry_cell_row, run_geometry_process, seed_geometry_state

    state = seed_geometry_state()
    state["geometry_cell_states"][0]["occupancy_fraction"] = 700
    source_batch = dict(list(state.get("material_batches") or [])[0])
    source_batch_id = str(source_batch.get("batch_id", "")).strip()
    starting_mass = int(source_batch.get("quantity_mass_raw", 0))
    result = run_geometry_process(
        state=state,
        process_id="process.geometry_add",
        inputs={
            "target_cell_keys": [geometry_cell_key([0, 0, 0])],
            "volume_amount": 100,
            "material_id": "material.stone_basic",
            "input_batch_ids": [source_batch_id],
        },
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "geometry add process did not complete"}
    if list(result.get("material_in_batch_ids") or []) != [source_batch_id]:
        return {"status": "fail", "message": "geometry add did not report consumed batch id deterministically"}
    batch_rows = {
        str(row.get("batch_id", "")).strip(): dict(row)
        for row in list(state.get("material_batches") or [])
        if isinstance(row, dict) and str(row.get("batch_id", "")).strip()
    }
    remaining = dict(batch_rows.get(source_batch_id) or {})
    if int(remaining.get("quantity_mass_raw", -1)) != int(starting_mass - 100):
        return {"status": "fail", "message": "geometry add did not consume the expected batch mass"}
    cell_row = dict(geometry_cell_row(state, [0, 0, 0]) or {})
    if int(cell_row.get("occupancy_fraction", -1)) != 800:
        return {"status": "fail", "message": "geometry add produced unexpected occupancy {}".format(cell_row.get("occupancy_fraction"))}
    return {"status": "pass", "message": "GEO-7 add-volume consumes deterministic MAT batch mass"}
