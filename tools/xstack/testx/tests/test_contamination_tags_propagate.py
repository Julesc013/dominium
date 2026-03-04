"""FAST test: CHEM-2 output batch quality propagates contamination tags deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_contamination_tags_propagate"
TEST_TAGS = ["fast", "chem", "quality", "contamination"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.chem_testlib import execute_process_run_lifecycle, seed_process_run_state

    contamination_tag = "contaminant.trace_sulfur"
    state = seed_process_run_state(contamination_tags=[contamination_tag])
    lifecycle = execute_process_run_lifecycle(repo_root=repo_root, state=state, catalyst_present=False)
    if str((dict(lifecycle.get("tick") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process_run_tick failed"}

    run_id = str(lifecycle.get("run_id", "")).strip()
    run_rows = [dict(row) for row in list(state.get("chem_process_run_state_rows") or []) if isinstance(row, dict)]
    target_run = {}
    for row in run_rows:
        if str(row.get("run_id", "")).strip() == run_id:
            target_run = dict(row)
            break
    output_batch_ids = list(target_run.get("output_batch_ids") or [])
    if not output_batch_ids:
        return {"status": "fail", "message": "expected output batches after process_run_tick"}

    quality_rows = {
        str(row.get("batch_id", "")).strip(): dict(row)
        for row in list(state.get("batch_quality_rows") or [])
        if isinstance(row, dict) and str(row.get("batch_id", "")).strip()
    }
    propagated = False
    for batch_id in output_batch_ids:
        row = dict(quality_rows.get(str(batch_id).strip()) or {})
        tags = sorted(set(str(tag).strip() for tag in list(row.get("contamination_tags") or []) if str(tag).strip()))
        if contamination_tag in tags:
            propagated = True
    if not propagated:
        return {"status": "fail", "message": "contamination tags were not propagated to output batch quality"}
    return {"status": "pass", "message": "output batch quality contamination tags propagated deterministically"}
