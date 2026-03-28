"""FAST test: PROC-1 stable topological ordering is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_toposort_stable"
TEST_TAGS = ["fast", "proc", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from process.process_definition_validator import build_process_step_row, stable_toposort

    steps = [
        build_process_step_row(step_id="step.b", step_kind="transform", inputs=[], outputs=[], cost_units=1),
        build_process_step_row(step_id="step.a", step_kind="transform", inputs=[], outputs=[], cost_units=1),
        build_process_step_row(step_id="step.c", step_kind="transform", inputs=[], outputs=[], cost_units=1),
    ]
    edges = [
        {"from_step_id": "step.a", "to_step_id": "step.c"},
        {"from_step_id": "step.b", "to_step_id": "step.c"},
    ]
    first = stable_toposort(step_rows=steps, edge_rows=edges)
    second = stable_toposort(step_rows=list(reversed(steps)), edge_rows=list(reversed(edges)))

    if str(first.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first stable_toposort failed"}
    if str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second stable_toposort failed"}

    first_order = list(first.get("ordered_step_ids") or [])
    second_order = list(second.get("ordered_step_ids") or [])
    if first_order != second_order:
        return {"status": "fail", "message": "toposort order drifted across equivalent inputs"}
    if first_order != ["step.a", "step.b", "step.c"]:
        return {"status": "fail", "message": "unexpected stable order: {}".format(",".join(first_order))}

    return {"status": "pass", "message": "stable toposort ordering is deterministic"}
