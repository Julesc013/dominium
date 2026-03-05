"""FAST test: STATEVEC0 expand restores internal graph state captured at collapse."""

from __future__ import annotations

import sys


TEST_ID = "test_expand_restores_internal_state"
TEST_TAGS = ["fast", "statevec", "sys", "roundtrip"]


EXPECTED_ASSEMBLY_IDS = {
    "assembly.engine.root.alpha",
    "assembly.engine.pump.alpha",
    "assembly.engine.generator.alpha",
}


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
    if str(collapse.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "collapse failed: {}".format(collapse)}

    capsule_id = str(collapse.get("capsule_id", "")).strip()
    if not capsule_id:
        return {"status": "fail", "message": "collapse result missing capsule_id"}

    expand = execute_system_process(
        state=state,
        process_id="process.system_expand",
        inputs={"capsule_id": capsule_id},
    )
    if str(expand.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "expand failed: {}".format(expand)}

    assembly_ids = {
        str(row.get("assembly_id", "")).strip()
        for row in list(state.get("assembly_rows") or [])
        if isinstance(row, dict) and str(row.get("assembly_id", "")).strip()
    }
    if not EXPECTED_ASSEMBLY_IDS.issubset(assembly_ids):
        return {
            "status": "fail",
            "message": "expanded assembly graph missing expected rows",
        }

    systems = [dict(row) for row in list(state.get("system_rows") or []) if isinstance(row, dict)]
    system_row = systems[0] if systems else {}
    if str(system_row.get("current_tier", "")).strip() != "micro":
        return {"status": "fail", "message": "system tier not restored to micro on expand"}

    return {"status": "pass", "message": "expand restores captured internal state deterministically"}
