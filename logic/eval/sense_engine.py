"""LOGIC-4/8 SENSE phase snapshot builder."""

from __future__ import annotations

from typing import Dict, List, Mapping

from logic.fault import apply_faults_to_signal_value, select_active_logic_fault_rows
from logic.noise import apply_noise_policy_to_value, logic_noise_policy_rows_by_id
from meta.explain import build_explain_artifact
from tools.xstack.compatx.canonical_json import canonical_sha256

from .common import (
    active_signal_for_slot,
    as_int,
    as_list,
    as_map,
    canon,
    default_value_ref,
    rows_by_id,
    signal_type_id_for_port,
    token,
)
from .runtime_state import build_logic_noise_decision_row, build_logic_security_fail_row


def _logic_security_policy_rows_by_id(payload: Mapping[str, object] | None) -> dict:
    body = as_map(payload)
    rows = body.get("logic_security_policies")
    if not isinstance(rows, list):
        rows = body.get("security_policies")
    if not isinstance(rows, list):
        record = as_map(body.get("record"))
        rows = record.get("logic_security_policies")
        if not isinstance(rows, list):
            rows = record.get("security_policies")
    return rows_by_id(rows or [], "security_policy_id")


def _incoming_edges_by_target_node(graph_row: Mapping[str, object]) -> Dict[str, list[dict]]:
    graph = as_map(graph_row)
    out: Dict[str, list[dict]] = {}
    for edge in sorted((dict(item) for item in as_list(graph.get("edges")) if isinstance(item, Mapping)), key=lambda item: token(item.get("edge_id"))):
        target_node_id = token(edge.get("to_node_id"))
        if not target_node_id:
            continue
        out.setdefault(target_node_id, []).append(edge)
    return dict((node_id, [dict(row) for row in out[node_id]]) for node_id in sorted(out.keys()))


def _field_modifier_stubs(evaluation_request: Mapping[str, object] | None) -> dict:
    request = as_map(evaluation_request)
    extensions = as_map(request.get("extensions"))
    return as_map(extensions.get("field_modifier_stubs"))


def _security_context(signal_row: Mapping[str, object]) -> dict:
    row = as_map(signal_row)
    value_ref = as_map(row.get("value_ref"))
    return {
        **as_map(value_ref.get("receipt_metadata")),
        **as_map(as_map(row.get("extensions")).get("security_context")),
    }


def _credential_type_allowed(security_policy_row: Mapping[str, object], security_context: Mapping[str, object]) -> bool:
    allowed = [token(item) for item in as_list(security_policy_row.get("allowed_credential_types")) if token(item)]
    if not allowed:
        return True
    return token(as_map(security_context).get("credential_type")) in set(allowed)


def _security_policy_for_incoming_edges(edges: object) -> tuple[str, dict]:
    selected_id = "sec.none"
    selected_edge = {}
    for edge in sorted((dict(item) for item in as_list(edges) if isinstance(item, Mapping)), key=lambda item: token(item.get("edge_id"))):
        payload = as_map(edge.get("payload"))
        extensions = as_map(payload.get("extensions"))
        security_policy_id = token(extensions.get("security_policy_id")) or "sec.none"
        if security_policy_id != "sec.none":
            return security_policy_id, edge
    return selected_id, selected_edge


def _noise_policy_id_for_incoming_edges(edges: object) -> str:
    for edge in sorted((dict(item) for item in as_list(edges) if isinstance(item, Mapping)), key=lambda item: token(item.get("edge_id"))):
        payload = as_map(edge.get("payload"))
        noise_policy_id = token(payload.get("noise_policy_id"))
        if noise_policy_id:
            return noise_policy_id
    return "noise.none"


