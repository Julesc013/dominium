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
    payload_ref = payload.get("payload_ref")
    if payload_ref is None:
        payload_ref = {}
    if not isinstance(payload_ref, dict):
        raise NetworkGraphError(
            REFUSAL_CORE_GRAPH_INVALID,
            "network node payload_ref must be object",
            {"node_id": node_id},
        )
    extensions = payload.get("extensions")
    if not isinstance(extensions, dict):
        extensions = {}
    return {
        "schema_version": "1.0.0",
        "node_id": node_id,
        "node_type_id": node_type_id,
        "payload_ref": dict(payload_ref),
        "tags": _sorted_unique_strings(payload.get("tags")),
        "extensions": dict(extensions),
    }


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
    payload_ref = payload.get("payload_ref")
    if payload_ref is None:
        payload_ref = {}
    if not isinstance(payload_ref, dict):
        raise NetworkGraphError(
            REFUSAL_CORE_GRAPH_INVALID,
            "network edge payload_ref must be object",
            {"edge_id": edge_id},
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
    extensions = payload.get("extensions")
    if not isinstance(extensions, dict):
        extensions = {}
    return {
        "schema_version": "1.0.0",
        "edge_id": edge_id,
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "edge_type_id": edge_type_id,
        "payload_ref": dict(payload_ref),
        "capacity": normalized_capacity,
        "delay_ticks": normalized_delay_ticks,
        "loss_fraction": normalized_loss_fraction,
        "extensions": dict(extensions),
    }


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
    node_id_set = set(nodes.keys())
    for edge in sorted((item for item in edges_raw if isinstance(item, dict)), key=lambda item: str(item.get("edge_id", ""))):
        normalized = normalize_network_edge(edge, node_id_set)
        edge_id = str(normalized.get("edge_id", ""))
        if edge_id in edges:
            raise NetworkGraphError(
                REFUSAL_CORE_GRAPH_INVALID,
                "duplicate network edge_id in graph",
                {"graph_id": graph_id, "edge_id": edge_id},
            )
        edges[edge_id] = normalized
    return {
        "schema_version": "1.0.0",
        "graph_id": graph_id,
        "node_type_schema_id": str(payload.get("node_type_schema_id", "")).strip(),
        "edge_type_schema_id": str(payload.get("edge_type_schema_id", "")).strip(),
        "nodes": [dict(nodes[node_id]) for node_id in sorted(nodes.keys())],
        "edges": [dict(edges[edge_id]) for edge_id in sorted(edges.keys())],
        "deterministic_routing_policy_id": deterministic_routing_policy_id,
        "extensions": dict(payload.get("extensions") or {}),
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
        payload_ref = dict(edge_row.get("payload_ref") or {})
        value = payload_ref.get("cost_units_per_mass")
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

