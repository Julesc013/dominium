"""FAST test: CHEM-2 output batches include deterministic provenance links."""

from __future__ import annotations

import sys


TEST_ID = "test_batch_provenance_links"
TEST_TAGS = ["fast", "chem", "materials", "provenance"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.chem_testlib import execute_process_run_lifecycle, seed_process_run_state

    state = seed_process_run_state()
    fixture = dict(state.get("chem_test_fixture") or {})
    lifecycle = execute_process_run_lifecycle(repo_root=repo_root, state=state)
    if str((dict(lifecycle.get("tick") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process_run_tick failed"}

    run_id = str(lifecycle.get("run_id", "")).strip()
    run_rows = [dict(row) for row in list(state.get("chem_process_run_state_rows") or []) if isinstance(row, dict)]
    target_run = {}
    for row in run_rows:
        if str(row.get("run_id", "")).strip() == run_id:
            target_run = dict(row)
            break
    if not target_run:
        return {"status": "fail", "message": "run row missing after process lifecycle"}

    input_batch_ids = sorted(set(str(token).strip() for token in list(target_run.get("input_batch_ids") or []) if str(token).strip()))
    output_batch_ids = sorted(set(str(token).strip() for token in list(target_run.get("output_batch_ids") or []) if str(token).strip()))
    if not input_batch_ids:
        return {"status": "fail", "message": "run row missing input_batch_ids"}
    if not output_batch_ids:
        return {"status": "fail", "message": "run row missing output_batch_ids"}

    batch_rows = {
        str(row.get("batch_id", "")).strip(): dict(row)
        for row in list(state.get("material_batches") or [])
        if isinstance(row, dict) and str(row.get("batch_id", "")).strip()
    }
    for batch_id in output_batch_ids:
        row = dict(batch_rows.get(batch_id) or {})
        if not row:
            return {"status": "fail", "message": "output batch '{}' missing from material_batches".format(batch_id)}
        ext = dict(row.get("extensions") or {})
        if str(ext.get("reaction_id", "")).strip() != str(fixture.get("reaction_id", "")).strip():
            return {"status": "fail", "message": "output batch '{}' missing reaction_id provenance".format(batch_id)}
        if str(ext.get("equipment_id", "")).strip() != str(fixture.get("equipment_id", "")).strip():
            return {"status": "fail", "message": "output batch '{}' missing equipment_id provenance".format(batch_id)}
        if str(ext.get("run_id", "")).strip() != run_id:
            return {"status": "fail", "message": "output batch '{}' missing run_id provenance".format(batch_id)}
        ext_inputs = sorted(
            set(str(token).strip() for token in list(ext.get("input_batch_ids") or []) if str(token).strip())
        )
        if ext_inputs != input_batch_ids:
            return {"status": "fail", "message": "output batch '{}' input_batch_ids provenance mismatch".format(batch_id)}
        parents = sorted(
            set(str(token).strip() for token in list(row.get("parent_batch_ids") or []) if str(token).strip())
        )
        if parents != input_batch_ids:
            return {"status": "fail", "message": "output batch '{}' parent_batch_ids mismatch".format(batch_id)}
    return {"status": "pass", "message": "CHEM-2 output batch provenance links are complete and deterministic"}
