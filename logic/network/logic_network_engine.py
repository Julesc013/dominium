"""LOGIC-3 deterministic LogicNetworkGraph helpers and process APIs."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping

from core.graph.network_graph_engine import NetworkGraphError, normalize_network_graph
from meta.compute import request_compute
from tools.xstack.compatx.canonical_json import canonical_sha256


PROCESS_LOGIC_NETWORK_CREATE = "process.logic_network_create"
PROCESS_LOGIC_NETWORK_ADD_NODE = "process.logic_network_add_node"
PROCESS_LOGIC_NETWORK_ADD_EDGE = "process.logic_network_add_edge"
PROCESS_LOGIC_NETWORK_REMOVE_EDGE = "process.logic_network_remove_edge"
PROCESS_LOGIC_NETWORK_VALIDATE = "process.logic_network_validate"

REFUSAL_LOGIC_NETWORK_INVALID = "refusal.logic.network_invalid"
REFUSAL_LOGIC_NETWORK_POLICY_UNREGISTERED = "refusal.logic.network_policy_unregistered"
REFUSAL_LOGIC_NETWORK_NODE_INVALID = "refusal.logic.network_node_invalid"
REFUSAL_LOGIC_NETWORK_EDGE_INVALID = "refusal.logic.network_edge_invalid"
REFUSAL_LOGIC_NETWORK_NOT_FOUND = "refusal.logic.network_not_found"
REFUSAL_LOGIC_NETWORK_CONTROL_CONTEXT_REQUIRED = "refusal.logic.control_context_required"

_NODE_KINDS = {"port_in", "port_out", "junction", "bus_junction", "protocol_endpoint"}
_EDGE_KINDS = {"link", "bus_link", "protocol_link", "sig_link"}
_CONTROL_CONTEXT_KINDS = {"planning", "execution"}
_CONTROL_CONTEXT_ID_KEYS = ("intent_id", "plan_id", "execution_id", "control_intent_id")


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(_token(item) for item in list(values or []) if _token(item)))


def _canon(value: object) -> object:
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if isinstance(value, float):
        return int(round(float(value)))
    if value is None or isinstance(value, (str, int, bool)):
        return value
    return str(value)


def _registry_rows_by_id(payload: Mapping[str, object] | None, list_key: str, id_key: str) -> Dict[str, dict]:
    body = _as_map(payload)
    rows = body.get(list_key)
    if not isinstance(rows, list):
        rows = _as_map(body.get("record")).get(list_key)
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: _token(item.get(id_key))):
        token = _token(row.get(id_key))
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _normalize_control_context(control_context: Mapping[str, object] | None) -> dict:
    body = _as_map(control_context)
    context_kind = _token(body.get("context_kind")).lower()
    if context_kind not in _CONTROL_CONTEXT_KINDS:
        return {}
    out = {
        "context_kind": context_kind,
        "intent_id": None,
        "plan_id": None,
        "execution_id": None,
        "control_intent_id": None,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(body.get("extensions"))),
    }
    has_id = False
    for key in _CONTROL_CONTEXT_ID_KEYS:
        value = None if body.get(key) is None else _token(body.get(key)) or None
        out[key] = value
        if value:
            has_id = True
    if not has_id:
        return {}
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


def deterministic_logic_graph_id(*, network_id: str) -> str:
    return "graph.logic.{}".format(canonical_sha256({"network_id": _token(network_id)})[:16])


def deterministic_logic_binding_id(*, network_id: str, graph_id: str) -> str:
    return "binding.logic.{}".format(
        canonical_sha256({"network_id": _token(network_id), "graph_id": _token(graph_id)})[:16]
    )


def deterministic_logic_node_id(*, network_id: str, node_key: str) -> str:
    return "node.logic.{}".format(
        canonical_sha256({"network_id": _token(network_id), "node_key": _token(node_key)})[:16]
    )


def deterministic_logic_edge_id(*, network_id: str, from_node_id: str, to_node_id: str, edge_key: str) -> str:
    return "edge.logic.{}".format(
        canonical_sha256(
            {
                "network_id": _token(network_id),
                "from_node_id": _token(from_node_id),
                "to_node_id": _token(to_node_id),
                "edge_key": _token(edge_key),
            }
        )[:16]
    )


def build_logic_node_payload_row(
    *,
    node_kind: str,
    element_instance_id: str | None = None,
    port_id: str | None = None,
    bus_id: str | None = None,
    protocol_id: str | None = None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "node_kind": _token(node_kind).lower(),
        "element_instance_id": None if element_instance_id is None else _token(element_instance_id) or None,
        "port_id": None if port_id is None else _token(port_id) or None,
        "bus_id": None if bus_id is None else _token(bus_id) or None,
        "protocol_id": None if protocol_id is None else _token(protocol_id) or None,
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    if payload["node_kind"] not in _NODE_KINDS:
        return {}
    if payload["node_kind"] in {"port_in", "port_out"} and (
        (not payload["element_instance_id"]) or (not payload["port_id"])
    ):
        return {}
    if payload["node_kind"] == "bus_junction" and not payload["bus_id"]:
        return {}
    if payload["node_kind"] == "protocol_endpoint" and not payload["protocol_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_logic_edge_payload_row(
    *,
    edge_kind: str,
    signal_type_id: str,
    carrier_type_id: str,
    delay_policy_id: str,
    noise_policy_id: str,
    protocol_id: str | None = None,
    capacity: int | None = None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "edge_kind": _token(edge_kind).lower(),
        "signal_type_id": _token(signal_type_id),
        "carrier_type_id": _token(carrier_type_id),
        "delay_policy_id": _token(delay_policy_id),
        "noise_policy_id": _token(noise_policy_id),
        "protocol_id": None if protocol_id is None else _token(protocol_id) or None,
        "capacity": None if capacity is None else int(max(0, _as_int(capacity, 0))),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    if (
        payload["edge_kind"] not in _EDGE_KINDS
        or (not payload["signal_type_id"])
        or (not payload["carrier_type_id"])
        or (not payload["delay_policy_id"])
        or (not payload["noise_policy_id"])
    ):
        return {}
    if payload["edge_kind"] == "protocol_link" and not payload["protocol_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_logic_network_binding_row(
    *,
    network_id: str,
    graph_id: str,
    policy_id: str,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "binding_id": deterministic_logic_binding_id(network_id=network_id, graph_id=graph_id),
        "network_id": _token(network_id),
        "graph_id": _token(graph_id),
        "policy_id": _token(policy_id),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    if (not payload["network_id"]) or (not payload["graph_id"]) or (not payload["policy_id"]):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_network_binding_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: _token(item.get("network_id"))):
        normalized = build_logic_network_binding_row(
            network_id=_token(row.get("network_id")),
            graph_id=_token(row.get("graph_id")),
            policy_id=_token(row.get("policy_id")),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        token = _token(normalized.get("network_id"))
        if token:
            out[token] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def normalize_logic_network_state(state: Mapping[str, object] | None) -> dict:
    src = _as_map(state)
    graph_rows = []
    for row in sorted(
        (dict(item) for item in _as_list(src.get("logic_network_graph_rows")) if isinstance(item, Mapping)),
        key=lambda item: _token(item.get("graph_id")),
    ):
        try:
            graph_rows.append(normalize_network_graph(row))
        except NetworkGraphError:
            continue
    return {
        "schema_version": "1.0.0",
        "logic_network_graph_rows": graph_rows,
        "logic_network_binding_rows": normalize_logic_network_binding_rows(src.get("logic_network_binding_rows")),
        "logic_network_validation_records": [
            _canon(dict(item))
            for item in sorted(
                (dict(item) for item in _as_list(src.get("logic_network_validation_records")) if isinstance(item, Mapping)),
                key=lambda item: (_token(item.get("network_id")), _as_int(item.get("validation_tick", 0), 0), _token(item.get("validation_hash"))),
            )
        ],
        "logic_network_change_records": [
            _canon(dict(item))
            for item in sorted(
                (dict(item) for item in _as_list(src.get("logic_network_change_records")) if isinstance(item, Mapping)),
                key=lambda item: (_as_int(item.get("tick", 0), 0), _token(item.get("record_id"))),
            )
        ],
        "logic_network_explain_artifact_rows": [
            _canon(dict(item))
            for item in sorted(
                (dict(item) for item in _as_list(src.get("logic_network_explain_artifact_rows")) if isinstance(item, Mapping)),
                key=lambda item: (_as_int(item.get("created_tick", 0), 0), _token(item.get("artifact_id"))),
            )
        ],
        "compute_runtime_state": _canon(_as_map(src.get("compute_runtime_state"))),
        "extensions": _canon(_as_map(src.get("extensions"))),
    }


def canonical_logic_network_snapshot(*, state: Mapping[str, object] | None) -> dict:
    normalized = normalize_logic_network_state(state)
    return {
        "schema_version": "1.0.0",
        "bindings": list(normalized.get("logic_network_binding_rows") or []),
        "graphs": list(normalized.get("logic_network_graph_rows") or []),
    }


def canonical_logic_network_hash(*, state: Mapping[str, object] | None) -> str:
    return canonical_sha256(canonical_logic_network_snapshot(state=state))


def _binding_by_network_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_logic_network_binding_rows(rows):
        token = _token(row.get("network_id"))
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _graph_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: _token(item.get("graph_id"))):
        graph_id = _token(row.get("graph_id"))
        if not graph_id:
            continue
        try:
            out[graph_id] = normalize_network_graph(row)
        except NetworkGraphError:
            continue
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _network_compute_owner_id(process_id: str, network_id: str) -> str:
    network_token = _token(network_id) or "logic_network"
    return "{}.{}".format(_token(process_id) or "process.logic_network", network_token)


def _estimate_compute_units(*, nodes: int = 0, edges: int = 0, validation: bool = False) -> tuple[int, int]:
    instruction_units = 4 + max(0, int(nodes)) * 2 + max(0, int(edges)) * 3
    memory_units = 2 + max(0, int(nodes)) + max(0, int(edges))
    if validation:
        instruction_units += max(4, int(nodes) + int(edges))
        memory_units += max(1, int(nodes))
    return int(instruction_units), int(memory_units)


def _logic_change_record_row(
    *,
    tick: int,
    process_id: str,
    network_id: str,
    graph_id: str,
    operation: str,
    control_context: Mapping[str, object] | None,
    prior_hash: str | None,
    next_hash: str | None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "record_id": "record.logic.network.{}".format(
            canonical_sha256(
                {
                    "tick": int(max(0, _as_int(tick, 0))),
                    "process_id": _token(process_id),
                    "network_id": _token(network_id),
                    "graph_id": _token(graph_id),
                    "operation": _token(operation),
                    "prior_hash": None if prior_hash is None else _token(prior_hash) or None,
                    "next_hash": None if next_hash is None else _token(next_hash) or None,
                    "control_context": _canon(_as_map(control_context)),
                }
            )[:16]
        ),
        "tick": int(max(0, _as_int(tick, 0))),
        "process_id": _token(process_id),
        "network_id": _token(network_id),
        "graph_id": _token(graph_id),
        "operation": _token(operation),
        "control_context": _canon(_as_map(control_context)),
        "prior_graph_hash": None if prior_hash is None else _token(prior_hash) or None,
        "next_graph_hash": None if next_hash is None else _token(next_hash) or None,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _logic_validation_record_row(
    *,
    tick: int,
    network_id: str,
    graph_id: str,
    policy_id: str,
    validation_result: Mapping[str, object],
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "network_id": _token(network_id),
        "graph_id": _token(graph_id),
        "policy_id": _token(policy_id),
        "validation_tick": int(max(0, _as_int(tick, 0))),
        "validation_hash": _token(validation_result.get("validation_hash")),
        "result": _token(validation_result.get("result")) or "refused",
        "reason_code": _token(validation_result.get("reason_code")),
        "requires_l2_roi": bool(validation_result.get("requires_l2_roi", False)),
        "loop_classifications": _canon(_as_list(validation_result.get("loop_classifications"))),
        "deterministic_fingerprint": "",
        "extensions": {
            "failed_check_count": len(_as_list(validation_result.get("failed_checks"))),
            "warning_count": len(_as_list(validation_result.get("warnings"))),
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _logic_loop_explain_artifact_rows(
    *,
    tick: int,
    network_id: str,
    graph_id: str,
    validation_result: Mapping[str, object],
) -> List[dict]:
    out: List[dict] = []
    for row in sorted(
        (dict(item) for item in _as_list(validation_result.get("loop_classifications")) if isinstance(item, Mapping)),
        key=lambda item: (_token(item.get("classification")), "|".join(_sorted_tokens(item.get("node_ids")))),
    ):
        node_ids = _sorted_tokens(row.get("node_ids"))
        if not node_ids:
            continue
        artifact_type_id = "artifact.explain.logic_loop_detected"
        event_kind_id = "logic.loop_detected"
        if _token(row.get("classification")) == "mixed" and bool(row.get("requires_l2_roi", False)):
            artifact_type_id = "artifact.explain.logic_timing_violation"
            event_kind_id = "logic.timing_violation"
        payload = {
            "schema_version": "1.0.0",
            "artifact_id": "artifact.logic.network.explain.{}".format(
                canonical_sha256(
                    {
                        "tick": int(max(0, _as_int(tick, 0))),
                        "network_id": _token(network_id),
                        "graph_id": _token(graph_id),
                        "event_kind_id": event_kind_id,
                        "node_ids": node_ids,
                    }
                )[:16]
            ),
            "artifact_family_id": "EXPLAIN",
            "artifact_type_id": artifact_type_id,
            "network_id": _token(network_id),
            "graph_id": _token(graph_id),
            "event_kind_id": event_kind_id,
            "created_tick": int(max(0, _as_int(tick, 0))),
            "deterministic_fingerprint": "",
            "extensions": {
                "classification": _token(row.get("classification")),
                "node_ids": node_ids,
                "element_instance_ids": _sorted_tokens(row.get("element_instance_ids")),
                "requires_l2_roi": bool(row.get("requires_l2_roi", False)),
                "policy_resolution": _token(row.get("policy_resolution")),
                "trace_compactable": True,
            },
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        out.append(payload)
    return sorted(out, key=lambda item: (_as_int(item.get("created_tick", 0), 0), _token(item.get("artifact_id"))))


def _logic_node_type_id(node_kind: str) -> str:
    return "node.logic.{}".format(_token(node_kind).lower())


def _logic_edge_type_id(edge_kind: str) -> str:
    return "edge.logic.{}".format(_token(edge_kind).lower())


def _build_logic_graph_row(
    *,
    graph_id: str,
    nodes: object,
    edges: object,
    graph_partition_id: str | None = None,
    deterministic_routing_policy_id: str = "route.direct_only",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    node_rows = []
    for row in sorted((dict(item) for item in _as_list(nodes) if isinstance(item, Mapping)), key=lambda item: _token(item.get("node_id"))):
        payload = _as_map(row.get("payload"))
        node_kind = _token(payload.get("node_kind"))
        node_rows.append(
            {
                "schema_version": "1.0.0",
                "node_id": _token(row.get("node_id")),
                "node_type_id": _token(row.get("node_type_id")) or _logic_node_type_id(node_kind),
                "payload": payload,
                "tags": _sorted_tokens(row.get("tags")),
                "extensions": _canon(_as_map(row.get("extensions"))),
            }
        )
    edge_rows = []
    for row in sorted(
        (dict(item) for item in _as_list(edges) if isinstance(item, Mapping)),
        key=lambda item: (_token(item.get("from_node_id")), _token(item.get("to_node_id")), _token(item.get("edge_id"))),
    ):
        payload = _as_map(row.get("payload"))
        edge_kind = _token(payload.get("edge_kind"))
        edge_rows.append(
            {
                "schema_version": "1.0.0",
                "edge_id": _token(row.get("edge_id")),
                "from_node_id": _token(row.get("from_node_id")),
                "to_node_id": _token(row.get("to_node_id")),
                "edge_type_id": _token(row.get("edge_type_id")) or _logic_edge_type_id(edge_kind),
                "payload": payload,
                "capacity": (None if row.get("capacity") is None else int(max(0, _as_int(row.get("capacity"), 0)))),
                "delay_ticks": (None if row.get("delay_ticks") is None else int(max(0, _as_int(row.get("delay_ticks"), 0)))),
                "loss_fraction": (None if row.get("loss_fraction") is None else int(max(0, _as_int(row.get("loss_fraction"), 0)))),
                "cost_units": (None if row.get("cost_units") is None else int(max(0, _as_int(row.get("cost_units"), 0)))),
                "extensions": _canon(_as_map(row.get("extensions"))),
            }
        )
    graph_row = {
        "schema_version": "1.0.0",
        "graph_id": _token(graph_id),
        "node_type_schema_id": "dominium.schema.logic.logic_node_payload",
        "edge_type_schema_id": "dominium.schema.logic.logic_edge_payload",
        "payload_schema_versions": {
            "dominium.schema.logic.logic_node_payload": "1.0.0",
            "dominium.schema.logic.logic_edge_payload": "1.0.0",
        },
        "validation_mode": "strict",
        "graph_partition_id": None if graph_partition_id is None else _token(graph_partition_id) or None,
        "nodes": node_rows,
        "edges": edge_rows,
        "deterministic_routing_policy_id": _token(deterministic_routing_policy_id) or "route.direct_only",
        "extensions": _canon(_as_map(extensions)),
    }
    return normalize_network_graph(graph_row)


def process_logic_network_create(
    *,
    current_tick: int,
    logic_network_state: Mapping[str, object] | None,
    network_request: Mapping[str, object],
    logic_network_policy_registry_payload: Mapping[str, object] | None,
    compute_runtime_state: Mapping[str, object] | None = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None = None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_id: str = "compute.default",
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    request = _as_map(network_request)
    state = normalize_logic_network_state(logic_network_state)
    control_context = _normalize_control_context(_as_map(request.get("control_context")))
    if not control_context:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_NETWORK_CONTROL_CONTEXT_REQUIRED,
            "logic_network_state": state,
        }
    network_id = _token(request.get("network_id"))
    graph_id = _token(request.get("graph_id")) or deterministic_logic_graph_id(network_id=network_id)
    policy_id = _token(request.get("policy_id")) or "logic.policy.default"
    if not network_id:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_INVALID, "logic_network_state": state}
    policy_rows = _registry_rows_by_id(
        logic_network_policy_registry_payload,
        "logic_network_policies",
        "policy_id",
    )
    if policy_id not in policy_rows:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_NETWORK_POLICY_UNREGISTERED,
            "logic_network_state": state,
        }
    binding_rows = _binding_by_network_id(state.get("logic_network_binding_rows"))
    if network_id in binding_rows:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_INVALID, "logic_network_state": state}
    instruction_units, memory_units = _estimate_compute_units(nodes=0, edges=0)
    compute_result = request_compute(
        current_tick=tick,
        owner_kind="process",
        owner_id=_network_compute_owner_id(PROCESS_LOGIC_NETWORK_CREATE, network_id),
        instruction_units=instruction_units,
        memory_units=memory_units,
        compute_runtime_state=(compute_runtime_state if isinstance(compute_runtime_state, Mapping) else state.get("compute_runtime_state")),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_budget_profile_id=_token(request.get("compute_profile_id")) or _token(compute_budget_profile_id) or "compute.default",
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
    )
    if str(compute_result.get("result", "")) not in {"complete", "throttled"}:
        state["compute_runtime_state"] = _as_map(compute_result.get("runtime_state"))
        state = normalize_logic_network_state(state)
        return {
            "result": str(compute_result.get("result", "")) or "refused",
            "reason_code": _token(compute_result.get("reason_code")) or REFUSAL_LOGIC_NETWORK_INVALID,
            "compute_request": dict(compute_result),
            "logic_network_state": state,
        }
    graph_row = _build_logic_graph_row(
        graph_id=graph_id,
        nodes=[],
        edges=[],
        graph_partition_id=(None if request.get("graph_partition_id") is None else _token(request.get("graph_partition_id"))),
        deterministic_routing_policy_id=_token(request.get("deterministic_routing_policy_id")) or "route.direct_only",
        extensions=dict(_as_map(request.get("extensions")), domain_id="LOGIC"),
    )
    binding_row = build_logic_network_binding_row(
        network_id=network_id,
        graph_id=graph_id,
        policy_id=policy_id,
        extensions={
            "validation_status": "pending",
            "control_context": control_context,
        },
    )
    state["logic_network_graph_rows"] = list(state.get("logic_network_graph_rows") or []) + [graph_row]
    state["logic_network_binding_rows"] = list(state.get("logic_network_binding_rows") or []) + [binding_row]
    state["compute_runtime_state"] = _as_map(compute_result.get("runtime_state"))
    graph_hash = canonical_sha256(graph_row)
    state["logic_network_change_records"] = list(state.get("logic_network_change_records") or []) + [
        _logic_change_record_row(
            tick=tick,
            process_id=PROCESS_LOGIC_NETWORK_CREATE,
            network_id=network_id,
            graph_id=graph_id,
            operation="create",
            control_context=control_context,
            prior_hash=None,
            next_hash=graph_hash,
        )
    ]
    state = normalize_logic_network_state(state)
    return {
        "result": "complete",
        "reason_code": "",
        "graph_row": graph_row,
        "binding_row": binding_row,
        "compute_request": dict(compute_result),
        "logic_network_state": state,
    }


def process_logic_network_add_node(
    *,
    current_tick: int,
    logic_network_state: Mapping[str, object] | None,
    node_request: Mapping[str, object],
    logic_network_policy_registry_payload: Mapping[str, object] | None,
    compute_runtime_state: Mapping[str, object] | None = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None = None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_id: str = "compute.default",
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    request = _as_map(node_request)
    state = normalize_logic_network_state(logic_network_state)
    control_context = _normalize_control_context(_as_map(request.get("control_context")))
    if not control_context:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_CONTROL_CONTEXT_REQUIRED, "logic_network_state": state}
    network_id = _token(request.get("network_id"))
    bindings = _binding_by_network_id(state.get("logic_network_binding_rows"))
    binding_row = dict(bindings.get(network_id) or {})
    if not binding_row:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_NOT_FOUND, "logic_network_state": state}
    policy_rows = _registry_rows_by_id(logic_network_policy_registry_payload, "logic_network_policies", "policy_id")
    if _token(binding_row.get("policy_id")) not in policy_rows:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_POLICY_UNREGISTERED, "logic_network_state": state}
    payload = build_logic_node_payload_row(
        node_kind=_token(request.get("node_kind")),
        element_instance_id=(None if request.get("element_instance_id") is None else _token(request.get("element_instance_id"))),
        port_id=(None if request.get("port_id") is None else _token(request.get("port_id"))),
        bus_id=(None if request.get("bus_id") is None else _token(request.get("bus_id"))),
        protocol_id=(None if request.get("protocol_id") is None else _token(request.get("protocol_id"))),
        extensions=_as_map(request.get("extensions")),
    )
    if not payload:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_NODE_INVALID, "logic_network_state": state}
    node_key = _token(request.get("node_key")) or canonical_sha256(payload)
    node_id = _token(request.get("node_id")) or deterministic_logic_node_id(network_id=network_id, node_key=node_key)
    graph_id = _token(binding_row.get("graph_id"))
    graph_rows = _graph_by_id(state.get("logic_network_graph_rows"))
    graph_row = dict(graph_rows.get(graph_id) or {})
    if not graph_row:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_NOT_FOUND, "logic_network_state": state}
    existing_node_ids = {_token(row.get("node_id")) for row in _as_list(graph_row.get("nodes")) if isinstance(row, Mapping)}
    if node_id in existing_node_ids:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_NODE_INVALID, "logic_network_state": state}
    instruction_units, memory_units = _estimate_compute_units(nodes=len(existing_node_ids) + 1, edges=len(_as_list(graph_row.get("edges"))))
    compute_result = request_compute(
        current_tick=tick,
        owner_kind="process",
        owner_id=_network_compute_owner_id(PROCESS_LOGIC_NETWORK_ADD_NODE, network_id),
        instruction_units=instruction_units,
        memory_units=memory_units,
        compute_runtime_state=(compute_runtime_state if isinstance(compute_runtime_state, Mapping) else state.get("compute_runtime_state")),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_budget_profile_id=_token(request.get("compute_profile_id")) or _token(compute_budget_profile_id) or "compute.default",
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
    )
    if str(compute_result.get("result", "")) not in {"complete", "throttled"}:
        state["compute_runtime_state"] = _as_map(compute_result.get("runtime_state"))
        state = normalize_logic_network_state(state)
        return {
            "result": str(compute_result.get("result", "")) or "refused",
            "reason_code": _token(compute_result.get("reason_code")) or REFUSAL_LOGIC_NETWORK_NODE_INVALID,
            "compute_request": dict(compute_result),
            "logic_network_state": state,
        }
    graph_candidate = dict(graph_row)
    graph_candidate["nodes"] = list(graph_row.get("nodes") or []) + [
        {
            "schema_version": "1.0.0",
            "node_id": node_id,
            "node_type_id": _logic_node_type_id(_token(payload.get("node_kind"))),
            "payload": payload,
            "tags": _sorted_tokens(request.get("tags")),
            "extensions": _canon(_as_map(request.get("node_extensions"))),
        }
    ]
    prior_hash = canonical_sha256(graph_row)
    try:
        graph_next = normalize_network_graph(graph_candidate)
    except NetworkGraphError:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_NODE_INVALID, "logic_network_state": state}
    next_hash = canonical_sha256(graph_next)
    state["logic_network_graph_rows"] = [
        dict(row)
        for row in list(state.get("logic_network_graph_rows") or [])
        if isinstance(row, Mapping) and _token(row.get("graph_id")) != graph_id
    ] + [graph_next]
    state["compute_runtime_state"] = _as_map(compute_result.get("runtime_state"))
    binding_row["extensions"] = dict(_as_map(binding_row.get("extensions")), validation_status="pending")
    state["logic_network_binding_rows"] = [
        dict(row)
        for row in list(state.get("logic_network_binding_rows") or [])
        if isinstance(row, Mapping) and _token(row.get("network_id")) != network_id
    ] + [build_logic_network_binding_row(
        network_id=network_id,
        graph_id=graph_id,
        policy_id=_token(binding_row.get("policy_id")),
        extensions=_as_map(binding_row.get("extensions")),
    )]
    state["logic_network_change_records"] = list(state.get("logic_network_change_records") or []) + [
        _logic_change_record_row(
            tick=tick,
            process_id=PROCESS_LOGIC_NETWORK_ADD_NODE,
            network_id=network_id,
            graph_id=graph_id,
            operation="add_node",
            control_context=control_context,
            prior_hash=prior_hash,
            next_hash=next_hash,
            extensions={"node_id": node_id},
        )
    ]
    state = normalize_logic_network_state(state)
    return {
        "result": "complete",
        "reason_code": "",
        "graph_row": graph_next,
        "node_id": node_id,
        "compute_request": dict(compute_result),
        "logic_network_state": state,
    }


def process_logic_network_add_edge(
    *,
    current_tick: int,
    logic_network_state: Mapping[str, object] | None,
    edge_request: Mapping[str, object],
    logic_network_policy_registry_payload: Mapping[str, object] | None,
    compute_runtime_state: Mapping[str, object] | None = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None = None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_id: str = "compute.default",
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    request = _as_map(edge_request)
    state = normalize_logic_network_state(logic_network_state)
    control_context = _normalize_control_context(_as_map(request.get("control_context")))
    if not control_context:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_CONTROL_CONTEXT_REQUIRED, "logic_network_state": state}
    network_id = _token(request.get("network_id"))
    bindings = _binding_by_network_id(state.get("logic_network_binding_rows"))
    binding_row = dict(bindings.get(network_id) or {})
    if not binding_row:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_NOT_FOUND, "logic_network_state": state}
    policy_rows = _registry_rows_by_id(logic_network_policy_registry_payload, "logic_network_policies", "policy_id")
    if _token(binding_row.get("policy_id")) not in policy_rows:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_POLICY_UNREGISTERED, "logic_network_state": state}
    payload = build_logic_edge_payload_row(
        edge_kind=_token(request.get("edge_kind")),
        signal_type_id=_token(request.get("signal_type_id")),
        carrier_type_id=_token(request.get("carrier_type_id")),
        delay_policy_id=_token(request.get("delay_policy_id")),
        noise_policy_id=_token(request.get("noise_policy_id")),
        protocol_id=(None if request.get("protocol_id") is None else _token(request.get("protocol_id"))),
        capacity=(None if request.get("capacity") is None else _as_int(request.get("capacity"), 0)),
        extensions=_as_map(request.get("extensions")),
    )
    if not payload:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_EDGE_INVALID, "logic_network_state": state}
    graph_id = _token(binding_row.get("graph_id"))
    graph_rows = _graph_by_id(state.get("logic_network_graph_rows"))
    graph_row = dict(graph_rows.get(graph_id) or {})
    if not graph_row:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_NOT_FOUND, "logic_network_state": state}
    from_node_id = _token(request.get("from_node_id"))
    to_node_id = _token(request.get("to_node_id"))
    node_ids = {_token(row.get("node_id")) for row in _as_list(graph_row.get("nodes")) if isinstance(row, Mapping)}
    if (from_node_id not in node_ids) or (to_node_id not in node_ids):
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_EDGE_INVALID, "logic_network_state": state}
    edge_key = _token(request.get("edge_key")) or canonical_sha256(
        {"from_node_id": from_node_id, "to_node_id": to_node_id, "payload": payload}
    )
    edge_id = _token(request.get("edge_id")) or deterministic_logic_edge_id(
        network_id=network_id,
        from_node_id=from_node_id,
        to_node_id=to_node_id,
        edge_key=edge_key,
    )
    edge_ids = {_token(row.get("edge_id")) for row in _as_list(graph_row.get("edges")) if isinstance(row, Mapping)}
    if edge_id in edge_ids:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_EDGE_INVALID, "logic_network_state": state}
    instruction_units, memory_units = _estimate_compute_units(nodes=len(node_ids), edges=len(edge_ids) + 1)
    compute_result = request_compute(
        current_tick=tick,
        owner_kind="process",
        owner_id=_network_compute_owner_id(PROCESS_LOGIC_NETWORK_ADD_EDGE, network_id),
        instruction_units=instruction_units,
        memory_units=memory_units,
        compute_runtime_state=(compute_runtime_state if isinstance(compute_runtime_state, Mapping) else state.get("compute_runtime_state")),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_budget_profile_id=_token(request.get("compute_profile_id")) or _token(compute_budget_profile_id) or "compute.default",
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
    )
    if str(compute_result.get("result", "")) not in {"complete", "throttled"}:
        state["compute_runtime_state"] = _as_map(compute_result.get("runtime_state"))
        state = normalize_logic_network_state(state)
        return {
            "result": str(compute_result.get("result", "")) or "refused",
            "reason_code": _token(compute_result.get("reason_code")) or REFUSAL_LOGIC_NETWORK_EDGE_INVALID,
            "compute_request": dict(compute_result),
            "logic_network_state": state,
        }
    graph_candidate = dict(graph_row)
    graph_candidate["edges"] = list(graph_row.get("edges") or []) + [
        {
            "schema_version": "1.0.0",
            "edge_id": edge_id,
            "from_node_id": from_node_id,
            "to_node_id": to_node_id,
            "edge_type_id": _logic_edge_type_id(_token(payload.get("edge_kind"))),
            "payload": payload,
            "capacity": (None if request.get("capacity") is None else int(max(0, _as_int(request.get("capacity"), 0)))),
            "delay_ticks": (None if request.get("delay_ticks") is None else int(max(0, _as_int(request.get("delay_ticks"), 0)))),
            "loss_fraction": (None if request.get("loss_fraction") is None else int(max(0, _as_int(request.get("loss_fraction"), 0)))),
            "cost_units": (None if request.get("cost_units") is None else int(max(0, _as_int(request.get("cost_units"), 0)))),
            "extensions": _canon(_as_map(request.get("edge_extensions"))),
        }
    ]
    prior_hash = canonical_sha256(graph_row)
    try:
        graph_next = normalize_network_graph(graph_candidate)
    except NetworkGraphError:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_EDGE_INVALID, "logic_network_state": state}
    next_hash = canonical_sha256(graph_next)
    state["logic_network_graph_rows"] = [
        dict(row)
        for row in list(state.get("logic_network_graph_rows") or [])
        if isinstance(row, Mapping) and _token(row.get("graph_id")) != graph_id
    ] + [graph_next]
    state["compute_runtime_state"] = _as_map(compute_result.get("runtime_state"))
    binding_row["extensions"] = dict(_as_map(binding_row.get("extensions")), validation_status="pending")
    state["logic_network_binding_rows"] = [
        dict(row)
        for row in list(state.get("logic_network_binding_rows") or [])
        if isinstance(row, Mapping) and _token(row.get("network_id")) != network_id
    ] + [build_logic_network_binding_row(
        network_id=network_id,
        graph_id=graph_id,
        policy_id=_token(binding_row.get("policy_id")),
        extensions=_as_map(binding_row.get("extensions")),
    )]
    state["logic_network_change_records"] = list(state.get("logic_network_change_records") or []) + [
        _logic_change_record_row(
            tick=tick,
            process_id=PROCESS_LOGIC_NETWORK_ADD_EDGE,
            network_id=network_id,
            graph_id=graph_id,
            operation="add_edge",
            control_context=control_context,
            prior_hash=prior_hash,
            next_hash=next_hash,
            extensions={"edge_id": edge_id},
        )
    ]
    state = normalize_logic_network_state(state)
    return {
        "result": "complete",
        "reason_code": "",
        "graph_row": graph_next,
        "edge_id": edge_id,
        "compute_request": dict(compute_result),
        "logic_network_state": state,
    }


def process_logic_network_remove_edge(
    *,
    current_tick: int,
    logic_network_state: Mapping[str, object] | None,
    edge_request: Mapping[str, object],
    logic_network_policy_registry_payload: Mapping[str, object] | None,
    compute_runtime_state: Mapping[str, object] | None = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None = None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_id: str = "compute.default",
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    request = _as_map(edge_request)
    state = normalize_logic_network_state(logic_network_state)
    control_context = _normalize_control_context(_as_map(request.get("control_context")))
    if not control_context:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_CONTROL_CONTEXT_REQUIRED, "logic_network_state": state}
    network_id = _token(request.get("network_id"))
    edge_id = _token(request.get("edge_id"))
    bindings = _binding_by_network_id(state.get("logic_network_binding_rows"))
    binding_row = dict(bindings.get(network_id) or {})
    if (not binding_row) or (not edge_id):
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_NOT_FOUND, "logic_network_state": state}
    policy_rows = _registry_rows_by_id(logic_network_policy_registry_payload, "logic_network_policies", "policy_id")
    if _token(binding_row.get("policy_id")) not in policy_rows:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_POLICY_UNREGISTERED, "logic_network_state": state}
    graph_id = _token(binding_row.get("graph_id"))
    graph_rows = _graph_by_id(state.get("logic_network_graph_rows"))
    graph_row = dict(graph_rows.get(graph_id) or {})
    if not graph_row:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_NOT_FOUND, "logic_network_state": state}
    edge_rows = [dict(row) for row in _as_list(graph_row.get("edges")) if isinstance(row, Mapping)]
    if edge_id not in {_token(row.get("edge_id")) for row in edge_rows}:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_EDGE_INVALID, "logic_network_state": state}
    instruction_units, memory_units = _estimate_compute_units(nodes=len(_as_list(graph_row.get("nodes"))), edges=max(0, len(edge_rows) - 1))
    compute_result = request_compute(
        current_tick=tick,
        owner_kind="process",
        owner_id=_network_compute_owner_id(PROCESS_LOGIC_NETWORK_REMOVE_EDGE, network_id),
        instruction_units=instruction_units,
        memory_units=memory_units,
        compute_runtime_state=(compute_runtime_state if isinstance(compute_runtime_state, Mapping) else state.get("compute_runtime_state")),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_budget_profile_id=_token(request.get("compute_profile_id")) or _token(compute_budget_profile_id) or "compute.default",
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
    )
    if str(compute_result.get("result", "")) not in {"complete", "throttled"}:
        state["compute_runtime_state"] = _as_map(compute_result.get("runtime_state"))
        state = normalize_logic_network_state(state)
        return {
            "result": str(compute_result.get("result", "")) or "refused",
            "reason_code": _token(compute_result.get("reason_code")) or REFUSAL_LOGIC_NETWORK_EDGE_INVALID,
            "compute_request": dict(compute_result),
            "logic_network_state": state,
        }
    prior_hash = canonical_sha256(graph_row)
    graph_candidate = dict(graph_row)
    graph_candidate["edges"] = [dict(row) for row in edge_rows if _token(row.get("edge_id")) != edge_id]
    try:
        graph_next = normalize_network_graph(graph_candidate)
    except NetworkGraphError:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_EDGE_INVALID, "logic_network_state": state}
    next_hash = canonical_sha256(graph_next)
    state["logic_network_graph_rows"] = [
        dict(row)
        for row in list(state.get("logic_network_graph_rows") or [])
        if isinstance(row, Mapping) and _token(row.get("graph_id")) != graph_id
    ] + [graph_next]
    state["compute_runtime_state"] = _as_map(compute_result.get("runtime_state"))
    binding_row["extensions"] = dict(_as_map(binding_row.get("extensions")), validation_status="pending")
    state["logic_network_binding_rows"] = [
        dict(row)
        for row in list(state.get("logic_network_binding_rows") or [])
        if isinstance(row, Mapping) and _token(row.get("network_id")) != network_id
    ] + [build_logic_network_binding_row(
        network_id=network_id,
        graph_id=graph_id,
        policy_id=_token(binding_row.get("policy_id")),
        extensions=_as_map(binding_row.get("extensions")),
    )]
    state["logic_network_change_records"] = list(state.get("logic_network_change_records") or []) + [
        _logic_change_record_row(
            tick=tick,
            process_id=PROCESS_LOGIC_NETWORK_REMOVE_EDGE,
            network_id=network_id,
            graph_id=graph_id,
            operation="remove_edge",
            control_context=control_context,
            prior_hash=prior_hash,
            next_hash=next_hash,
            extensions={"edge_id": edge_id},
        )
    ]
    state = normalize_logic_network_state(state)
    return {
        "result": "complete",
        "reason_code": "",
        "graph_row": graph_next,
        "removed_edge_id": edge_id,
        "compute_request": dict(compute_result),
        "logic_network_state": state,
    }


def process_logic_network_validate(
    *,
    current_tick: int,
    logic_network_state: Mapping[str, object] | None,
    validation_request: Mapping[str, object],
    logic_network_policy_registry_payload: Mapping[str, object] | None,
    logic_node_kind_registry_payload: Mapping[str, object] | None,
    logic_edge_kind_registry_payload: Mapping[str, object] | None,
    signal_type_registry_payload: Mapping[str, object] | None,
    carrier_type_registry_payload: Mapping[str, object] | None,
    signal_delay_policy_registry_payload: Mapping[str, object] | None,
    signal_noise_policy_registry_payload: Mapping[str, object] | None,
    protocol_registry_payload: Mapping[str, object] | None = None,
    logic_element_rows: object = None,
    logic_behavior_model_rows: object = None,
    interface_signature_rows: object = None,
    bus_definition_rows: object = None,
    compute_runtime_state: Mapping[str, object] | None = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None = None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_id: str = "compute.default",
) -> dict:
    try:
        from logic.network.logic_network_validator import validate_logic_network
    except ImportError:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_NETWORK_INVALID,
            "validation_result": {
                "result": "refused",
                "reason_code": REFUSAL_LOGIC_NETWORK_INVALID,
                "checks": [],
                "failed_checks": [],
                "warnings": [],
                "loop_classifications": [],
                "requires_l2_roi": False,
                "validation_hash": "",
            },
            "logic_network_state": normalize_logic_network_state(logic_network_state),
            "explain_artifact_rows": [],
        }

    tick = int(max(0, _as_int(current_tick, 0)))
    request = _as_map(validation_request)
    state = normalize_logic_network_state(logic_network_state)
    control_context = _normalize_control_context(_as_map(request.get("control_context")))
    if not control_context:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_CONTROL_CONTEXT_REQUIRED, "logic_network_state": state}
    network_id = _token(request.get("network_id"))
    bindings = _binding_by_network_id(state.get("logic_network_binding_rows"))
    binding_row = dict(bindings.get(network_id) or {})
    if not binding_row:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_NOT_FOUND, "logic_network_state": state}
    graph_id = _token(binding_row.get("graph_id"))
    graph_rows = _graph_by_id(state.get("logic_network_graph_rows"))
    graph_row = dict(graph_rows.get(graph_id) or {})
    if not graph_row:
        return {"result": "refused", "reason_code": REFUSAL_LOGIC_NETWORK_NOT_FOUND, "logic_network_state": state}
    instruction_units, memory_units = _estimate_compute_units(
        nodes=len(_as_list(graph_row.get("nodes"))),
        edges=len(_as_list(graph_row.get("edges"))),
        validation=True,
    )
    compute_result = request_compute(
        current_tick=tick,
        owner_kind="process",
        owner_id=_network_compute_owner_id(PROCESS_LOGIC_NETWORK_VALIDATE, network_id),
        instruction_units=instruction_units,
        memory_units=memory_units,
        compute_runtime_state=(compute_runtime_state if isinstance(compute_runtime_state, Mapping) else state.get("compute_runtime_state")),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_budget_profile_id=_token(request.get("compute_profile_id")) or _token(compute_budget_profile_id) or "compute.default",
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
    )
    if str(compute_result.get("result", "")) not in {"complete", "throttled"}:
        state["compute_runtime_state"] = _as_map(compute_result.get("runtime_state"))
        state = normalize_logic_network_state(state)
        return {
            "result": str(compute_result.get("result", "")) or "refused",
            "reason_code": _token(compute_result.get("reason_code")) or REFUSAL_LOGIC_NETWORK_INVALID,
            "compute_request": dict(compute_result),
            "logic_network_state": state,
        }
    validation_result = validate_logic_network(
        binding_row=binding_row,
        graph_row=graph_row,
        logic_network_policy_registry_payload=logic_network_policy_registry_payload,
        logic_node_kind_registry_payload=logic_node_kind_registry_payload,
        logic_edge_kind_registry_payload=logic_edge_kind_registry_payload,
        signal_type_registry_payload=signal_type_registry_payload,
        carrier_type_registry_payload=carrier_type_registry_payload,
        signal_delay_policy_registry_payload=signal_delay_policy_registry_payload,
        signal_noise_policy_registry_payload=signal_noise_policy_registry_payload,
        protocol_registry_payload=protocol_registry_payload,
        logic_element_rows=logic_element_rows,
        logic_behavior_model_rows=logic_behavior_model_rows,
        interface_signature_rows=interface_signature_rows,
        bus_definition_rows=bus_definition_rows,
    )
    state["compute_runtime_state"] = _as_map(compute_result.get("runtime_state"))
    state["logic_network_validation_records"] = list(state.get("logic_network_validation_records") or []) + [
        _logic_validation_record_row(
            tick=tick,
            network_id=network_id,
            graph_id=graph_id,
            policy_id=_token(binding_row.get("policy_id")),
            validation_result=validation_result,
        )
    ]
    explain_rows = _logic_loop_explain_artifact_rows(
        tick=tick,
        network_id=network_id,
        graph_id=graph_id,
        validation_result=validation_result,
    )
    state["logic_network_explain_artifact_rows"] = list(state.get("logic_network_explain_artifact_rows") or []) + explain_rows
    binding_extensions = dict(_as_map(binding_row.get("extensions")))
    binding_extensions["validation_status"] = "validated" if _token(validation_result.get("result")) == "complete" else "refused"
    binding_extensions["last_validation_hash"] = _token(validation_result.get("validation_hash"))
    if bool(validation_result.get("requires_l2_roi", False)):
        binding_extensions["requires_l2_roi"] = True
    state["logic_network_binding_rows"] = [
        dict(row)
        for row in list(state.get("logic_network_binding_rows") or [])
        if isinstance(row, Mapping) and _token(row.get("network_id")) != network_id
    ] + [build_logic_network_binding_row(
        network_id=network_id,
        graph_id=graph_id,
        policy_id=_token(binding_row.get("policy_id")),
        extensions=binding_extensions,
    )]
    state["logic_network_change_records"] = list(state.get("logic_network_change_records") or []) + [
        _logic_change_record_row(
            tick=tick,
            process_id=PROCESS_LOGIC_NETWORK_VALIDATE,
            network_id=network_id,
            graph_id=graph_id,
            operation="validate",
            control_context=control_context,
            prior_hash=canonical_sha256(graph_row),
            next_hash=canonical_sha256(graph_row),
            extensions={
                "validation_hash": _token(validation_result.get("validation_hash")),
                "validation_result": _token(validation_result.get("result")),
            },
        )
    ]
    state = normalize_logic_network_state(state)
    return {
        "result": _token(validation_result.get("result")) or "refused",
        "reason_code": _token(validation_result.get("reason_code")),
        "validation_result": validation_result,
        "compute_request": dict(compute_result),
        "logic_network_state": state,
        "explain_artifact_rows": explain_rows,
    }


__all__ = [
    "PROCESS_LOGIC_NETWORK_CREATE",
    "PROCESS_LOGIC_NETWORK_ADD_NODE",
    "PROCESS_LOGIC_NETWORK_ADD_EDGE",
    "PROCESS_LOGIC_NETWORK_REMOVE_EDGE",
    "PROCESS_LOGIC_NETWORK_VALIDATE",
    "REFUSAL_LOGIC_NETWORK_INVALID",
    "REFUSAL_LOGIC_NETWORK_POLICY_UNREGISTERED",
    "REFUSAL_LOGIC_NETWORK_NODE_INVALID",
    "REFUSAL_LOGIC_NETWORK_EDGE_INVALID",
    "REFUSAL_LOGIC_NETWORK_NOT_FOUND",
    "REFUSAL_LOGIC_NETWORK_CONTROL_CONTEXT_REQUIRED",
    "build_logic_node_payload_row",
    "build_logic_edge_payload_row",
    "build_logic_network_binding_row",
    "canonical_logic_network_hash",
    "canonical_logic_network_snapshot",
    "deterministic_logic_binding_id",
    "deterministic_logic_edge_id",
    "deterministic_logic_graph_id",
    "deterministic_logic_node_id",
    "normalize_logic_network_binding_rows",
    "normalize_logic_network_state",
    "process_logic_network_create",
    "process_logic_network_add_node",
    "process_logic_network_add_edge",
    "process_logic_network_remove_edge",
    "process_logic_network_validate",
]
