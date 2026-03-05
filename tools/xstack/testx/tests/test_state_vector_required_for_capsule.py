"""FAST test: STATEVEC0 collapse emits required explicit state-vector payload for capsules."""

from __future__ import annotations

import sys


TEST_ID = "test_state_vector_required_for_capsule"
TEST_TAGS = ["fast", "statevec", "sys", "capsule"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys0_testlib import cloned_state, execute_system_process

    state = cloned_state()
    result = execute_system_process(
        state=state,
        process_id="process.system_collapse",
        inputs={"system_id": "system.engine.alpha"},
    )
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "system collapse failed: {}".format(result)}

    capsule_rows = [dict(row) for row in list(state.get("system_macro_capsule_rows") or []) if isinstance(row, dict)]
    if not capsule_rows:
        return {"status": "fail", "message": "collapse produced no macro capsule rows"}
    capsule = capsule_rows[0]
    internal_state = dict(capsule.get("internal_state_vector") or {})
    if not str(internal_state.get("state_vector_id", "")).strip():
        return {"status": "fail", "message": "capsule internal_state_vector missing state_vector_id"}
    if not str(internal_state.get("snapshot_id", "")).strip():
        return {"status": "fail", "message": "capsule internal_state_vector missing snapshot_id"}
    if not str(internal_state.get("owner_id", "")).strip().startswith("system."):
        return {"status": "fail", "message": "capsule internal_state_vector missing owner_id"}

    if not list(state.get("state_vector_definition_rows") or []):
        return {"status": "fail", "message": "state_vector_definition_rows missing after collapse"}
    if not list(state.get("state_vector_snapshot_rows") or []):
        return {"status": "fail", "message": "state_vector_snapshot_rows missing after collapse"}

    return {"status": "pass", "message": "collapse emits explicit state vector state for capsules"}
