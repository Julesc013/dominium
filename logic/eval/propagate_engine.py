"""LOGIC-4 PROPAGATE phase helpers."""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from models import constitutive_model_rows_by_id, model_type_rows_by_id
from engine.time import evaluate_time_mappings
from logic.protocol import build_protocol_frame_from_delivery, normalize_protocol_frame_rows

from .common import as_int, as_list, as_map, slot_key, token
from .runtime_state import (
    build_logic_pending_signal_update_row,
    build_logic_propagation_trace_artifact_row,
    normalize_logic_pending_signal_update_rows,
    normalize_logic_propagation_trace_artifact_rows,
)


def _registry_rows(payload: Mapping[str, object] | None, key: str) -> list[dict]:
    body = as_map(payload)
    rows = body.get(key)
    if not isinstance(rows, list):
        rows = as_map(body.get("record")).get(key)
    return [dict(item) for item in list(rows or []) if isinstance(item, Mapping)]


def _registry_rows_by_id(payload: Mapping[str, object] | None, key: str, id_key: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted(_registry_rows(payload, key), key=lambda item: token(item.get(id_key))):
        row_id = token(row.get(id_key))
        if row_id:
            out[row_id] = dict(row)
    return dict((name, dict(out[name])) for name in sorted(out.keys()))


def _select_time_mapping_rows(
    *,
    time_mapping_registry_payload: Mapping[str, object] | None,
    mapping_id: str,
    temporal_domain_id: str,
) -> list[dict]:
    mapping_rows = _registry_rows(time_mapping_registry_payload, "time_mappings")
    if mapping_id:
        selected = [dict(row) for row in mapping_rows if token(row.get("mapping_id")) == token(mapping_id)]
        if selected:
            return selected
    if temporal_domain_id:
        selected = [dict(row) for row in mapping_rows if token(row.get("to_domain_id")) == token(temporal_domain_id)]
        if selected:
            return selected
    return [dict(mapping_rows[0])] if mapping_rows else []


def _resolve_delay_resolution(
    *,
    current_tick: int,
    network_id: str,
    delay_policy_id: str,
    edge_payload: Mapping[str, object],
    temporal_domain_registry_payload: Mapping[str, object] | None = None,
    time_mapping_registry_payload: Mapping[str, object] | None = None,
    drift_policy_registry_payload: Mapping[str, object] | None = None,
    model_type_registry_payload: Mapping[str, object] | None = None,
    constitutive_model_registry_payload: Mapping[str, object] | None = None,
    session_scope_id: str = "session.default",
) -> dict:
    policy_id = token(delay_policy_id)
    extensions = as_map(edge_payload.get("extensions"))
    if policy_id == "delay.fixed_ticks":
        delay_ticks = int(max(1, as_int(extensions.get("fixed_ticks", extensions.get("delay_ticks", 1)), 1)))
        return {"deliver_delay_ticks": delay_ticks, "resolution_trace": {"delay_policy_id": policy_id}}
    if policy_id == "delay.temporal_domain":
        delay_ticks = int(max(1, as_int(extensions.get("temporal_delay_ticks", extensions.get("delay_ticks", 1)), 1)))
        temporal_domain_id = token(extensions.get("temporal_domain_id")) or "time.civil"
        mapping_id = token(extensions.get("time_mapping_id"))
        temp_report = {}
        selected_mappings = _select_time_mapping_rows(
            time_mapping_registry_payload=time_mapping_registry_payload,
            mapping_id=mapping_id,
            temporal_domain_id=temporal_domain_id,
        )
        if temporal_domain_registry_payload and constitutive_model_registry_payload and selected_mappings:
            temp_report = evaluate_time_mappings(
                current_tick=int(max(0, as_int(current_tick, 0))),
                time_mapping_rows=selected_mappings,
                temporal_domain_rows=_registry_rows(temporal_domain_registry_payload, "temporal_domains"),
                model_rows=list(constitutive_model_rows_by_id(constitutive_model_registry_payload).values()),
                model_type_rows=model_type_rows_by_id(model_type_registry_payload),
                drift_policy_rows=_registry_rows(drift_policy_registry_payload, "drift_policies"),
                scope_rows_by_selector={
                    "global": ["global"],
                    "per_session": [token(session_scope_id) or "session.default"],
                    "per_assembly": [token(network_id) or "logic.network"],
                    "per_spatial": [],
                },
                session_id=token(session_scope_id) or "session.default",
                max_cost_units=int(max(1, as_int(extensions.get("time_mapping_cost_units", 2), 2))),
            )
        return {
            "deliver_delay_ticks": delay_ticks,
            "resolution_trace": {
                "delay_policy_id": policy_id,
                "temporal_domain_id": temporal_domain_id,
                "time_mapping_id": token(selected_mappings[0].get("mapping_id")) if selected_mappings else None,
                "temp_fingerprint": token(temp_report.get("deterministic_fingerprint")),
                "time_mapping_hash_chain": token(temp_report.get("time_mapping_hash_chain")),
                "temp_cost_units": int(max(0, as_int(temp_report.get("cost_units", 0), 0))),
            },
        }
    if policy_id == "delay.sig_delivery":
        delay_ticks = int(max(1, as_int(extensions.get("sig_delivery_ticks", extensions.get("delay_ticks", 1)), 1)))
        return {"deliver_delay_ticks": delay_ticks, "resolution_trace": {"delay_policy_id": policy_id}}
    return {"deliver_delay_ticks": 1, "resolution_trace": {"delay_policy_id": "delay.none"}}


def _node_payload_by_id(graph_row: Mapping[str, object]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for node in sorted((dict(item) for item in as_list(as_map(graph_row).get("nodes")) if isinstance(item, Mapping)), key=lambda item: token(item.get("node_id"))):
        out[token(node.get("node_id"))] = as_map(node.get("payload"))
    return out


def _edge_rows_from_node(graph_row: Mapping[str, object]) -> Dict[str, list[dict]]:
    out: Dict[str, list[dict]] = {}
    for edge in sorted((dict(item) for item in as_list(as_map(graph_row).get("edges")) if isinstance(item, Mapping)), key=lambda item: (token(item.get("from_node_id")), token(item.get("to_node_id")), token(item.get("edge_id")))):
        out.setdefault(token(edge.get("from_node_id")), []).append(edge)
    return out


def _route_output_targets(
    *,
    current_tick: int,
    network_id: str,
    graph_row: Mapping[str, object],
    from_node_id: str,
    temporal_domain_registry_payload: Mapping[str, object] | None = None,
    time_mapping_registry_payload: Mapping[str, object] | None = None,
    drift_policy_registry_payload: Mapping[str, object] | None = None,
    model_type_registry_payload: Mapping[str, object] | None = None,
    constitutive_model_registry_payload: Mapping[str, object] | None = None,
    session_scope_id: str = "session.default",
) -> list[dict]:
    node_payloads = _node_payload_by_id(graph_row)
    outgoing_edges = _edge_rows_from_node(graph_row)
    queue = deque([(token(from_node_id), [], 0, [])])
    visited: set[tuple[str, tuple[str, ...]]] = set()
    deliveries: List[dict] = []
    while queue:
        node_id, edge_path, delay_accumulated, delay_trace = queue.popleft()
        visit_key = (node_id, tuple(token(row.get("edge_id")) for row in edge_path))
        if visit_key in visited:
            continue
        visited.add(visit_key)
        for edge in outgoing_edges.get(node_id, []):
            payload = as_map(edge.get("payload"))
            next_node_id = token(edge.get("to_node_id"))
            resolution = _resolve_delay_resolution(
                current_tick=current_tick,
                network_id=network_id,
                delay_policy_id=token(payload.get("delay_policy_id")) or "delay.none",
                edge_payload=payload,
                temporal_domain_registry_payload=temporal_domain_registry_payload,
                time_mapping_registry_payload=time_mapping_registry_payload,
                drift_policy_registry_payload=drift_policy_registry_payload,
                model_type_registry_payload=model_type_registry_payload,
                constitutive_model_registry_payload=constitutive_model_registry_payload,
                session_scope_id=session_scope_id,
            )
            next_delay = delay_accumulated + int(max(1, as_int(resolution.get("deliver_delay_ticks", 1), 1)))
            next_path = list(edge_path) + [dict(edge)]
            next_delay_trace = list(delay_trace) + [dict(as_map(resolution.get("resolution_trace")))]
            next_payload = as_map(node_payloads.get(next_node_id))
            node_kind = token(next_payload.get("node_kind"))
            if node_kind == "port_in":
                deliveries.append(
                    {
                        "target_element_id": token(next_payload.get("element_instance_id")),
                        "target_port_id": token(next_payload.get("port_id")),
                        "target_node_id": next_node_id,
                        "edge_path": next_path,
                        "deliver_delay_ticks": int(max(1, next_delay)),
                        "carrier_type_id": token(payload.get("carrier_type_id")),
                        "delay_policy_id": token(payload.get("delay_policy_id")) or "delay.none",
                        "noise_policy_id": token(payload.get("noise_policy_id")) or "noise.none",
                        "signal_type_id": token(payload.get("signal_type_id")),
                        "bus_id": token(as_map(payload.get("extensions")).get("bus_id")) or None,
                        "protocol_id": token(payload.get("protocol_id")) or None,
                        "delay_trace": next_delay_trace,
                    }
                )
                continue
            if node_kind in {"junction", "bus_junction", "protocol_endpoint"}:
                queue.append((next_node_id, next_path, next_delay, next_delay_trace))
    return deliveries


def schedule_logic_output_propagation(
    *,
    current_tick: int,
    network_id: str,
    graph_row: Mapping[str, object],
    compute_result: Mapping[str, object],
    sense_snapshot: Mapping[str, object],
    pending_signal_update_rows: object,
    protocol_frame_rows: object,
    propagation_trace_rows: object,
    protocol_registry_payload: Mapping[str, object] | None = None,
    temporal_domain_registry_payload: Mapping[str, object] | None = None,
    time_mapping_registry_payload: Mapping[str, object] | None = None,
    drift_policy_registry_payload: Mapping[str, object] | None = None,
    model_type_registry_payload: Mapping[str, object] | None = None,
    constitutive_model_registry_payload: Mapping[str, object] | None = None,
    session_scope_id: str = "session.default",
) -> dict:
    snapshot = as_map(sense_snapshot)
    element_nodes = {
        token(row.get("element_instance_id")): dict(as_map(row.get("output_ports")))
        for row in as_list(snapshot.get("elements"))
        if isinstance(row, Mapping)
    }
    pending_rows = list(pending_signal_update_rows or [])
    frame_rows = list(protocol_frame_rows or [])
    trace_rows = list(propagation_trace_rows or [])
    scheduled_count = 0
    max_propagation_delay_ticks = 0
    max_deliver_tick = int(current_tick)
    protocol_rows = _registry_rows_by_id(protocol_registry_payload, "protocols", "protocol_id")
    for row in (dict(item) for item in as_list(as_map(compute_result).get("element_results")) if isinstance(item, Mapping)):
        element_instance_id = token(row.get("element_instance_id"))
        output_nodes = dict(element_nodes.get(element_instance_id) or {})
        for port_id, output_payload in sorted((dict(as_map(row.get("output_payloads"))).items()), key=lambda item: str(item[0])):
            source_node = dict(output_nodes.get(port_id) or {})
            from_node_id = token(source_node.get("node_id"))
            if not from_node_id:
                continue
            deliveries = _route_output_targets(
                current_tick=current_tick,
                network_id=network_id,
                graph_row=graph_row,
                from_node_id=from_node_id,
                temporal_domain_registry_payload=temporal_domain_registry_payload,
                time_mapping_registry_payload=time_mapping_registry_payload,
                drift_policy_registry_payload=drift_policy_registry_payload,
                model_type_registry_payload=model_type_registry_payload,
                constitutive_model_registry_payload=constitutive_model_registry_payload,
                session_scope_id=session_scope_id,
            )
            signal_payload = as_map(output_payload)
            value_payload = as_map(signal_payload.get("value_payload"))
            signal_type_id = token(signal_payload.get("signal_type_id")) or "signal.boolean"
            source_slot = slot_key(network_id=network_id, element_id=element_instance_id, port_id=port_id)
            signal_hash = canonical_sha256(
                {
                    "source_slot": source_slot,
                    "signal_type_id": signal_type_id,
                    "value_payload": value_payload,
                }
            )
            for delivery in deliveries:
                scheduled_count += 1
                if token(delivery.get("protocol_id")):
                    protocol_row = dict(protocol_rows.get(token(delivery.get("protocol_id"))) or {})
                    if protocol_row:
                        frame_rows.append(
                            build_protocol_frame_from_delivery(
                                current_tick=int(current_tick),
                                network_id=network_id,
                                source_element_id=element_instance_id,
                                source_port_id=port_id,
                                delivery=delivery,
                                value_payload=value_payload,
                                protocol_row=protocol_row,
                            )
                        )
                        max_propagation_delay_ticks = max(
                            int(max_propagation_delay_ticks),
                            int(max(1, as_int(delivery.get("deliver_delay_ticks"), 1))),
                        )
                        max_deliver_tick = max(
                            int(max_deliver_tick),
                            int(current_tick) + int(max(1, as_int(delivery.get("deliver_delay_ticks"), 1))),
                        )
                        continue
                deliver_tick = int(max(int(current_tick) + 1, int(current_tick) + as_int(delivery.get("deliver_delay_ticks"), 1)))
                max_propagation_delay_ticks = max(
                    int(max_propagation_delay_ticks),
                    int(max(1, as_int(delivery.get("deliver_delay_ticks"), 1))),
                )
                max_deliver_tick = max(int(max_deliver_tick), int(deliver_tick))
                pending_rows.append(
                    build_logic_pending_signal_update_row(
                        network_id=network_id,
                        source_element_id=element_instance_id,
                        source_port_id=port_id,
                        target_element_id=token(delivery.get("target_element_id")),
                        target_port_id=token(delivery.get("target_port_id")),
                        signal_type_id=token(delivery.get("signal_type_id")) or signal_type_id,
                        carrier_type_id=token(delivery.get("carrier_type_id")) or "carrier.electrical",
                        delay_policy_id=token(delivery.get("delay_policy_id")) or "delay.none",
                        noise_policy_id=token(delivery.get("noise_policy_id")) or "noise.none",
                        deliver_tick=deliver_tick,
                        value_payload=value_payload,
                        bus_id=(None if delivery.get("bus_id") is None else token(delivery.get("bus_id")) or None),
                        protocol_id=(None if delivery.get("protocol_id") is None else token(delivery.get("protocol_id")) or None),
                        deterministic_fingerprint="",
                        extensions={
                            "edge_ids": [token(edge.get("edge_id")) for edge in as_list(delivery.get("edge_path"))],
                            "deliver_delay_ticks": int(as_int(delivery.get("deliver_delay_ticks"), 1)),
                            "delay_resolution_trace": [dict(row) for row in as_list(delivery.get("delay_trace")) if isinstance(row, Mapping)],
                            "scheduled_by": "LOGIC4-6",
                        },
                    )
                )
                trace_rows.append(
                    build_logic_propagation_trace_artifact_row(
                        tick=int(current_tick),
                        network_id=network_id,
                        trace_kind="trace.logic.propagation_scheduled",
                        slot_key_value=slot_key(
                            network_id=network_id,
                            element_id=token(delivery.get("target_element_id")),
                            port_id=token(delivery.get("target_port_id")),
                        ),
                        signal_hash=signal_hash,
                        deterministic_fingerprint="",
                        extensions={
                            "source_slot_key": source_slot,
                            "deliver_tick": deliver_tick,
                            "signal_type_id": token(delivery.get("signal_type_id")) or signal_type_id,
                            "delay_resolution_trace": [dict(row) for row in as_list(delivery.get("delay_trace")) if isinstance(row, Mapping)],
                        },
                    )
                )
    return {
        "logic_pending_signal_update_rows": normalize_logic_pending_signal_update_rows(pending_rows),
        "logic_protocol_frame_rows": normalize_protocol_frame_rows(frame_rows),
        "logic_propagation_trace_artifact_rows": normalize_logic_propagation_trace_artifact_rows(trace_rows),
        "scheduled_count": int(scheduled_count),
        "max_propagation_delay_ticks": int(max_propagation_delay_ticks),
        "max_deliver_tick": int(max_deliver_tick),
    }


def flush_due_logic_signal_updates(
    *,
    current_tick: int,
    signal_store_state: Mapping[str, object] | None,
    pending_signal_update_rows: object,
    propagation_trace_rows: object,
    signal_type_registry_payload: Mapping[str, object] | None,
    carrier_type_registry_payload: Mapping[str, object] | None,
    signal_delay_policy_registry_payload: Mapping[str, object] | None,
    signal_noise_policy_registry_payload: Mapping[str, object] | None,
    bus_encoding_registry_payload: Mapping[str, object] | None,
    protocol_registry_payload: Mapping[str, object] | None,
    compute_runtime_state: Mapping[str, object] | None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None,
    tolerance_policy_registry_payload: Mapping[str, object] | None,
    process_signal_set_fn,
    process_signal_emit_pulse_fn,
) -> dict:
    due = []
    pending = []
    for row in normalize_logic_pending_signal_update_rows(pending_signal_update_rows):
        if as_int(row.get("deliver_tick"), 0) <= int(current_tick):
            due.append(dict(row))
        else:
            pending.append(dict(row))
    state = signal_store_state
    compute_state = as_map(compute_runtime_state)
    trace_rows = list(propagation_trace_rows or [])
    delivered_count = 0
    for row in due:
        delivered_count += 1
        request = {
            "network_id": token(row.get("network_id")),
            "element_id": token(row.get("target_element_id")),
            "port_id": token(row.get("target_port_id")),
            "signal_type_id": token(row.get("signal_type_id")),
            "carrier_type_id": token(row.get("carrier_type_id")),
            "delay_policy_id": token(row.get("delay_policy_id")) or "delay.none",
            "noise_policy_id": token(row.get("noise_policy_id")) or "noise.none",
            "value_payload": as_map(row.get("value_payload")),
            "bus_id": None if row.get("bus_id") is None else token(row.get("bus_id")) or None,
            "protocol_id": None if row.get("protocol_id") is None else token(row.get("protocol_id")) or None,
            "extensions": {
                "pending_id": token(row.get("pending_id")),
                "source_element_id": token(row.get("source_element_id")),
                "source_port_id": token(row.get("source_port_id")),
                "scheduled_deliver_tick": int(as_int(row.get("deliver_tick"), 0)),
            },
        }
        if token(row.get("signal_type_id")) == "signal.pulse":
            updated = process_signal_emit_pulse_fn(
                current_tick=current_tick,
                signal_store_state=state,
                pulse_request=request,
                signal_type_registry_payload=signal_type_registry_payload,
                carrier_type_registry_payload=carrier_type_registry_payload,
                signal_delay_policy_registry_payload=signal_delay_policy_registry_payload,
                signal_noise_policy_registry_payload=signal_noise_policy_registry_payload,
                bus_encoding_registry_payload=bus_encoding_registry_payload,
                protocol_registry_payload=protocol_registry_payload,
                compute_runtime_state=compute_state,
                compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
                compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
                tolerance_policy_registry_payload=tolerance_policy_registry_payload,
            )
        else:
            updated = process_signal_set_fn(
                current_tick=current_tick,
                signal_store_state=state,
                signal_request=request,
                signal_type_registry_payload=signal_type_registry_payload,
                carrier_type_registry_payload=carrier_type_registry_payload,
                signal_delay_policy_registry_payload=signal_delay_policy_registry_payload,
                signal_noise_policy_registry_payload=signal_noise_policy_registry_payload,
                bus_encoding_registry_payload=bus_encoding_registry_payload,
                protocol_registry_payload=protocol_registry_payload,
                compute_runtime_state=compute_state,
                compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
                compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
                tolerance_policy_registry_payload=tolerance_policy_registry_payload,
            )
        if token(updated.get("result")) != "complete":
            return {
                "result": token(updated.get("result")) or "refused",
                "reason_code": token(updated.get("reason_code")) or "refusal.logic.signal_invalid",
                "signal_store_state": updated.get("signal_store_state") or state,
                "compute_runtime_state": compute_state,
                "logic_pending_signal_update_rows": normalize_logic_pending_signal_update_rows(pending + [row] + due[due.index(row) + 1 :]),
                "logic_propagation_trace_artifact_rows": normalize_logic_propagation_trace_artifact_rows(trace_rows),
            }
        state = updated.get("signal_store_state") or state
        compute_state = as_map(as_map(state).get("compute_runtime_state"))
        signal_row = dict(updated.get("signal_row") or {})
        signal_hash = canonical_sha256(signal_row) if signal_row else canonical_sha256(row)
        trace_rows.append(
            build_logic_propagation_trace_artifact_row(
                tick=int(current_tick),
                network_id=token(row.get("network_id")),
                trace_kind="trace.logic.propagation_delivered",
                slot_key_value=slot_key(
                    network_id=token(row.get("network_id")),
                    element_id=token(row.get("target_element_id")),
                    port_id=token(row.get("target_port_id")),
                ),
                signal_hash=signal_hash,
                deterministic_fingerprint="",
                extensions={
                    "pending_id": token(row.get("pending_id")),
                    "signal_id": token(signal_row.get("signal_id")),
                },
            )
        )
    return {
        "result": "complete",
        "reason_code": "",
        "signal_store_state": state,
        "compute_runtime_state": compute_state,
        "logic_pending_signal_update_rows": normalize_logic_pending_signal_update_rows(pending),
        "logic_propagation_trace_artifact_rows": normalize_logic_propagation_trace_artifact_rows(trace_rows),
        "delivered_count": int(delivered_count),
    }


__all__ = [
    "flush_due_logic_signal_updates",
    "schedule_logic_output_propagation",
]
