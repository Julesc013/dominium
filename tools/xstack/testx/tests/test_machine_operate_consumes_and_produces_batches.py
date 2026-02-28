"""FAST test: machine operate consumes input batches and produces output batches."""

from __future__ import annotations

import sys


TEST_ID = "test_machine_operate_consumes_and_produces_batches"
TEST_TAGS = ["fast", "materials", "interaction", "machine"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.machine_testlib import authority_context, base_state, law_profile, policy_context, with_machine

    state = with_machine(base_state())
    state["machine_ports"] = [
        {
            "schema_version": "1.0.0",
            "port_id": "port.sawmill.input",
            "machine_id": "machine.sawmill.alpha",
            "parent_structure_id": None,
            "port_type_id": "port.material_in",
            "accepted_material_tags": [],
            "accepted_material_ids": ["material.wood_basic"],
            "capacity_mass": 2000,
            "current_contents": [
                {"batch_id": "batch.log.001", "material_id": "material.wood_basic", "mass": 1000}
            ],
            "connected_to": None,
            "visibility_policy_id": "visibility.default",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "port_id": "port.sawmill.output",
            "machine_id": "machine.sawmill.alpha",
            "parent_structure_id": None,
            "port_type_id": "port.material_out",
            "accepted_material_tags": [],
            "accepted_material_ids": [],
            "capacity_mass": 2000,
            "current_contents": [],
            "connected_to": None,
            "visibility_policy_id": "visibility.default",
            "extensions": {},
        },
    ]
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.test.machine.operate.001",
            "process_id": "process.machine_operate",
            "inputs": {
                "machine_id": "machine.sawmill.alpha",
                "operation_id": "op.saw_planks",
            },
        },
        law_profile=law_profile(["process.machine_operate"]),
        authority_context=authority_context(["entitlement.tool.operating"], privilege_level="operator"),
        navigation_indices={},
        policy_context=policy_context(),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.machine_operate refused unexpectedly"}

    ports = sorted(
        [dict(row) for row in list(state.get("machine_ports") or []) if isinstance(row, dict)],
        key=lambda row: str(row.get("port_id", "")),
    )
    input_port = dict(ports[0])
    output_port = dict(ports[1])
    if list(input_port.get("current_contents") or []):
        return {"status": "fail", "message": "machine input port should be consumed"}
    output_rows = list(output_port.get("current_contents") or [])
    if len(output_rows) != 1:
        return {"status": "fail", "message": "machine output port should receive one produced batch row"}
    out_row = dict(output_rows[0] or {})
    if str(out_row.get("material_id", "")).strip() != "material.wood_basic":
        return {"status": "fail", "message": "machine output material mismatch"}
    if int(out_row.get("mass", 0) or 0) != 1000:
        return {"status": "fail", "message": "machine output mass mismatch"}
    if not str(out_row.get("batch_id", "")).startswith("batch.machine."):
        return {"status": "fail", "message": "machine output batch id must be deterministic"}
    events = [dict(row) for row in list(state.get("machine_provenance_events") or []) if isinstance(row, dict)]
    event_types = sorted(str(row.get("event_type_id", "")).strip() for row in events)
    if "event.batch_created" not in event_types:
        return {"status": "fail", "message": "machine operation should emit event.batch_created provenance row"}
    return {"status": "pass", "message": "machine operate consumption/output behavior verified"}

