"""LOGIC-3 deterministic LogicNetworkGraph validation and loop classification."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Sequence, Set, Tuple

from src.core.graph.network_graph_engine import NetworkGraphError, normalize_network_graph
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_LOGIC_LOOP_DETECTED = "refusal.logic.loop_detected"
REFUSAL_LOGIC_NETWORK_INVALID = "refusal.logic.network_invalid"

_NODE_KINDS = {"port_in", "port_out", "junction", "bus_junction", "protocol_endpoint"}
_EDGE_KINDS = {"link", "bus_link", "protocol_link", "sig_link"}
_COMBINATIONAL_BEHAVIOR_KINDS = {"combinational", "mux"}
_SEQUENTIAL_BEHAVIOR_KINDS = {"sequential", "timer", "counter"}


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


def _rows_by_id(rows: object, id_key: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: _token(item.get(id_key))):
        token = _token(row.get(id_key))
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _normalize_node_payload(payload: Mapping[str, object]) -> dict:
    row = _as_map(payload)
    out = {
        "node_kind": _token(row.get("node_kind")).lower(),
        "element_instance_id": None if row.get("element_instance_id") is None else _token(row.get("element_instance_id")) or None,
        "port_id": None if row.get("port_id") is None else _token(row.get("port_id")) or None,
        "bus_id": None if row.get("bus_id") is None else _token(row.get("bus_id")) or None,
        "protocol_id": None if row.get("protocol_id") is None else _token(row.get("protocol_id")) or None,
        "extensions": _canon(_as_map(row.get("extensions"))),
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


def _normalize_edge_payload(payload: Mapping[str, object]) -> dict:
    row = _as_map(payload)
    out = {
        "edge_kind": _token(row.get("edge_kind")).lower(),
        "signal_type_id": _token(row.get("signal_type_id")),
        "carrier_type_id": _token(row.get("carrier_type_id")),
        "delay_policy_id": _token(row.get("delay_policy_id")),
        "noise_policy_id": _token(row.get("noise_policy_id")),
        "protocol_id": None if row.get("protocol_id") is None else _token(row.get("protocol_id")) or None,
        "capacity": None if row.get("capacity") is None else int(max(0, _as_int(row.get("capacity"), 0))),
        "extensions": _canon(_as_map(row.get("extensions"))),
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


def _check(check_id: str, ok: bool, message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "check_id": _token(check_id),
        "status": "pass" if bool(ok) else "fail",
        "message": _token(message),
        "details": _canon(_as_map(details)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(payload)
    return payload


def _port_signal_type_ids(
    *,
    node_payload: Mapping[str, object],
    interface_rows_by_system: Mapping[str, dict],
    logic_elements_by_id: Mapping[str, dict],
) -> List[str]:
    payload = _as_map(node_payload)
    extensions = _as_map(payload.get("extensions"))
    explicit = _sorted_tokens(extensions.get("allowed_signal_type_ids"))
    if explicit:
        return explicit
    element_definition_id = _token(extensions.get("element_definition_id")) or _token(payload.get("element_instance_id"))
    element_row = dict(logic_elements_by_id.get(element_definition_id) or {})
    interface_system_id = _token(extensions.get("interface_system_id")) or _token(element_row.get("element_id")) or element_definition_id
    interface_row = dict(interface_rows_by_system.get(interface_system_id) or {})
    return _sorted_tokens(_as_map(interface_row.get("extensions")).get("signal_type_ids"))


def _protocol_for_node(node_payload: Mapping[str, object]) -> str:
    payload = _as_map(node_payload)
    return _token(payload.get("protocol_id")) or _token(_as_map(payload.get("extensions")).get("protocol_id"))


def _bus_for_node(node_payload: Mapping[str, object]) -> str:
    payload = _as_map(node_payload)
    return _token(payload.get("bus_id")) or _token(_as_map(payload.get("extensions")).get("bus_id"))


def _node_shard_id(node_payload: Mapping[str, object]) -> str:
    return _token(_as_map(_as_map(node_payload).get("extensions")).get("shard_id"))


def _edge_boundary_safe(edge_payload: Mapping[str, object], from_node_payload: Mapping[str, object], to_node_payload: Mapping[str, object]) -> bool:
    payload_ext = _as_map(_as_map(edge_payload).get("extensions"))
    if bool(payload_ext.get("boundary_artifact_exchange", False)) or _token(payload_ext.get("boundary_artifact_id")):
        return True
    from_ext = _as_map(_as_map(from_node_payload).get("extensions"))
    to_ext = _as_map(_as_map(to_node_payload).get("extensions"))
    return bool(_token(from_ext.get("boundary_artifact_id")) and _token(to_ext.get("boundary_artifact_id")))


def _element_behavior_kind(
    *,
    element_instance_id: str,
    node_payload: Mapping[str, object],
    logic_elements_by_id: Mapping[str, dict],
    behavior_models_by_id: Mapping[str, dict],
) -> str:
    payload_ext = _as_map(_as_map(node_payload).get("extensions"))
    explicit = _token(payload_ext.get("behavior_kind")).lower()
    if explicit:
        return explicit
    element_definition_id = _token(payload_ext.get("element_definition_id")) or _token(element_instance_id)
    element_row = dict(logic_elements_by_id.get(element_definition_id) or {})
    behavior_id = _token(element_row.get("behavior_model_id"))
    behavior_row = dict(behavior_models_by_id.get(behavior_id) or {})
    behavior_kind = _token(behavior_row.get("model_kind")).lower()
    if behavior_kind:
        return behavior_kind
    return "combinational"


def _build_augmented_adjacency(
    *,
    graph_row: Mapping[str, object],
    node_payload_by_id: Mapping[str, dict],
) -> Dict[str, List[str]]:
    adjacency: Dict[str, List[str]] = {}
    for edge in sorted((dict(item) for item in _as_list(graph_row.get("edges")) if isinstance(item, Mapping)), key=lambda item: _token(item.get("edge_id"))):
        from_node_id = _token(edge.get("from_node_id"))
        to_node_id = _token(edge.get("to_node_id"))
        if from_node_id and to_node_id:
            adjacency.setdefault(from_node_id, []).append(to_node_id)
    element_in_nodes: Dict[str, List[str]] = {}
    element_out_nodes: Dict[str, List[str]] = {}
    for node_id in sorted(node_payload_by_id.keys()):
        payload = dict(node_payload_by_id[node_id])
        element_instance_id = _token(payload.get("element_instance_id"))
        if not element_instance_id:
            continue
        node_kind = _token(payload.get("node_kind"))
        if node_kind == "port_in":
            element_in_nodes.setdefault(element_instance_id, []).append(node_id)
        elif node_kind == "port_out":
            element_out_nodes.setdefault(element_instance_id, []).append(node_id)
    for element_instance_id in sorted(set(element_in_nodes.keys()) | set(element_out_nodes.keys())):
        in_nodes = sorted(set(element_in_nodes.get(element_instance_id) or []))
        out_nodes = sorted(set(element_out_nodes.get(element_instance_id) or []))
        for from_node_id in in_nodes:
            for to_node_id in out_nodes:
                adjacency.setdefault(from_node_id, []).append(to_node_id)
    for node_id in list(adjacency.keys()):
        adjacency[node_id] = sorted(set(adjacency[node_id]))
    return adjacency


def _tarjan_scc(adjacency: Mapping[str, Sequence[str]], node_ids: Sequence[str]) -> List[List[str]]:
    index = 0
    stack: List[str] = []
    on_stack: Set[str] = set()
    indices: Dict[str, int] = {}
    lowlink: Dict[str, int] = {}
    out: List[List[str]] = []

    def strongconnect(node_id: str) -> None:
        nonlocal index
        indices[node_id] = index
        lowlink[node_id] = index
        index += 1
        stack.append(node_id)
        on_stack.add(node_id)
        for target_id in sorted(set(adjacency.get(node_id) or [])):
            if target_id not in indices:
                strongconnect(target_id)
                lowlink[node_id] = min(lowlink[node_id], lowlink[target_id])
            elif target_id in on_stack:
                lowlink[node_id] = min(lowlink[node_id], indices[target_id])
        if lowlink[node_id] == indices[node_id]:
            component: List[str] = []
            while stack:
                target_id = stack.pop()
                on_stack.remove(target_id)
                component.append(target_id)
                if target_id == node_id:
                    break
            out.append(sorted(component))

    for node_id in sorted(set(node_ids)):
        if node_id not in indices:
            strongconnect(node_id)
    return sorted(out, key=lambda item: (len(item), "|".join(item)))


def _self_loop_exists(node_id: str, adjacency: Mapping[str, Sequence[str]]) -> bool:
    return node_id in set(adjacency.get(node_id) or [])


def _classify_loops(
    *,
    graph_row: Mapping[str, object],
    node_payload_by_id: Mapping[str, dict],
    policy_row: Mapping[str, object],
    logic_elements_by_id: Mapping[str, dict],
    behavior_models_by_id: Mapping[str, dict],
    compiled_proof_id: str,
) -> List[dict]:
    node_ids = [_token(row.get("node_id")) for row in _as_list(graph_row.get("nodes")) if isinstance(row, Mapping) and _token(row.get("node_id"))]
    adjacency = _build_augmented_adjacency(graph_row=graph_row, node_payload_by_id=node_payload_by_id)
    components = _tarjan_scc(adjacency, node_ids)
    out: List[dict] = []
    loop_mode = _token(policy_row.get("loop_resolution_mode")).lower() or "refuse"
    for component in components:
        if (len(component) == 1) and (not _self_loop_exists(component[0], adjacency)):
            continue
        element_instance_ids = _sorted_tokens(
            _token(node_payload_by_id.get(node_id, {}).get("element_instance_id"))
            for node_id in component
            if _token(node_payload_by_id.get(node_id, {}).get("element_instance_id"))
        )
        behavior_kinds = {
            _element_behavior_kind(
                element_instance_id=element_instance_id,
                node_payload=next(
                    dict(node_payload_by_id[node_id])
                    for node_id in component
                    if _token(node_payload_by_id.get(node_id, {}).get("element_instance_id")) == element_instance_id
                ),
                logic_elements_by_id=logic_elements_by_id,
                behavior_models_by_id=behavior_models_by_id,
            )
            for element_instance_id in element_instance_ids
        }
        combinational_hits = sorted(kind for kind in behavior_kinds if kind in _COMBINATIONAL_BEHAVIOR_KINDS)
        sequential_hits = sorted(kind for kind in behavior_kinds if kind in _SEQUENTIAL_BEHAVIOR_KINDS)
        if combinational_hits and sequential_hits:
            classification = "mixed"
        elif sequential_hits and not combinational_hits:
            classification = "sequential"
        else:
            classification = "combinational"
        policy_resolution = "allow"
        requires_l2_roi = False
        if classification in {"combinational", "mixed"}:
            if loop_mode == "force_roi":
                policy_resolution = "force_roi"
                requires_l2_roi = True
            elif loop_mode == "allow_compiled_only":
                policy_resolution = "allow_compiled_only" if compiled_proof_id else "refuse"
            else:
                policy_resolution = "refuse"
        out.append(
            {
                "classification": classification,
                "node_ids": component,
                "element_instance_ids": element_instance_ids,
                "behavior_kinds": sorted(behavior_kinds),
                "policy_resolution": policy_resolution,
                "requires_l2_roi": requires_l2_roi,
            }
        )
    return sorted(out, key=lambda item: (_token(item.get("classification")), "|".join(_sorted_tokens(item.get("node_ids")))))


def validate_logic_network(
    *,
    binding_row: Mapping[str, object],
    graph_row: Mapping[str, object],
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
) -> dict:
    checks: List[dict] = []
    warnings: List[dict] = []
    binding = {
        "network_id": _token(binding_row.get("network_id")),
        "graph_id": _token(binding_row.get("graph_id")),
        "policy_id": _token(binding_row.get("policy_id")),
        "extensions": _canon(_as_map(binding_row.get("extensions"))),
    }
    policy_rows = _registry_rows_by_id(logic_network_policy_registry_payload, "logic_network_policies", "policy_id")
    policy_row = dict(policy_rows.get(binding["policy_id"]) or {})
    checks.append(_check("binding.network_id.present", bool(binding["network_id"]), "network_id present"))
    checks.append(_check("binding.graph_id.present", bool(binding["graph_id"]), "graph_id present"))
    checks.append(_check("binding.policy.registered", bool(policy_row), "logic network policy registered"))
    if not policy_row:
        failed = [dict(item) for item in checks if _token(item.get("status")) != "pass"]
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_NETWORK_INVALID,
            "checks": checks,
            "failed_checks": failed,
            "warnings": warnings,
            "loop_classifications": [],
            "requires_l2_roi": False,
            "validation_hash": canonical_sha256({"binding": binding, "checks": checks}),
        }
    try:
        graph = normalize_network_graph(graph_row)
    except NetworkGraphError as exc:
        checks.append(_check("graph.normalize", False, str(exc), _as_map(exc.details)))
        failed = [dict(item) for item in checks if _token(item.get("status")) != "pass"]
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_NETWORK_INVALID,
            "checks": checks,
            "failed_checks": failed,
            "warnings": warnings,
            "loop_classifications": [],
            "requires_l2_roi": False,
            "validation_hash": canonical_sha256({"binding": binding, "error": str(exc), "details": _canon(_as_map(exc.details))}),
        }

    node_kind_rows = _registry_rows_by_id(logic_node_kind_registry_payload, "node_kinds", "node_kind_id")
    edge_kind_rows = _registry_rows_by_id(logic_edge_kind_registry_payload, "edge_kinds", "edge_kind_id")
    signal_rows = _registry_rows_by_id(signal_type_registry_payload, "signal_types", "signal_type_id")
    carrier_rows = _registry_rows_by_id(carrier_type_registry_payload, "carrier_types", "carrier_type_id")
    delay_rows = _registry_rows_by_id(signal_delay_policy_registry_payload, "signal_delay_policies", "delay_policy_id")
    noise_rows = _registry_rows_by_id(signal_noise_policy_registry_payload, "signal_noise_policies", "noise_policy_id")
    protocol_rows = _registry_rows_by_id(protocol_registry_payload, "protocols", "protocol_id")
    bus_rows = _rows_by_id(bus_definition_rows, "bus_id")
    logic_elements_by_id = _rows_by_id(logic_element_rows, "element_id")
    behavior_models_by_id = _rows_by_id(logic_behavior_model_rows, "behavior_model_id")
    interface_rows_by_system = _rows_by_id(interface_signature_rows, "system_id")

    allowed_carriers = set(_sorted_tokens(policy_row.get("allowed_carrier_type_ids")))
    require_boundary_artifact = bool(policy_row.get("require_boundary_artifact_for_cross_shard", True))
    compiled_proof_id = _token(binding["extensions"].get("compiled_equivalence_proof_id"))

    node_payload_by_id: Dict[str, dict] = {}
    incident_counts: Dict[str, int] = {}
    for node in sorted((dict(item) for item in _as_list(graph.get("nodes")) if isinstance(item, Mapping)), key=lambda item: _token(item.get("node_id"))):
        node_id = _token(node.get("node_id"))
        payload = _normalize_node_payload(_as_map(node.get("payload")))
        node_payload_by_id[node_id] = payload
        incident_counts[node_id] = 0
        node_kind = _token(payload.get("node_kind"))
        checks.append(_check("node.kind.valid.{}".format(node_id), node_kind in _NODE_KINDS, "node kind valid"))
        checks.append(_check("node.kind.registered.{}".format(node_id), node_kind in node_kind_rows, "node kind registered"))
        if node_kind in {"port_in", "port_out"}:
            checks.append(_check("node.port.bound.{}".format(node_id), bool(_token(payload.get("element_instance_id"))) and bool(_token(payload.get("port_id"))), "port node binds element_instance_id and port_id"))
        if node_kind == "bus_junction":
            checks.append(_check("node.bus.present.{}".format(node_id), bool(_bus_for_node(payload)), "bus_junction declares bus_id"))
        if node_kind == "protocol_endpoint":
            checks.append(_check("node.protocol.present.{}".format(node_id), bool(_protocol_for_node(payload)), "protocol_endpoint declares protocol_id"))

    for edge in sorted((dict(item) for item in _as_list(graph.get("edges")) if isinstance(item, Mapping)), key=lambda item: (_token(item.get("from_node_id")), _token(item.get("to_node_id")), _token(item.get("edge_id")))):
        edge_id = _token(edge.get("edge_id"))
        from_node_id = _token(edge.get("from_node_id"))
        to_node_id = _token(edge.get("to_node_id"))
        incident_counts[from_node_id] = int(incident_counts.get(from_node_id, 0)) + 1
        incident_counts[to_node_id] = int(incident_counts.get(to_node_id, 0)) + 1
        payload = _normalize_edge_payload(_as_map(edge.get("payload")))
        edge_kind = _token(payload.get("edge_kind"))
        signal_type_id = _token(payload.get("signal_type_id"))
        carrier_type_id = _token(payload.get("carrier_type_id"))
        delay_policy_id = _token(payload.get("delay_policy_id"))
        noise_policy_id = _token(payload.get("noise_policy_id"))
        protocol_id = _token(payload.get("protocol_id"))
        from_payload = dict(node_payload_by_id.get(from_node_id) or {})
        to_payload = dict(node_payload_by_id.get(to_node_id) or {})

        checks.append(_check("edge.kind.valid.{}".format(edge_id), edge_kind in _EDGE_KINDS, "edge kind valid"))
        checks.append(_check("edge.kind.registered.{}".format(edge_id), edge_kind in edge_kind_rows, "edge kind registered"))
        checks.append(_check("edge.signal.registered.{}".format(edge_id), signal_type_id in signal_rows, "signal type registered"))
        checks.append(_check("edge.carrier.registered.{}".format(edge_id), carrier_type_id in carrier_rows, "carrier type registered"))
        checks.append(_check("edge.delay.registered.{}".format(edge_id), delay_policy_id in delay_rows, "delay policy registered"))
        checks.append(_check("edge.noise.registered.{}".format(edge_id), noise_policy_id in noise_rows, "noise policy registered"))
        checks.append(_check("edge.carrier.policy_allowed.{}".format(edge_id), (not allowed_carriers) or (carrier_type_id in allowed_carriers), "carrier allowed by network policy"))

        from_signal_ids = _port_signal_type_ids(node_payload=from_payload, interface_rows_by_system=interface_rows_by_system, logic_elements_by_id=logic_elements_by_id)
        to_signal_ids = _port_signal_type_ids(node_payload=to_payload, interface_rows_by_system=interface_rows_by_system, logic_elements_by_id=logic_elements_by_id)
        if from_signal_ids:
            checks.append(_check("edge.signal.matches_from.{}".format(edge_id), signal_type_id in set(from_signal_ids), "edge signal_type matches source declarations", {"edge_signal_type_id": signal_type_id, "allowed_signal_type_ids": from_signal_ids}))
        if to_signal_ids:
            checks.append(_check("edge.signal.matches_to.{}".format(edge_id), signal_type_id in set(to_signal_ids), "edge signal_type matches target declarations", {"edge_signal_type_id": signal_type_id, "allowed_signal_type_ids": to_signal_ids}))

        if edge_kind == "bus_link":
            bus_id = _token(_as_map(payload.get("extensions")).get("bus_id")) or _bus_for_node(from_payload) or _bus_for_node(to_payload)
            checks.append(_check("edge.bus.present.{}".format(edge_id), bool(bus_id), "bus_link declares bus_id"))
            if bus_id:
                checks.append(_check("edge.bus.registered.{}".format(edge_id), bus_id in bus_rows, "bus definition registered"))
                checks.append(_check("edge.bus.matches_nodes.{}".format(edge_id), (not _bus_for_node(from_payload) or _bus_for_node(from_payload) == bus_id) and (not _bus_for_node(to_payload) or _bus_for_node(to_payload) == bus_id), "bus_link matches endpoint bus ids"))

        if edge_kind == "protocol_link":
            checks.append(_check("edge.protocol.present.{}".format(edge_id), bool(protocol_id), "protocol_link protocol_id present"))
            checks.append(_check("edge.protocol.registered.{}".format(edge_id), protocol_id in protocol_rows, "protocol_id registered"))
        if protocol_id:
            from_protocol = _protocol_for_node(from_payload)
            to_protocol = _protocol_for_node(to_payload)
            if from_protocol:
                checks.append(_check("edge.protocol.matches_from.{}".format(edge_id), from_protocol == protocol_id, "source protocol matches edge"))
            if to_protocol:
                checks.append(_check("edge.protocol.matches_to.{}".format(edge_id), to_protocol == protocol_id, "target protocol matches edge"))

        from_shard_id = _node_shard_id(from_payload)
        to_shard_id = _node_shard_id(to_payload)
        cross_shard = bool(from_shard_id and to_shard_id and from_shard_id != to_shard_id)
        if cross_shard and require_boundary_artifact:
            checks.append(_check("edge.cross_shard.boundary_safe.{}".format(edge_id), (edge_kind == "sig_link") or _edge_boundary_safe(payload, from_payload, to_payload), "cross-shard links require sig_link or explicit boundary artifact exchange"))

    for node_id in sorted(incident_counts.keys()):
        payload = dict(node_payload_by_id.get(node_id) or {})
        if _token(payload.get("node_kind")) in {"port_in", "port_out", "protocol_endpoint"}:
            checks.append(_check("node.incident_edge.present.{}".format(node_id), int(incident_counts.get(node_id, 0)) > 0, "port-like nodes must be connected"))

    loop_classifications = _classify_loops(
        graph_row=graph,
        node_payload_by_id=node_payload_by_id,
        policy_row=policy_row,
        logic_elements_by_id=logic_elements_by_id,
        behavior_models_by_id=behavior_models_by_id,
        compiled_proof_id=compiled_proof_id,
    )
    requires_l2_roi = any(bool(row.get("requires_l2_roi", False)) for row in loop_classifications)
    for index, loop_row in enumerate(loop_classifications):
        classification = _token(loop_row.get("classification"))
        resolution = _token(loop_row.get("policy_resolution"))
        check_id = "loop.{}.{}".format(classification or "unknown", index)
        if classification == "sequential":
            checks.append(_check(check_id, True, "sequential loop allowed", loop_row))
        elif resolution == "force_roi":
            warnings.append(_check(check_id, True, "loop allowed only with forced L2 ROI", loop_row))
        elif resolution == "allow_compiled_only":
            checks.append(_check(check_id, True, "loop allowed because compiled proof is present", loop_row))
        else:
            checks.append(_check(check_id, False, "loop policy refuses this topology", loop_row))

    checks = sorted(checks, key=lambda item: _token(item.get("check_id")))
    warnings = sorted(warnings, key=lambda item: _token(item.get("check_id")))
    failed = [dict(item) for item in checks if _token(item.get("status")) != "pass"]
    reason_code = ""
    if any(_token(item.get("policy_resolution")) == "refuse" for item in loop_classifications):
        reason_code = REFUSAL_LOGIC_LOOP_DETECTED
    elif failed:
        reason_code = REFUSAL_LOGIC_NETWORK_INVALID
    result = "complete" if not failed else "refused"
    validation_hash = canonical_sha256(
        {
            "binding": binding,
            "graph_hash": canonical_sha256(graph),
            "checks": checks,
            "warnings": warnings,
            "loop_classifications": loop_classifications,
        }
    )
    return {
        "result": result,
        "reason_code": reason_code,
        "checks": checks,
        "failed_checks": failed,
        "warnings": warnings,
        "loop_classifications": loop_classifications,
        "requires_l2_roi": requires_l2_roi,
        "validation_hash": validation_hash,
    }


__all__ = [
    "REFUSAL_LOGIC_LOOP_DETECTED",
    "REFUSAL_LOGIC_NETWORK_INVALID",
    "validate_logic_network",
]
