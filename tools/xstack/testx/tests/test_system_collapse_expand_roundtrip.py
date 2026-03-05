"""FAST test: SYS0 collapse/expand roundtrip is deterministic and reversible."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_system_collapse_expand_roundtrip"
TEST_TAGS = ["fast", "system", "sys0", "determinism"]


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
        return {"status": "fail", "message": "system collapse refused unexpectedly"}

    capsule_id = str(collapse.get("capsule_id", "")).strip()
    if not capsule_id:
        return {"status": "fail", "message": "collapse returned empty capsule_id"}

    expand = execute_system_process(
        state=state,
        process_id="process.system_expand",
        inputs={"capsule_id": capsule_id},
    )
    if str(expand.get("result", "")) != "complete":
        return {"status": "fail", "message": "system expand refused unexpectedly"}

    system_rows = [dict(row) for row in list(state.get("system_rows") or []) if isinstance(row, dict)]
    if len(system_rows) != 1:
        return {"status": "fail", "message": "expected one system row after roundtrip"}
    if str(system_rows[0].get("current_tier", "")).strip() != "micro":
        return {"status": "fail", "message": "system tier did not return to micro after expand"}

    restored = sorted(
        str(row.get("assembly_id", "")).strip()
        for row in list(state.get("assembly_rows") or [])
        if isinstance(row, dict) and str(row.get("assembly_id", "")).strip().startswith("assembly.engine.")
    )
    expected = [
        "assembly.engine.generator.alpha",
        "assembly.engine.pump.alpha",
        "assembly.engine.root.alpha",
    ]
    if restored != expected:
        return {"status": "fail", "message": "restored assembly graph mismatch after collapse/expand"}

    second_state = copy.deepcopy(cloned_state())
    second_collapse = execute_system_process(
        state=second_state,
        process_id="process.system_collapse",
        inputs={"system_id": "system.engine.alpha"},
    )
    if str(second_collapse.get("result", "")) != "complete":
        return {"status": "fail", "message": "second collapse refused unexpectedly"}
    if str(second_collapse.get("capsule_id", "")).strip() != str(collapse.get("capsule_id", "")).strip():
        return {"status": "fail", "message": "collapse capsule_id diverged for equivalent inputs"}

    return {"status": "pass", "message": "system collapse/expand roundtrip deterministic"}
