"""Deterministic MOB-2 MobilityNetworkGraph helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from src.core.graph.network_graph_engine import normalize_network_graph
from src.core.state.state_machine_engine import normalize_state_machine
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_MOBILITY_NETWORK_INVALID = "refusal.mob.network_invalid"
REFUSAL_MOBILITY_NO_ROUTE = "refusal.mob.no_route"
REFUSAL_MOBILITY_SWITCH_INVALID = "refusal.mob.switch_invalid"


class MobilityNetworkError(ValueError):
    """Deterministic mobility-network refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _point3(value: object) -> dict:
    payload = _as_map(value)
    return {
        "x": int(_as_int(payload.get("x", 0), 0)),
        "y": int(_as_int(payload.get("y", 0), 0)),
        "z": int(_as_int(payload.get("z", 0), 0)),
    }


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda token: str(token)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _geometry_points(parameters: Mapping[str, object] | None) -> List[dict]:
    payload = _as_map(parameters)
    for key in ("control_points_mm", "points_mm", "path_points_mm"):
        rows = payload.get(key)
        if not isinstance(rows, list):
            continue
        points = [_point3(row) for row in rows if isinstance(row, Mapping)]
        if points:
            return points
    start = payload.get("start_mm")
    end = payload.get("end_mm")
    if isinstance(start, Mapping) and isinstance(end, Mapping):
        return [_point3(start), _point3(end)]
    return []