def _security_gate(
    *,
    current_tick: int,
    network_id: str,
    signal_type_id: str,
    selected_signal_row: Mapping[str, object] | None,
    security_policy_row: Mapping[str, object] | None,
    security_policy_id: str,
    edge_row: Mapping[str, object] | None,
) -> dict:
    row = as_map(selected_signal_row)
    policy = as_map(security_policy_row)
    if security_policy_id == "sec.none" or not row or not policy:
        return {
            "result": "complete",
            "value_ref": as_map(row.get("value_ref")),
            "security_fail_row": {},
            "explain_artifact_rows": [],
        }
    context = _security_context(row)
    verified = bool(context.get("authenticated", False) or context.get("credential_verified", False))
    if token(context.get("verification_state")).lower() == "verified":
        verified = True
    encrypted = bool(context.get("encrypted", False))
    credential_allowed = _credential_type_allowed(policy, context)
    reason = ""
    if bool(policy.get("requires_auth", False)) and (not verified or not credential_allowed):
        reason = "auth_required"
    elif bool(policy.get("requires_encryption", False)) and not encrypted:
        reason = "encryption_required"
    if not reason:
        return {
            "result": "complete",
            "value_ref": as_map(row.get("value_ref")),
            "security_fail_row": {},
            "explain_artifact_rows": [],
        }
    security_fail_row = build_logic_security_fail_row(
        tick=current_tick,
        network_id=network_id,
        edge_id=token(as_map(edge_row).get("edge_id")),
        security_policy_id=security_policy_id,
        reason=reason,
        signal_id=token(row.get("signal_id")) or None,
        extensions={
            "verification_state": token(context.get("verification_state")),
            "credential_type": token(context.get("credential_type")) or None,
            "encrypted": bool(context.get("encrypted", False)),
        },
    )
    explain = build_explain_artifact(
        explain_id="explain.logic_spoof_detected.{}".format(
            canonical_sha256(
                {
                    "tick": int(max(0, as_int(current_tick, 0))),
                    "network_id": token(network_id),
                    "edge_id": token(as_map(edge_row).get("edge_id")),
                    "security_policy_id": security_policy_id,
                    "reason": reason,
                }
            )[:16]
        ),
        event_id=token(security_fail_row.get("event_id")),
        target_id=token(network_id),
        cause_chain=["cause.logic.security_policy"],
        remediation_hints=["provide the required credentials or encryption for this protocol link"],
        extensions={
            "event_kind_id": "explain.logic_spoof_detected",
            "security_policy_id": security_policy_id,
            "edge_id": token(as_map(edge_row).get("edge_id")),
            "signal_id": token(row.get("signal_id")) or None,
            "reason": reason,
        },
    )
    return {
        "result": "refused",
        "value_ref": default_value_ref(signal_type_id=signal_type_id),
        "security_fail_row": security_fail_row,
        "explain_artifact_rows": [explain],
    }


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
    logic_fault_state_rows: object = None,
    logic_noise_policy_registry_payload: Mapping[str, object] | None = None,
    logic_security_policy_registry_payload: Mapping[str, object] | None = None,
    evaluation_request: Mapping[str, object] | None = None,
) -> dict:
    graph = as_map(graph_row)
    request = as_map(evaluation_request)
    request_extensions = as_map(request.get("extensions"))
    field_modifier_stubs = _field_modifier_stubs(request)
    allow_named_rng_noise = bool(request_extensions.get("allow_named_rng_noise", False))
    allow_roi_bounce = bool(request_extensions.get("allow_roi_bounce", False))
    noise_policy_rows = logic_noise_policy_rows_by_id(logic_noise_policy_registry_payload)
    security_policy_rows = _logic_security_policy_rows_by_id(logic_security_policy_registry_payload)
    incoming_edges_by_target_node = _incoming_edges_by_target_node(graph)
    element_index = build_logic_element_index(
        graph_row=graph,
        logic_element_rows=logic_element_rows,
        logic_behavior_model_rows=logic_behavior_model_rows,
        interface_signature_rows=interface_signature_rows,
        state_machine_rows=state_machine_rows,
    )
    port_snapshot: Dict[str, dict] = {}
    element_inputs: Dict[str, dict] = {}
    applied_fault_rows: List[dict] = []
    explain_artifact_rows: List[dict] = []
    safety_event_rows: List[dict] = []
    logic_noise_decision_rows: List[dict] = []
    logic_security_fail_rows: List[dict] = []
    requires_l2_timing = False
    snapshot_refused = False
    snapshot_reason_codes: List[str] = []
    for element in element_index:
        element_instance_id = token(element.get("element_instance_id"))
        input_rows: Dict[str, dict] = {}
        for port_id, port_row in sorted(dict(element.get("input_ports") or {}).items(), key=lambda item: token(item[0])):
            port_payload = as_map(port_row)
            node_id = token(port_payload.get("node_id"))
            signal_type_id = signal_type_id_for_port(
                node_id=node_id,
                direction="in",
                graph_row=graph,
                element_row=as_map(element.get("element_row")),
                interface_row=as_map(element.get("interface_row")),
            )
            incoming_edges = list(incoming_edges_by_target_node.get(node_id) or [])
            selected_signal_row = active_signal_for_slot(
                signal_store_state=signal_store_state,
                network_id=network_id,
                element_id=element_instance_id,
                port_id=port_id,
                tick=current_tick,
            )
            value_ref = as_map(selected_signal_row.get("value_ref")) if selected_signal_row else default_value_ref(signal_type_id=signal_type_id)

            security_policy_id, security_edge_row = _security_policy_for_incoming_edges(incoming_edges)
            security_policy_row = dict(security_policy_rows.get(security_policy_id) or {})
            security_gate = _security_gate(
                current_tick=current_tick,
                network_id=network_id,
                signal_type_id=signal_type_id,
                selected_signal_row=selected_signal_row,
                security_policy_row=security_policy_row,
                security_policy_id=security_policy_id,
                edge_row=security_edge_row,
            )
            if security_gate.get("security_fail_row"):
                logic_security_fail_rows.append(dict(security_gate.get("security_fail_row") or {}))
            explain_artifact_rows.extend(
                [dict(row) for row in as_list(security_gate.get("explain_artifact_rows")) if isinstance(row, Mapping)]
            )
            value_ref = as_map(security_gate.get("value_ref")) or value_ref

            target_refs = [("element", element_instance_id), ("node", node_id)]
            target_refs.extend(("edge", token(row.get("edge_id"))) for row in incoming_edges if token(row.get("edge_id")))
            active_fault_rows = select_active_logic_fault_rows(
                logic_fault_state_rows=logic_fault_state_rows,
                target_refs=target_refs,
                current_tick=current_tick,
                field_modifier_stubs=field_modifier_stubs,
            )
            adjusted_fault_rows = []
            magnetic_flux = int(max(0, as_int(field_modifier_stubs.get("field.magnetic_flux_stub"), 0)))
            for row in active_fault_rows:
                current_fault = dict(row)
                if token(current_fault.get("fault_kind_id")) == "fault.threshold_drift" and magnetic_flux > 0:
                    parameters = dict(as_map(current_fault.get("parameters")))
                    parameters["delta_fixed"] = int(as_int(parameters.get("delta_fixed"), 0) + magnetic_flux)
                    current_fault["parameters"] = parameters
                adjusted_fault_rows.append(current_fault)
            fault_result = apply_faults_to_signal_value(
                current_tick=current_tick,
                network_id=network_id,
                signal_type_id=signal_type_id,
                base_value_ref=value_ref,
                active_fault_rows=adjusted_fault_rows,
                allow_roi_bounce=allow_roi_bounce,
            )
            if token(fault_result.get("result")) != "complete":
                snapshot_refused = True
                if token(fault_result.get("reason_code")):
                    snapshot_reason_codes.append(token(fault_result.get("reason_code")))
            applied_fault_rows.extend(
                [dict(row) for row in as_list(fault_result.get("applied_fault_rows")) if isinstance(row, Mapping)]
            )
            explain_artifact_rows.extend(
                [dict(row) for row in as_list(fault_result.get("explain_artifact_rows")) if isinstance(row, Mapping)]
            )
            safety_event_rows.extend(
                [dict(row) for row in as_list(fault_result.get("safety_event_rows")) if isinstance(row, Mapping)]
            )
            requires_l2_timing = bool(requires_l2_timing or fault_result.get("requires_l2_timing", False))
            value_ref = as_map(fault_result.get("value_ref")) or value_ref

            noise_policy_id = _noise_policy_id_for_incoming_edges(incoming_edges) or token(as_map(as_map(selected_signal_row or {}).get("extensions")).get("noise_policy_id")) or "noise.none"
            noise_policy_row = dict(noise_policy_rows.get(noise_policy_id) or noise_policy_rows.get("noise.none") or {})
            noise_result = apply_noise_policy_to_value(
                current_tick=current_tick,
                network_id=network_id,
                element_id=element_instance_id,
                port_id=port_id,
                signal_type_id=signal_type_id,
                value_ref=value_ref,
                noise_policy_row=noise_policy_row,
                allow_named_rng=allow_named_rng_noise,
                field_modifier_stubs=field_modifier_stubs,
            )
            noise_decision = build_logic_noise_decision_row(
                tick=as_int(as_map(noise_result.get("decision_row")).get("tick"), current_tick),
                network_id=token(as_map(noise_result.get("decision_row")).get("network_id")) or network_id,
                slot_key_value=token(as_map(noise_result.get("decision_row")).get("slot_key")),
                noise_policy_id=token(as_map(noise_result.get("decision_row")).get("noise_policy_id")) or noise_policy_id,
                signal_type_id=token(as_map(noise_result.get("decision_row")).get("signal_type_id")) or signal_type_id,
                reason=token(as_map(noise_result.get("decision_row")).get("reason")) or "none",
                input_value_hash=token(as_map(noise_result.get("decision_row")).get("input_value_hash")),
                output_value_hash=token(as_map(noise_result.get("decision_row")).get("output_value_hash")),
                decision_id=token(as_map(noise_result.get("decision_row")).get("decision_id")),
                rng_stream_name=(None if as_map(noise_result.get("decision_row")).get("rng_stream_name") is None else token(as_map(noise_result.get("decision_row")).get("rng_stream_name")) or None),
                rng_seed_hash=(None if as_map(noise_result.get("decision_row")).get("rng_seed_hash") is None else token(as_map(noise_result.get("decision_row")).get("rng_seed_hash")) or None),
                extensions=as_map(as_map(noise_result.get("decision_row")).get("extensions")),
            )
            if noise_decision:
                logic_noise_decision_rows.append(noise_decision)
                if token(noise_decision.get("reason")) not in {"none", "named_rng_blocked"} and token(noise_decision.get("input_value_hash")) != token(noise_decision.get("output_value_hash")):
                    explain_artifact_rows.append(
                        build_explain_artifact(
                            explain_id="explain.logic_noise_effect.{}".format(
                                canonical_sha256(
                                    {
                                        "tick": int(max(0, as_int(current_tick, 0))),
                                        "network_id": network_id,
                                        "slot_key": token(noise_decision.get("slot_key")),
                                    }
                                )[:16]
                            ),
                            event_id="event.logic.noise_effect.{}".format(
                                canonical_sha256(
                                    {
                                        "tick": int(max(0, as_int(current_tick, 0))),
                                        "network_id": network_id,
                                        "slot_key": token(noise_decision.get("slot_key")),
                                    }
                                )[:16]
                            ),
                            target_id=network_id,
                            cause_chain=["cause.logic.noise_policy"],
                            remediation_hints=["adjust the active noise policy or shield the affected carrier path"],
                            extensions={
                                "event_kind_id": "explain.logic_noise_effect",
                                "noise_policy_id": token(noise_decision.get("noise_policy_id")),
                                "slot_key": token(noise_decision.get("slot_key")),
                            },
                        )
                    )
            value_ref = as_map(noise_result.get("value_ref")) or value_ref

            input_rows[port_id] = canon(value_ref)
            port_snapshot["{}::{}".format(element_instance_id, port_id)] = canon(value_ref)
        element_inputs[element_instance_id] = dict((port_id, dict(input_rows[port_id])) for port_id in sorted(input_rows.keys()))
    snapshot = {
        "schema_version": "1.0.0",
        "network_id": token(network_id),
        "tick": int(current_tick),
        "elements": element_index,
        "inputs_by_element": element_inputs,
        "port_snapshot": dict((key, dict(port_snapshot[key])) for key in sorted(port_snapshot.keys())),
        "applied_fault_rows": applied_fault_rows,
        "logic_noise_decision_rows": logic_noise_decision_rows,
        "logic_security_fail_rows": logic_security_fail_rows,
        "requires_l2_timing": bool(requires_l2_timing),
        "result": "refused" if snapshot_refused else "complete",
        "reason_code": token(snapshot_reason_codes[0]) if snapshot_reason_codes else "",
    }
    snapshot["snapshot_hash"] = canonical_sha256(snapshot)
    snapshot["explain_artifact_rows"] = [
        dict(row)
        for row in sorted(
            (dict(item) for item in explain_artifact_rows if isinstance(item, Mapping)),
            key=lambda item: (token(item.get("artifact_id") or item.get("explain_id")), canonical_sha256(canon(item))),
        )
    ]
    snapshot["safety_event_rows"] = [
        dict(row)
        for row in sorted(
            (dict(item) for item in safety_event_rows if isinstance(item, Mapping)),
            key=lambda item: (as_int(item.get("tick"), 0), token(item.get("event_id"))),
        )
    ]
    return snapshot


__all__ = [
    "build_logic_element_index",
    "build_logic_sense_snapshot",
]
