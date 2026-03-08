"""FAST test: GEO-7 excavation emits deterministic MAT debris batches."""

from __future__ import annotations

import sys


TEST_ID = "test_material_out_batch_created"
TEST_TAGS = ["fast", "geo", "geometry", "materials"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo7_testlib import geometry_cell_key, run_geometry_process, seed_geometry_state

    state = seed_geometry_state()
    before_count = len(list(state.get("material_batches") or []))
    result = run_geometry_process(
        state=state,
        process_id="process.geometry_remove",
        inputs={
            "target_cell_keys": [geometry_cell_key([0, 0, 0])],
            "volume_amount": 300,
        },
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "geometry remove process did not complete"}
    produced_batch_ids = list(result.get("material_out_batch_ids") or [])
    if not produced_batch_ids:
        return {"status": "fail", "message": "geometry remove did not report produced material_out batch ids"}
    batch_rows = {
        str(row.get("batch_id", "")).strip(): dict(row)
        for row in list(state.get("material_batches") or [])
        if isinstance(row, dict) and str(row.get("batch_id", "")).strip()
    }
    if len(batch_rows) <= before_count:
        return {"status": "fail", "message": "material batch collection did not grow after excavation"}
    produced = dict(batch_rows.get(str(produced_batch_ids[0]).strip()) or {})
    if str(produced.get("material_id", "")).strip() != "material.stone_basic":
        return {"status": "fail", "message": "excavation debris batch used unexpected material_id"}
    ext = dict(produced.get("extensions") or {})
    if str(ext.get("artifact_type_id", "")).strip() != "artifact.material_batch.geometry_edit":
        return {"status": "fail", "message": "excavation debris batch missing geometry artifact provenance"}
    return {"status": "pass", "message": "GEO-7 excavation emits deterministic MAT debris batches"}
