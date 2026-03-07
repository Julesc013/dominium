"""LOGIC-4 SENSE phase snapshot builder."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from .common import (
    active_signal_for_slot,
    as_list,
    as_map,
    default_value_ref,
    rows_by_id,
    signal_type_id_for_port,
    token,
)


def build_logic_element_index(
    *,
    graph_row: Mapping[str, object],
    logic_element_rows: object,
    logic_behavior_model_rows: object,
    interface_signature_rows: object,
    state_machine_rows: object,
) -> list[dict]:
    graph = as_map(graph_row)
    elements_by_id = rows_by_id(logic_element_rows, "element_id")
    behavior_by_id = rows_by_id(logic_behavior_model_rows, "behavior_model_id")
    interfaces_by_system = rows_by_id(interface_signature_rows, "system_id")
    state_machines_by_id = rows_by_id(state_machine_rows, "sm_id")

    by_instance: Dict[str, dict] = {}
    for node in sorted((dict(item) for item in as_list(graph.get("nodes")) if isinstance(item, Mapping)), key=lambda item: token(item.get("node_id"))):
        node_id = token(node.get("node_id"))
        payload = as_map(node.get("payload"))
        element_instance_id = token(payload.get("element_instance_id"))
        if not element_instance_id:
            continue
        port_id = token(payload.get("port_id"))
        node_kind = token(payload.get("node_kind"))
        extensions = as_map(payload.get("extensions"))
        element_definition_id = token(extensions.get("element_definition_id")) or element_instance_id
        element_row = dict(elements_by_id.get(element_definition_id) or {})
        behavior_row = dict(behavior_by_id.get(token(element_row.get("behavior_model_id"))) or {})
        interface_row = dict(interfaces_by_system.get(element_definition_id) or {})
        model_ref = as_map(behavior_row.get("model_ref"))
        state_machine_row = dict(state_machines_by_id.get(token(model_ref.get("ref_id"))) or {})
        current = by_instance.setdefault(
            element_instance_id,
            {
                "element_instance_id": element_instance_id,
                "element_definition_id": element_definition_id,
                "element_row": element_row,
                "behavior_row": behavior_row,
                "state_machine_row": state_machine_row,
                "interface_row": interface_row,
                "input_ports": {},
                "output_ports": {},
            },
        )
        if node_kind == "port_in" and port_id:
            current["input_ports"][port_id] = {"node_id": node_id, "payload": payload}
        elif node_kind == "port_out" and port_id:
            current["output_ports"][port_id] = {"node_id": node_id, "payload": payload}

    out: List[dict] = []
    for element_instance_id in sorted(by_instance.keys()):
        row = dict(by_instance[element_instance_id])
        row["input_ports"] = dict((port_id, dict(row["input_ports"][port_id])) for port_id in sorted(row["input_ports"].keys()))
        row["output_ports"] = dict((port_id, dict(row["output_ports"][port_id])) for port_id in sorted(row["output_ports"].keys()))
        out.append(row)
    return out


def build_logic_sense_snapshot(
    *,
    current_tick: int,
    network_id: str,
    graph_row: Mapping[str, object],
    signal_store_state: Mapping[str, object] | None,
    logic_element_rows: object,
    logic_behavior_model_rows: object,
    interface_signature_rows: object,
    state_machine_rows: object,
) -> dict:
    graph = as_map(graph_row)
    element_index = build_logic_element_index(
        graph_row=graph,
        logic_element_rows=logic_element_rows,
        logic_behavior_model_rows=logic_behavior_model_rows,
        interface_signature_rows=interface_signature_rows,
        state_machine_rows=state_machine_rows,
    )
    port_snapshot: Dict[str, dict] = {}
    element_inputs: Dict[str, dict] = {}
    for element in element_index:
        element_instance_id = token(element.get("element_instance_id"))
        input_rows: Dict[str, dict] = {}
        for port_id, port_row in dict(element.get("input_ports") or {}).items():
            node_id = token(as_map(port_row).get("node_id"))
            signal_type_id = signal_type_id_for_port(
                node_id=node_id,
                direction="in",
                graph_row=graph,
                element_row=as_map(element.get("element_row")),
                interface_row=as_map(element.get("interface_row")),
            )
            selected = active_signal_for_slot(
                signal_store_state=signal_store_state,
                network_id=network_id,
                element_id=element_instance_id,
                port_id=port_id,
                tick=current_tick,
            )
            value_ref = as_map(selected.get("value_ref")) if selected else default_value_ref(signal_type_id=signal_type_id)
            input_rows[port_id] = value_ref
            port_snapshot["{}::{}".format(element_instance_id, port_id)] = value_ref
        element_inputs[element_instance_id] = dict((port_id, dict(input_rows[port_id])) for port_id in sorted(input_rows.keys()))
    snapshot = {
        "schema_version": "1.0.0",
        "network_id": token(network_id),
        "tick": int(current_tick),
        "elements": element_index,
        "inputs_by_element": element_inputs,
        "port_snapshot": dict((key, dict(port_snapshot[key])) for key in sorted(port_snapshot.keys())),
    }
    snapshot["snapshot_hash"] = canonical_sha256(snapshot)
    return snapshot


__all__ = [
    "build_logic_element_index",
    "build_logic_sense_snapshot",
]
