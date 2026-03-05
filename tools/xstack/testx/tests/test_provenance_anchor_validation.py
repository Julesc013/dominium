"""FAST test: SYS0 expand refuses deterministically when provenance anchor mismatches."""

from __future__ import annotations

import sys


TEST_ID = "test_provenance_anchor_validation"
TEST_TAGS = ["fast", "system", "sys0", "provenance"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys0_testlib import cloned_state, execute_system_process

    state = cloned_state()
    collapse = execute_system_process(
        state=state,
        process_id="process.system_collapse",
        inputs={"system_id": "system.engine.alpha"},
    )
    if str(collapse.get("result", "")) != "complete":
        return {"status": "fail", "message": "collapse refused unexpectedly in provenance test"}

    capsule_id = str(collapse.get("capsule_id", "")).strip()
    state_vector_rows = list(state.get("system_state_vector_rows") or [])
    if not state_vector_rows:
        return {"status": "fail", "message": "collapse produced no system_state_vector_rows"}

    # Deliberately tamper with serialized state to break provenance anchor validation.
    first_row = dict(state_vector_rows[0])
    serialized = dict(first_row.get("serialized_internal_state") or {})
    assembly_rows = [dict(row) for row in list(serialized.get("assembly_rows") or []) if isinstance(row, dict)]
    if not assembly_rows:
        return {"status": "fail", "message": "serialized state has no assembly_rows to tamper"}
    assembly_rows[0]["assembly_type_id"] = "assembly.tampered.type"
    serialized["assembly_rows"] = assembly_rows
    first_row["serialized_internal_state"] = serialized
    state["system_state_vector_rows"] = [first_row] + [dict(row) for row in state_vector_rows[1:]]

    expand = execute_system_process(
        state=state,
        process_id="process.system_expand",
        inputs={"capsule_id": capsule_id},
    )
    if str(expand.get("result", "")) != "refused":
        return {"status": "fail", "message": "expand should refuse on provenance anchor mismatch"}
    reason_code = str((expand.get("refusal") or {}).get("reason_code", "")).strip()
    if reason_code != "REFUSAL_SYSTEM_EXPAND_HASH_MISMATCH":
        return {"status": "fail", "message": "unexpected refusal code for anchor mismatch"}

    return {"status": "pass", "message": "provenance anchor mismatch refusal deterministic"}