def _registry_rows_by_id(registry_payload: Mapping[str, object] | None, entry_key: str, id_key: str) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get(entry_key)
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get(entry_key)
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get(id_key, ""))):
        token = str(row.get(id_key, "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def mobility_node_kind_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    return _registry_rows_by_id(registry_payload, "node_kinds", "node_kind_id")


def mobility_edge_kind_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    return _registry_rows_by_id(registry_payload, "edge_kinds", "edge_kind_id")


def mobility_max_speed_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    return _registry_rows_by_id(registry_payload, "max_speed_policies", "max_speed_policy_id")


def _deterministic_graph_id(formalization_id: str) -> str:
    return "graph.mobility.{}".format(canonical_sha256({"formalization_id": str(formalization_id).strip()})[:16])


def _deterministic_node_id(*, formalization_id: str, node_key: str) -> str:
    return "node.mobility.{}".format(
        canonical_sha256(
            {
                "formalization_id": str(formalization_id).strip(),
                "node_key": str(node_key).strip(),
            }
        )[:16]
    )


def _deterministic_edge_id(*, formalization_id: str, geometry_id: str, from_node_id: str, to_node_id: str) -> str:
    return "edge.mobility.{}".format(
        canonical_sha256(
            {
                "formalization_id": str(formalization_id).strip(),
                "geometry_id": str(geometry_id).strip(),
                "from_node_id": str(from_node_id).strip(),
                "to_node_id": str(to_node_id).strip(),
            }
        )[:16]
    )


def deterministic_mobility_binding_id(*, formalization_id: str, graph_id: str) -> str:
    return "binding.mobility.{}".format(
        canonical_sha256(
            {
                "formalization_id": str(formalization_id).strip(),
                "graph_id": str(graph_id).strip(),
            }
        )[:16]
    )


def build_mobility_network_binding(
    *,
    binding_id: str,
    formalization_id: str,
    graph_id: str,
    node_ids: object,
    edge_ids: object,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "binding_id": str(binding_id).strip(),
        "formalization_id": str(formalization_id).strip(),
        "graph_id": str(graph_id).strip(),
        "node_ids": _sorted_tokens(node_ids),
        "edge_ids": _sorted_tokens(edge_ids),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_mobility_network_binding_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("binding_id", ""))):
        binding_id = str(row.get("binding_id", "")).strip()
        formalization_id = str(row.get("formalization_id", "")).strip()
        graph_id = str(row.get("graph_id", "")).strip()
        if (not binding_id) or (not formalization_id) or (not graph_id):
            continue
        out[binding_id] = build_mobility_network_binding(
            binding_id=binding_id,
            formalization_id=formalization_id,
            graph_id=graph_id,
            node_ids=row.get("node_ids"),
            edge_ids=row.get("edge_ids"),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def _resolve_junction_node_kind(junction_type_id: str) -> str:
    token = str(junction_type_id or "").strip()
    if token in {"switch", "junc.switch"}:
        return "switch"
    if token in {"station", "junc.station"}:
        return "station"
    if token in {"endpoint", "junc.endpoint"}:
        return "endpoint"
    return "junction"


def build_mobility_network_graph(
    *,
    formalization_id: str,
    guide_geometry_rows: object,
    junction_rows: object,
    geometry_metric_rows: object,
    graph_id: str | None = None,
    graph_partition_id: str | None = None,
    edge_kind_default: str = "track",
    max_speed_policy_id: str | None = "speed_policy.spec_based",
    node_kind_registry: Mapping[str, object] | None = None,
    edge_kind_registry: Mapping[str, object] | None = None,
    max_speed_policy_registry: Mapping[str, object] | None = None,
) -> dict:
    formalization_token = str(formalization_id).strip()
    if not formalization_token:
        raise MobilityNetworkError(REFUSAL_MOBILITY_NETWORK_INVALID, "formalization_id is required", {})

    geometry_rows = sorted(
        [dict(item) for item in list(guide_geometry_rows or []) if isinstance(item, Mapping)],
        key=lambda item: str(item.get("geometry_id", "")),
    )
    if not geometry_rows:
        raise MobilityNetworkError(
            REFUSAL_MOBILITY_NETWORK_INVALID,
            "no guide geometries are available for mobility network construction",
            {"formalization_id": formalization_token},
        )
    junction_rows_norm = sorted(
        [dict(item) for item in list(junction_rows or []) if isinstance(item, Mapping)],
        key=lambda item: str(item.get("junction_id", "")),
    )
    metric_by_geometry = dict(
        (
            str(row.get("geometry_id", "")).strip(),
            dict(row),
        )
        for row in list(geometry_metric_rows or [])
        if isinstance(row, Mapping) and str(row.get("geometry_id", "")).strip()
    )
    node_kind_rows = mobility_node_kind_rows_by_id(node_kind_registry)
    edge_kind_rows = mobility_edge_kind_rows_by_id(edge_kind_registry)
    max_speed_rows = mobility_max_speed_policy_rows_by_id(max_speed_policy_registry)

    default_edge_kind = str(edge_kind_default).strip() or "track"
    if edge_kind_rows and default_edge_kind not in edge_kind_rows:
        default_edge_kind = sorted(edge_kind_rows.keys())[0]
    resolved_speed_policy_id = None if max_speed_policy_id is None else str(max_speed_policy_id).strip() or None
    if resolved_speed_policy_id and max_speed_rows and resolved_speed_policy_id not in max_speed_rows:
        resolved_speed_policy_id = sorted(max_speed_rows.keys())[0]

    resolved_graph_id = str(graph_id or "").strip() or _deterministic_graph_id(formalization_token)
    resolved_partition_id = None if graph_partition_id is None else str(graph_partition_id).strip() or None

    nodes_by_id: Dict[str, dict] = {}
    junction_node_id_by_id: Dict[str, str] = {}
    for row in junction_rows_norm:
        junction_id = str(row.get("junction_id", "")).strip()
        if not junction_id:
            continue
        node_kind = _resolve_junction_node_kind(str(row.get("junction_type_id", "")))
        if node_kind_rows and node_kind not in node_kind_rows:
            node_kind = "junction" if "junction" in node_kind_rows else sorted(node_kind_rows.keys())[0]
        parent_spatial_id = str(row.get("parent_spatial_id", "")).strip() or "spatial.unknown"
        node_id = _deterministic_node_id(formalization_id=formalization_token, node_key="junction:{}".format(junction_id))
        machine_id = None if row.get("state_machine_id") is None else str(row.get("state_machine_id", "")).strip() or None
        payload = {
            "schema_version": "1.0.0",
            "node_kind": node_kind,
            "parent_spatial_id": parent_spatial_id,
            "position_ref": None,
            "junction_id": junction_id,
            "state_machine_id": machine_id if node_kind == "switch" else None,
            "tags": ["mobility", "junction", node_kind],
            "extensions": {},
        }
        nodes_by_id[node_id] = {
            "schema_version": "1.0.0",
            "node_id": node_id,
            "node_type_id": "node.mobility.{}".format(node_kind),
            "payload": payload,
            "tags": ["mobility", "junction", node_kind],
            "extensions": {},
        }
        junction_node_id_by_id[junction_id] = node_id

    edges_by_id: Dict[str, dict] = {}
    geometry_to_junctions: Dict[str, List[str]] = {}
    for junction in junction_rows_norm:
        junction_id = str(junction.get("junction_id", "")).strip()
        for geometry_id in _sorted_tokens(junction.get("connected_geometry_ids")):
            geometry_to_junctions.setdefault(geometry_id, []).append(junction_id)
    for geometry_id in list(geometry_to_junctions.keys()):
        geometry_to_junctions[geometry_id] = sorted(set(geometry_to_junctions[geometry_id]))

    for geometry in geometry_rows:
        geometry_id = str(geometry.get("geometry_id", "")).strip()
        if not geometry_id:
            continue
        parent_spatial_id = str(geometry.get("parent_spatial_id", "")).strip() or "spatial.unknown"
        points = _geometry_points(_as_map(geometry.get("parameters")))
        if len(points) < 2:
            continue
        junction_refs = _sorted_tokens(geometry.get("junction_refs")) or list(geometry_to_junctions.get(geometry_id) or [])
        from_junction_id = str((junction_refs[0] if junction_refs else "")).strip()
        to_junction_id = str((junction_refs[-1] if junction_refs else "")).strip()
        from_node_id = str(junction_node_id_by_id.get(from_junction_id, "")).strip()
        to_node_id = str(junction_node_id_by_id.get(to_junction_id, "")).strip()
        if not from_node_id:
            from_node_id = _deterministic_node_id(
                formalization_id=formalization_token,
                node_key="geometry:{}:endpoint:0".format(geometry_id),
            )
            nodes_by_id[from_node_id] = {
                "schema_version": "1.0.0",
                "node_id": from_node_id,
                "node_type_id": "node.mobility.endpoint",
                "payload": {
                    "schema_version": "1.0.0",
                    "node_kind": "endpoint",
                    "parent_spatial_id": parent_spatial_id,
                    "position_ref": {"point_mm": _point3(points[0])},
                    "junction_id": None,
                    "state_machine_id": None,
                    "tags": ["mobility", "endpoint"],
                    "extensions": {"geometry_id": geometry_id, "endpoint_index": 0},
                },
                "tags": ["mobility", "endpoint"],
                "extensions": {},
            }
        if not to_node_id:
            to_node_id = _deterministic_node_id(
                formalization_id=formalization_token,
                node_key="geometry:{}:endpoint:1".format(geometry_id),
            )
            nodes_by_id[to_node_id] = {
                "schema_version": "1.0.0",
                "node_id": to_node_id,
                "node_type_id": "node.mobility.endpoint",
                "payload": {
                    "schema_version": "1.0.0",
                    "node_kind": "endpoint",
                    "parent_spatial_id": parent_spatial_id,
                    "position_ref": {"point_mm": _point3(points[-1])},
                    "junction_id": None,
                    "state_machine_id": None,
                    "tags": ["mobility", "endpoint"],
                    "extensions": {"geometry_id": geometry_id, "endpoint_index": 1},
                },
                "tags": ["mobility", "endpoint"],
                "extensions": {},
            }
        metric = dict(metric_by_geometry.get(geometry_id) or {})
        length_mm = int(max(0, _as_int(metric.get("length_mm", 0), 0)))
        delay_ticks = int(max(1, length_mm // 1000)) if length_mm > 0 else 1
        edge_kind = default_edge_kind
        if edge_kind_rows and edge_kind not in edge_kind_rows:
            edge_kind = sorted(edge_kind_rows.keys())[0]
        edge_speed_policy_id = resolved_speed_policy_id
        if edge_speed_policy_id and max_speed_rows and edge_speed_policy_id not in max_speed_rows:
            edge_speed_policy_id = sorted(max_speed_rows.keys())[0]
        edge_id = _deterministic_edge_id(
            formalization_id=formalization_token,
            geometry_id=geometry_id,
            from_node_id=from_node_id,
            to_node_id=to_node_id,
        )
        edge_payload = {
            "schema_version": "1.0.0",
            "edge_kind": edge_kind,
            "guide_geometry_id": geometry_id,
            "spec_id": None if geometry.get("spec_id") is None else str(geometry.get("spec_id", "")).strip() or None,
            "capacity_units": None,
            "max_speed_policy_id": edge_speed_policy_id,
            "tags": ["mobility", edge_kind],
            "extensions": {"length_mm": length_mm},
        }
        edges_by_id[edge_id] = {
            "schema_version": "1.0.0",
            "edge_id": edge_id,
            "from_node_id": from_node_id,
            "to_node_id": to_node_id,
            "edge_type_id": "edge.mobility.{}".format(edge_kind),
            "capacity": None,
            "delay_ticks": delay_ticks,
            "loss_fraction": 0,
            "cost_units": max(1, delay_ticks),
            "payload": edge_payload,
            "extensions": {},
        }

    if not edges_by_id:
        raise MobilityNetworkError(
            REFUSAL_MOBILITY_NETWORK_INVALID,
            "no mobility edges were produced from guide geometries",
            {"formalization_id": formalization_token},
        )

    outgoing_by_node: Dict[str, List[str]] = {}
    for edge_id, edge in edges_by_id.items():
        node_id = str(dict(edge).get("from_node_id", "")).strip()
        if node_id:
            outgoing_by_node.setdefault(node_id, []).append(edge_id)

    switch_machines: List[dict] = []
    for node_id in sorted(nodes_by_id.keys()):
        node = dict(nodes_by_id[node_id])
        payload = _as_map(node.get("payload"))
        if str(payload.get("node_kind", "")).strip() != "switch":
            continue
        outgoing = sorted(set(outgoing_by_node.get(node_id) or []))
        if not outgoing:
            continue
        machine_id = str(payload.get("state_machine_id", "")).strip() or "state_machine.mob.switch.{}".format(
            canonical_sha256({"graph_id": resolved_graph_id, "node_id": node_id})[:16]
        )
        payload["state_machine_id"] = machine_id
        node["payload"] = payload
        nodes_by_id[node_id] = node
        transition_rows = []
        for from_state in outgoing:
            for to_state in outgoing:
                transition_rows.append(
                    {
                        "schema_version": "1.0.0",
                        "transition_id": "transition.mob.switch.{}".format(
                            canonical_sha256(
                                {
                                    "machine_id": machine_id,
                                    "from_state": from_state,
                                    "to_state": to_state,
                                }
                            )[:16]
                        ),
                        "from_state": from_state,
                        "to_state": to_state,
                        "trigger_process_id": "process.switch_set_state",
                        "guard_conditions": {},
                        "priority": 0,
                        "extensions": {},
                    }
                )
        switch_machines.append(
            normalize_state_machine(
                {
                    "schema_version": "1.0.0",
                    "machine_id": machine_id,
                    "machine_type_id": "state_machine.mobility.switch",
                    "state_id": outgoing[0],
                    "transitions": [str(item.get("transition_id", "")) for item in transition_rows],
                    "transition_rows": transition_rows,
                    "extensions": {
                        "graph_id": resolved_graph_id,
                        "switch_node_id": node_id,
                        "outgoing_edge_ids": outgoing,
                    },
                }
            )
        )

    graph = normalize_network_graph(
        {
            "schema_version": "1.0.0",
            "graph_id": resolved_graph_id,
            "node_type_schema_id": "dominium.schema.mobility.mobility_node_payload.v1",
            "edge_type_schema_id": "dominium.schema.mobility.mobility_edge_payload.v1",
            "payload_schema_versions": {
                "dominium.schema.mobility.mobility_node_payload.v1": "1.0.0",
                "dominium.schema.mobility.mobility_edge_payload.v1": "1.0.0",
            },
            "validation_mode": "strict",
            "graph_partition_id": resolved_partition_id,
            "nodes": [dict(nodes_by_id[node_id]) for node_id in sorted(nodes_by_id.keys())],
            "edges": [
                dict(edges_by_id[edge_id])
                for edge_id in sorted(
                    edges_by_id.keys(),
                    key=lambda edge_id: (
                        str(edges_by_id[edge_id].get("from_node_id", "")),
                        str(edges_by_id[edge_id].get("to_node_id", "")),
                        str(edge_id),
                    ),
                )
            ],
            "deterministic_routing_policy_id": "route.shortest_delay",
            "extensions": {
                "formalization_id": formalization_token,
                "source": "mobility_network_engine",
            },
        }
    )
    node_ids = [str(row.get("node_id", "")).strip() for row in list(graph.get("nodes") or []) if isinstance(row, dict)]
    edge_ids = [str(row.get("edge_id", "")).strip() for row in list(graph.get("edges") or []) if isinstance(row, dict)]
    binding = build_mobility_network_binding(
        binding_id=deterministic_mobility_binding_id(formalization_id=formalization_token, graph_id=resolved_graph_id),
        formalization_id=formalization_token,
        graph_id=resolved_graph_id,
        node_ids=node_ids,
        edge_ids=edge_ids,
        extensions={},
    )
    return {
        "graph": graph,
        "binding": binding,
        "switch_state_machines": sorted(
            [dict(row) for row in switch_machines],
            key=lambda row: str(row.get("machine_id", "")),
        ),
    }


def filter_graph_by_switch_state(
    *,
    graph_row: Mapping[str, object],
    switch_state_machine_rows: object,
) -> dict:
    graph = normalize_network_graph(graph_row)
    machine_by_id = {}
    for row in sorted((dict(item) for item in list(switch_state_machine_rows or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("machine_id", ""))):
        machine_id = str(row.get("machine_id", "")).strip()
        if not machine_id:
            continue
        try:
            machine_by_id[machine_id] = normalize_state_machine(row)
        except Exception:
            continue
    node_to_machine = {}
    for node in list(graph.get("nodes") or []):
        if not isinstance(node, Mapping):
            continue
        node_id = str(node.get("node_id", "")).strip()
        payload = _as_map(node.get("payload"))
        if str(payload.get("node_kind", "")).strip() != "switch":
            continue
        machine_id = str(payload.get("state_machine_id", "")).strip()
        if node_id and machine_id:
            node_to_machine[node_id] = machine_id
    if not node_to_machine:
        return graph

    disabled_edges: List[str] = []
    kept_edges: List[dict] = []
    for edge in list(graph.get("edges") or []):
        if not isinstance(edge, Mapping):
            continue
        edge_id = str(edge.get("edge_id", "")).strip()
        from_node_id = str(edge.get("from_node_id", "")).strip()
        machine_id = str(node_to_machine.get(from_node_id, "")).strip()
        if not machine_id:
            kept_edges.append(dict(edge))
            continue
        machine = dict(machine_by_id.get(machine_id) or {})
        active_edge_id = str(machine.get("state_id", "")).strip()
        if active_edge_id and edge_id == active_edge_id:
            kept_edges.append(dict(edge))
            continue
        disabled_edges.append(edge_id)
    graph["edges"] = sorted(
        kept_edges,
        key=lambda row: (
            str(row.get("from_node_id", "")),
            str(row.get("to_node_id", "")),
            str(row.get("edge_id", "")),
        ),
    )
    ext = _as_map(graph.get("extensions"))
    ext["switch_filtered"] = {
        "switch_count": int(len(node_to_machine)),
        "disabled_edge_ids": sorted(set(disabled_edges)),
    }
    graph["extensions"] = ext
    return normalize_network_graph(graph)


def select_switch_transition_id(
    *,
    machine_row: Mapping[str, object],
    target_edge_id: str,
) -> str:
    machine = normalize_state_machine(machine_row)
    token = str(target_edge_id).strip()
    if not token:
        raise MobilityNetworkError(
            REFUSAL_MOBILITY_SWITCH_INVALID,
            "target_edge_id is required",
            {"machine_id": str(machine.get("machine_id", ""))},
        )
    candidates = [
        dict(row)
        for row in list(machine.get("transition_rows") or [])
        if isinstance(row, Mapping) and str(row.get("to_state", "")).strip() == token
    ]
    if not candidates:
        raise MobilityNetworkError(
            REFUSAL_MOBILITY_SWITCH_INVALID,
            "target_edge_id is not reachable by switch transition",
            {
                "machine_id": str(machine.get("machine_id", "")),
                "target_edge_id": token,
            },
        )
    selected = sorted(
        candidates,
        key=lambda row: (
            -1 * int(_as_int(row.get("priority", 0), 0)),
            str(row.get("from_state", "")),
            str(row.get("transition_id", "")),
        ),
    )[0]
    return str(selected.get("transition_id", "")).strip()


__all__ = [
    "MobilityNetworkError",
    "REFUSAL_MOBILITY_NETWORK_INVALID",
    "REFUSAL_MOBILITY_NO_ROUTE",
    "REFUSAL_MOBILITY_SWITCH_INVALID",
    "build_mobility_network_binding",
    "build_mobility_network_graph",
    "deterministic_mobility_binding_id",
    "filter_graph_by_switch_state",
    "mobility_edge_kind_rows_by_id",
    "mobility_max_speed_policy_rows_by_id",
    "mobility_node_kind_rows_by_id",
    "normalize_mobility_network_binding_rows",
    "select_switch_transition_id",
]
