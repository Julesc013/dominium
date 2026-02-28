"""Deterministic core NetworkGraph helpers."""

from __future__ import annotations

import heapq
from typing import Dict, List, Mapping, Tuple


REFUSAL_CORE_GRAPH_INVALID = "refusal.core.network_graph.invalid"
REFUSAL_CORE_GRAPH_ROUTE_MISSING = "refusal.core.network_graph.route_missing"


class NetworkGraphError(ValueError):
    """Deterministic NetworkGraph refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _round_div_away_from_zero(numerator: int, denominator: int) -> int:
    if int(denominator) == 0:
        raise NetworkGraphError(
            REFUSAL_CORE_GRAPH_INVALID,
            "division by zero in NetworkGraph fixed-point calculation",
            {"denominator": str(denominator)},
        )
    n = int(numerator)
    d = int(denominator)
    sign = -1 if (n < 0) ^ (d < 0) else 1
    abs_n = abs(n)
    abs_d = abs(d)
    quotient = abs_n // abs_d
    remainder = abs_n % abs_d
    if remainder * 2 >= abs_d:
        quotient += 1
    return int(sign * quotient)


def _is_semver(value: str) -> bool:
    parts = str(value or "").strip().split(".")
    if len(parts) != 3:
        return False
    for token in parts:
        if not token.isdigit():
            return False
    return True


def _canonicalize_value(value: object) -> object:
    if isinstance(value, dict):
        out: Dict[str, object] = {}
        for key in sorted(value.keys(), key=lambda item: str(item)):
            token = str(key)
            out[token] = _canonicalize_value(value[key])
        return out
    if isinstance(value, list):
        return [_canonicalize_value(item) for item in list(value)]
    return value


def _normalize_payload_payload_ref(
    *,
    row: Mapping[str, object],
    reason_details: Mapping[str, object],
) -> Tuple[dict | None, dict | str | None]:
    payload = row.get("payload")
    payload_ref = row.get("payload_ref")
    if payload is None and payload_ref is None:
        raise NetworkGraphError(
            REFUSAL_CORE_GRAPH_INVALID,
            "network payload requires payload or payload_ref",
            dict(reason_details),
        )
    normalized_payload = None
    if payload is not None:
        if not isinstance(payload, dict):
            raise NetworkGraphError(
                REFUSAL_CORE_GRAPH_INVALID,
                "network payload must be object when provided",
                dict(reason_details),
            )
        normalized_payload = dict(_canonicalize_value(dict(payload)))
    normalized_payload_ref: dict | str | None = None
    if payload_ref is not None:
        if isinstance(payload_ref, dict):
            normalized_payload_ref = dict(_canonicalize_value(dict(payload_ref)))
        elif isinstance(payload_ref, str):
            token = str(payload_ref).strip()
            if not token:
                raise NetworkGraphError(
                    REFUSAL_CORE_GRAPH_INVALID,
                    "network payload_ref string must be non-empty",
                    dict(reason_details),
                )
            normalized_payload_ref = token
        else:
            raise NetworkGraphError(
                REFUSAL_CORE_GRAPH_INVALID,
                "network payload_ref must be object or string",
                dict(reason_details),
            )
    return normalized_payload, normalized_payload_ref


def normalize_network_node(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    node_id = str(payload.get("node_id", "")).strip()
    node_type_id = str(payload.get("node_type_id", "")).strip()
    if not node_id or not node_type_id:
        raise NetworkGraphError(
            REFUSAL_CORE_GRAPH_INVALID,
            "network node missing required node_id/node_type_id",
            {"node_id": node_id, "node_type_id": node_type_id},
        )
    normalized_payload, normalized_payload_ref = _normalize_payload_payload_ref(
        row=payload,
        reason_details={"node_id": node_id},
    )
    extensions = payload.get("extensions")
    if not isinstance(extensions, dict):
        extensions = {}
    out = {
        "schema_version": "1.0.0",
        "node_id": node_id,
        "node_type_id": node_type_id,
        "tags": _sorted_unique_strings(payload.get("tags")),
        "extensions": dict(_canonicalize_value(dict(extensions))),
    }
    if normalized_payload is not None:
        out["payload"] = dict(normalized_payload)
    if normalized_payload_ref is not None:
        out["payload_ref"] = (
            dict(normalized_payload_ref) if isinstance(normalized_payload_ref, dict) else str(normalized_payload_ref)
        )
    return out


def normalize_network_edge(row: Mapping[str, object], node_ids: set[str]) -> dict:
    payload = dict(row or {})
    edge_id = str(payload.get("edge_id", "")).strip()
    from_node_id = str(payload.get("from_node_id", "")).strip()
    to_node_id = str(payload.get("to_node_id", "")).strip()
    edge_type_id = str(payload.get("edge_type_id", "")).strip()
    if not edge_id or not from_node_id or not to_node_id or not edge_type_id:
        raise NetworkGraphError(
            REFUSAL_CORE_GRAPH_INVALID,
            "network edge missing required fields",
            {
                "edge_id": edge_id,
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
                "edge_type_id": edge_type_id,
            },
        )
    if from_node_id not in node_ids or to_node_id not in node_ids:
        raise NetworkGraphError(
            REFUSAL_CORE_GRAPH_INVALID,
            "network edge references unknown node",
            {"edge_id": edge_id, "from_node_id": from_node_id, "to_node_id": to_node_id},
        )
    normalized_payload, normalized_payload_ref = _normalize_payload_payload_ref(
        row=payload,
        reason_details={"edge_id": edge_id},
    )
    capacity = payload.get("capacity")
    if capacity is None:
        normalized_capacity = None
    else:
        normalized_capacity = _as_int(capacity, 0)
        if normalized_capacity < 0:
            raise NetworkGraphError(
                REFUSAL_CORE_GRAPH_INVALID,
                "network edge capacity must be >= 0",
                {"edge_id": edge_id, "capacity": int(normalized_capacity)},
            )
    delay_ticks = payload.get("delay_ticks")
    if delay_ticks is None:
        normalized_delay_ticks = None
    else:
        normalized_delay_ticks = _as_int(delay_ticks, 0)
        if normalized_delay_ticks < 0:
            raise NetworkGraphError(
                REFUSAL_CORE_GRAPH_INVALID,
                "network edge delay_ticks must be >= 0",
                {"edge_id": edge_id, "delay_ticks": int(normalized_delay_ticks)},
            )
    loss_fraction = payload.get("loss_fraction")
    if loss_fraction is None:
        normalized_loss_fraction = None
    else:
        normalized_loss_fraction = _as_int(loss_fraction, 0)
        if normalized_loss_fraction < 0:
            raise NetworkGraphError(
                REFUSAL_CORE_GRAPH_INVALID,
                "network edge loss_fraction must be >= 0",
                {"edge_id": edge_id, "loss_fraction": int(normalized_loss_fraction)},
            )
    cost_units = payload.get("cost_units")
    if cost_units is None:
        normalized_cost_units = None
    else:
        normalized_cost_units = _as_int(cost_units, 0)
        if normalized_cost_units < 0:
            raise NetworkGraphError(
                REFUSAL_CORE_GRAPH_INVALID,
                "network edge cost_units must be >= 0",
                {"edge_id": edge_id, "cost_units": int(normalized_cost_units)},
            )
    extensions = payload.get("extensions")
    if not isinstance(extensions, dict):
        extensions = {}
    out = {
        "schema_version": "1.0.0",
        "edge_id": edge_id,
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "edge_type_id": edge_type_id,
        "capacity": normalized_capacity,
        "delay_ticks": normalized_delay_ticks,
        "loss_fraction": normalized_loss_fraction,
        "cost_units": normalized_cost_units,
        "extensions": dict(_canonicalize_value(dict(extensions))),
    }
    if normalized_payload is not None:
        out["payload"] = dict(normalized_payload)
    if normalized_payload_ref is not None:
        out["payload_ref"] = (
            dict(normalized_payload_ref) if isinstance(normalized_payload_ref, dict) else str(normalized_payload_ref)
        )
    return out


def normalize_network_graph(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    graph_id = str(payload.get("graph_id", "")).strip()
    deterministic_routing_policy_id = str(payload.get("deterministic_routing_policy_id", "")).strip()
    if not graph_id or not deterministic_routing_policy_id:
        raise NetworkGraphError(
            REFUSAL_CORE_GRAPH_INVALID,
            "network graph missing graph_id or deterministic_routing_policy_id",
            {
                "graph_id": graph_id,
                "deterministic_routing_policy_id": deterministic_routing_policy_id,
            },
        )
    node_type_schema_id = str(payload.get("node_type_schema_id", "")).strip()
    edge_type_schema_id = str(payload.get("edge_type_schema_id", "")).strip()
    payload_schema_versions_raw = payload.get("payload_schema_versions")
    payload_schema_versions = {}
    if isinstance(payload_schema_versions_raw, dict):
        for key in sorted(payload_schema_versions_raw.keys(), key=lambda item: str(item)):
            schema_id = str(key).strip()
            version = str(payload_schema_versions_raw.get(key, "")).strip()
            if schema_id and version:
                payload_schema_versions[schema_id] = version
    if node_type_schema_id and node_type_schema_id not in payload_schema_versions:
        payload_schema_versions[node_type_schema_id] = "1.0.0"
    if edge_type_schema_id and edge_type_schema_id not in payload_schema_versions:
        payload_schema_versions[edge_type_schema_id] = "1.0.0"
    validation_mode = str(payload.get("validation_mode", "strict")).strip() or "strict"
    if validation_mode not in {"strict", "warn", "off"}:
        validation_mode = "strict"
    if validation_mode == "strict":
        if not node_type_schema_id or not edge_type_schema_id:
            raise NetworkGraphError(
                REFUSAL_CORE_GRAPH_INVALID,
                "strict network graph validation requires node/edge payload schema IDs",
                {"graph_id": graph_id},
            )
        for schema_id in (node_type_schema_id, edge_type_schema_id):
            version = str(payload_schema_versions.get(schema_id, "")).strip()
            if not version:
                raise NetworkGraphError(
                    REFUSAL_CORE_GRAPH_INVALID,
                    "strict network graph validation requires payload schema version mapping",
                    {"graph_id": graph_id, "schema_id": schema_id},
                )
            if not _is_semver(version):
                raise NetworkGraphError(
                    REFUSAL_CORE_GRAPH_INVALID,
                    "payload schema version must be semantic version",
                    {"graph_id": graph_id, "schema_id": schema_id, "version": version},
                )
    nodes_raw = payload.get("nodes")
    edges_raw = payload.get("edges")
    if not isinstance(nodes_raw, list) or not isinstance(edges_raw, list):
        raise NetworkGraphError(
            REFUSAL_CORE_GRAPH_INVALID,
            "network graph nodes/edges must be arrays",
            {"graph_id": graph_id},
        )
    nodes: Dict[str, dict] = {}
    for node in sorted((item for item in nodes_raw if isinstance(item, dict)), key=lambda item: str(item.get("node_id", ""))):
        normalized = normalize_network_node(node)
        node_id = str(normalized.get("node_id", ""))
        if node_id in nodes:
            raise NetworkGraphError(
                REFUSAL_CORE_GRAPH_INVALID,
                "duplicate network node_id in graph",
                {"graph_id": graph_id, "node_id": node_id},
            )
        nodes[node_id] = normalized
    edges: Dict[str, dict] = {}
    edge_order: List[str] = []
    node_id_set = set(nodes.keys())
    for edge in sorted(
        (item for item in edges_raw if isinstance(item, dict)),
        key=lambda item: (
            str(item.get("from_node_id", "")),
            str(item.get("to_node_id", "")),
            str(item.get("edge_id", "")),
        ),
    ):
        normalized = normalize_network_edge(edge, node_id_set)
        edge_id = str(normalized.get("edge_id", ""))
        if edge_id in edges:
            raise NetworkGraphError(
                REFUSAL_CORE_GRAPH_INVALID,
                "duplicate network edge_id in graph",
                {"graph_id": graph_id, "edge_id": edge_id},
            )
        edges[edge_id] = normalized
        edge_order.append(edge_id)
    graph_partition_id_raw = payload.get("graph_partition_id")
    graph_partition_id = None
    if graph_partition_id_raw is not None:
        token = str(graph_partition_id_raw).strip()
        if token:
            graph_partition_id = token
    extensions = payload.get("extensions")
    if not isinstance(extensions, dict):
        extensions = {}
    return {
        "schema_version": "1.0.0",
        "graph_id": graph_id,
        "node_type_schema_id": node_type_schema_id,
        "edge_type_schema_id": edge_type_schema_id,
        "payload_schema_versions": dict(
            (str(key), str(payload_schema_versions[key]).strip())
            for key in sorted(payload_schema_versions.keys())
            if str(key).strip()
        ),
        "validation_mode": validation_mode,
        "graph_partition_id": graph_partition_id,
        "nodes": [dict(nodes[node_id]) for node_id in sorted(nodes.keys())],
        "edges": [dict(edges[edge_id]) for edge_id in edge_order],
        "deterministic_routing_policy_id": deterministic_routing_policy_id,
        "extensions": dict(_canonicalize_value(dict(extensions))),
    }


def _edge_index(graph_row: Mapping[str, object]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list((graph_row or {}).get("edges") or []) if isinstance(item, dict)), key=lambda item: str(item.get("edge_id", ""))):
        edge_id = str(row.get("edge_id", "")).strip()
        if edge_id:
            out[edge_id] = dict(row)
    return out


def _adjacency(graph_row: Mapping[str, object]) -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = {}
    for edge in sorted((item for item in list((graph_row or {}).get("edges") or []) if isinstance(item, dict)), key=lambda item: str(item.get("edge_id", ""))):
        from_node_id = str(edge.get("from_node_id", "")).strip()
        if not from_node_id:
            continue
        out.setdefault(from_node_id, []).append(dict(edge))
    for key in sorted(out.keys()):
        out[key] = sorted(out[key], key=lambda item: str(item.get("edge_id", "")))
    return out


def _direct_route(graph_row: Mapping[str, object], from_node_id: str, to_node_id: str) -> List[str]:
    candidates = []
    for edge in sorted((item for item in list((graph_row or {}).get("edges") or []) if isinstance(item, dict)), key=lambda item: str(item.get("edge_id", ""))):
        if str(edge.get("from_node_id", "")).strip() != str(from_node_id).strip():
            continue
        if str(edge.get("to_node_id", "")).strip() != str(to_node_id).strip():
            continue
        candidates.append(str(edge.get("edge_id", "")).strip())
    candidates = [token for token in candidates if token]
    return sorted(set(candidates))[:1]


def _metric_cost(edge_row: Mapping[str, object], metric: str) -> int:
    if str(metric) == "min_cost_units":
        if edge_row.get("cost_units") is not None:
            return int(_as_int(edge_row.get("cost_units"), 0))
        payload_ref_raw = edge_row.get("payload_ref")
        payload_ref = payload_ref_raw if isinstance(payload_ref_raw, dict) else {}
        value = dict(payload_ref).get("cost_units_per_mass")
        return int(_as_int(0 if value is None else value, 0))
    delay_ticks = edge_row.get("delay_ticks")
    if delay_ticks is None:
        delay_ticks = 0
    return int(_as_int(delay_ticks, 0))


def route_query(
    graph_row: Mapping[str, object],
    routing_policy_row: Mapping[str, object],
    from_node_id: str,
    to_node_id: str,
) -> List[str]:
    graph = normalize_network_graph(graph_row)
    from_node = str(from_node_id).strip()
    to_node = str(to_node_id).strip()
    if from_node == to_node:
        return []
    policy = dict(routing_policy_row or {})
    policy_id = str(policy.get("policy_id", "")).strip() or str(policy.get("rule_id", "")).strip()
    allow_multi_hop = bool(policy.get("allow_multi_hop", False))
    if policy_id == "route.direct_only" or not allow_multi_hop:
        direct = _direct_route(graph, from_node, to_node)
        if direct:
            return list(direct)
        raise NetworkGraphError(
            REFUSAL_CORE_GRAPH_ROUTE_MISSING,
            "no direct route exists between network nodes",
            {"from_node_id": from_node, "to_node_id": to_node, "policy_id": policy_id},
        )
    metric = str(policy.get("optimization_metric", "")).strip() or "delay_ticks"
    if policy_id == "route.shortest_delay":
        metric = "delay_ticks"
    elif policy_id == "route.min_cost_units":
        metric = "min_cost_units"
    adjacency = _adjacency(graph)
    heap: List[Tuple[int, str, str, Tuple[str, ...]]] = []
    heapq.heappush(heap, (0, "", from_node, tuple()))
    best_seen: Dict[str, Tuple[int, str]] = {}
    while heap:
        metric_total, tie_path, node_id, route_tuple = heapq.heappop(heap)
        prior = best_seen.get(node_id)
        if prior is not None and (metric_total, tie_path) > prior:
            continue
        best_seen[node_id] = (metric_total, tie_path)
        if node_id == to_node:
            return list(route_tuple)
        for edge in adjacency.get(node_id, []):
            edge_id = str(edge.get("edge_id", "")).strip()
            if not edge_id:
                continue
            next_node = str(edge.get("to_node_id", "")).strip()
            if not next_node:
                continue
            step = _metric_cost(edge, metric)
            next_metric = int(metric_total) + int(step)
            next_route = tuple(list(route_tuple) + [edge_id])
            next_tie = "|".join(next_route)
            prior_next = best_seen.get(next_node)
            if prior_next is not None and (next_metric, next_tie) >= prior_next:
                continue
            heapq.heappush(heap, (next_metric, next_tie, next_node, next_route))
    raise NetworkGraphError(
        REFUSAL_CORE_GRAPH_ROUTE_MISSING,
        "no route exists between network nodes",
        {"from_node_id": from_node, "to_node_id": to_node, "policy_id": policy_id},
    )


def route_delay_ticks(graph_row: Mapping[str, object], edge_ids: List[str]) -> int:
    graph = normalize_network_graph(graph_row)
    edge_index = _edge_index(graph)
    return int(
        sum(
            int(_as_int((edge_index.get(edge_id) or {}).get("delay_ticks", 0), 0))
            for edge_id in list(edge_ids or [])
        )
    )


def route_loss_fraction(graph_row: Mapping[str, object], edge_ids: List[str], *, scale: int) -> int:
    graph = normalize_network_graph(graph_row)
    edge_index = _edge_index(graph)
    survival = int(scale)
    for edge_id in list(edge_ids or []):
        edge_row = dict(edge_index.get(str(edge_id).strip()) or {})
        loss_fraction = int(_as_int(edge_row.get("loss_fraction", 0), 0))
        if loss_fraction < 0:
            loss_fraction = 0
        if loss_fraction > int(scale):
            loss_fraction = int(scale)
        survival = int(_round_div_away_from_zero(int(survival) * int(scale - loss_fraction), int(scale)))
    return int(max(0, int(scale - survival)))
