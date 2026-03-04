"""FAST test: CHEM-2 process runs log energy ledger and entropy events."""

from __future__ import annotations

import sys


TEST_ID = "test_energy_and_entropy_logged"
TEST_TAGS = ["fast", "chem", "energy", "entropy"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.chem_testlib import execute_process_run_lifecycle, seed_process_run_state

    state = seed_process_run_state(entropy_value=0)
    lifecycle = execute_process_run_lifecycle(repo_root=repo_root, state=state, catalyst_present=True)
    if str((dict(lifecycle.get("tick") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process_run_tick failed"}

    run_id = str(lifecycle.get("run_id", "")).strip()
    ledger_rows = [dict(row) for row in list(state.get("energy_ledger_entries") or []) if isinstance(row, dict)]
    matching_ledger = [
        row
        for row in ledger_rows
        if str(row.get("source_id", "")).strip() == run_id
        and str(row.get("transformation_id", "")).strip() == "transform.chemical_to_thermal"
    ]
    if not matching_ledger:
        return {"status": "fail", "message": "missing transform.chemical_to_thermal energy ledger entry for process run"}

    entropy_rows = [dict(row) for row in list(state.get("entropy_event_rows") or []) if isinstance(row, dict)]
    matching_entropy = [
        row
        for row in entropy_rows
        if str(row.get("target_id", "")).strip() == run_id
        and str(row.get("source_transformation_id", "")).strip() == "transform.chemical_to_thermal"
    ]
    if not matching_entropy:
        return {"status": "fail", "message": "missing entropy_event_rows entry linked to chemical_to_thermal transform"}
    return {"status": "pass", "message": "CHEM-2 process runs log energy ledger and entropy contributions"}
