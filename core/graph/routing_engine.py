"""Deterministic NetworkGraph routing engine with cache and partition hooks."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from .network_graph_engine import (
    NetworkGraphError,
    normalize_network_graph,
    route_query as _route_query_base,
)


REFUSAL_ROUTE_INVALID = "refusal.route.invalid"
REFUSAL_ROUTE_NOT_FOUND = "refusal.route.not_found"
REFUSAL_ROUTE_CAPACITY_INSUFFICIENT = "refusal.route.capacity_insufficient"


class RoutingError(ValueError):
    """Deterministic routing refusal."""

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


def _canonicalize_dict(value: Mapping[str, object] | None) -> dict:
    src = dict(value or {})
    out: Dict[str, object] = {}
    for key in sorted(src.keys(), key=lambda item: str(item)):
        token = str(key)
        child = src[key]
        if isinstance(child, dict):
            out[token] = _canonicalize_dict(dict(child))
        elif isinstance(child, list):
            out[token] = [item for item in child]
        else:
            out[token] = child
    return out


def normalize_route_query_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    graph_id = str(payload.get("graph_id", "")).strip()
    from_node_id = str(payload.get("from_node_id", "")).strip()
    to_node_id = str(payload.get("to_node_id", "")).strip()
    route_policy_id = str(payload.get("route_policy_id", "")).strip()
    if not graph_id or not from_node_id or not to_node_id or not route_policy_id:
        raise RoutingError(
            REFUSAL_ROUTE_INVALID,
            "route query missing required identifiers",
            {
                "graph_id": graph_id,
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
                "route_policy_id": route_policy_id,
            },
        )
    constraints = payload.get("constraints")
    if constraints is None:
        constraints = {}
    if not isinstance(constraints, dict):
        raise RoutingError(
            REFUSAL_ROUTE_INVALID,
            "route query constraints must be object",
            {"graph_id": graph_id},
        )
    return {
        "schema_version": "1.0.0",
        "graph_id": graph_id,
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "route_policy_id": route_policy_id,
        "constraints": _canonicalize_dict(constraints),
        "extensions": dict(payload.get("extensions") or {}),
    }


def normalize_route_result_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    path_node_ids = [str(item).strip() for item in list(payload.get("path_node_ids") or []) if str(item).strip()]
    path_edge_ids = [str(item).strip() for item in list(payload.get("path_edge_ids") or []) if str(item).strip()]
    total_cost = max(0, _as_int(payload.get("total_cost", 0), 0))
    result = {
        "schema_version": "1.0.0",
        "path_node_ids": list(path_node_ids),
        "path_edge_ids": list(path_edge_ids),
        "total_cost": int(total_cost),
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": dict(payload.get("extensions") or {}),
    }
    if not result["deterministic_fingerprint"]:
        result["deterministic_fingerprint"] = canonical_sha256(
            dict(result, deterministic_fingerprint="")
        )
    return result


def normalize_graph_partition_row(row: Mapping[str, object], *, graph_row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    graph = normalize_network_graph(graph_row)
    partition_id = str(payload.get("partition_id", "")).strip()
    if not partition_id:
        raise RoutingError(
            REFUSAL_ROUTE_INVALID,
            "graph partition missing partition_id",
            {},
        )
    graph_id = str(payload.get("graph_id", "")).strip() or str(graph.get("graph_id", "")).strip()
    if graph_id != str(graph.get("graph_id", "")).strip():
        raise RoutingError(
            REFUSAL_ROUTE_INVALID,
            "graph partition graph_id must match target graph",
            {"partition_graph_id": graph_id, "graph_id": str(graph.get("graph_id", ""))},
        )

    known_nodes = {str(item.get("node_id", "")).strip() for item in list(graph.get("nodes") or []) if isinstance(item, dict)}
    known_edges = {str(item.get("edge_id", "")).strip() for item in list(graph.get("edges") or []) if isinstance(item, dict)}

    node_shard_map_raw = payload.get("node_shard_map")
    if not isinstance(node_shard_map_raw, dict):
        node_shard_map_raw = {}
    node_shard_map = {}
    for key in sorted(node_shard_map_raw.keys(), key=lambda item: str(item)):
        node_id = str(key).strip()
        shard_id = str(node_shard_map_raw.get(key, "")).strip()
        if not node_id or not shard_id:
            continue
        if node_id not in known_nodes:
            raise RoutingError(
                REFUSAL_ROUTE_INVALID,
                "graph partition references unknown node_id",
                {"partition_id": partition_id, "node_id": node_id},
            )
        node_shard_map[node_id] = shard_id

    edge_shard_map_raw = payload.get("edge_shard_map")
    if not isinstance(edge_shard_map_raw, dict):
        edge_shard_map_raw = {}
    edge_shard_map = {}
    for key in sorted(edge_shard_map_raw.keys(), key=lambda item: str(item)):
        edge_id = str(key).strip()
        shard_id = str(edge_shard_map_raw.get(key, "")).strip()
        if not edge_id or not shard_id:
            continue
        if edge_id not in known_edges:
            raise RoutingError(
                REFUSAL_ROUTE_INVALID,
                "graph partition references unknown edge_id",
                {"partition_id": partition_id, "edge_id": edge_id},
            )
        edge_shard_map[edge_id] = shard_id

    boundary_node_ids = []
    for token in _sorted_unique_strings(payload.get("cross_shard_boundary_nodes")):
        if token not in known_nodes:
            raise RoutingError(
                REFUSAL_ROUTE_INVALID,
                "graph partition boundary references unknown node_id",
                {"partition_id": partition_id, "node_id": token},
            )
        boundary_node_ids.append(token)
    return {
        "schema_version": "1.0.0",
        "partition_id": partition_id,
        "graph_id": graph_id,
        "node_shard_map": dict(node_shard_map),
        "edge_shard_map": dict(edge_shard_map),
        "cross_shard_boundary_nodes": list(boundary_node_ids),
        "extensions": dict(payload.get("extensions") or {}),
    }


def _routing_policy(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    policy_id = str(payload.get("policy_id", "")).strip() or str(payload.get("rule_id", "")).strip()
    if not policy_id:
        raise RoutingError(REFUSAL_ROUTE_INVALID, "routing policy_id is required", {})
    tie_break_policy = str(payload.get("tie_break_policy", "")).strip() or "edge_id_lexicographic"
    allow_multi_hop = bool(payload.get("allow_multi_hop", False))
    optimization_metric = str(payload.get("optimization_metric", "")).strip()
    if not optimization_metric:
        if policy_id == "route.min_cost_units":
            optimization_metric = "min_cost_units"
        else:
            optimization_metric = "delay_ticks"
    return {
        "policy_id": policy_id,
        "tie_break_policy": tie_break_policy,
        "allow_multi_hop": allow_multi_hop,
        "optimization_metric": optimization_metric,
        "extensions": dict(payload.get("extensions") or {}),
    }


def _route_constraints(row: Mapping[str, object] | None) -> dict:
    payload = dict(row or {})
    required_capacity = max(0, _as_int(payload.get("required_capacity", 0), 0))
    max_hops = payload.get("max_hops")
    normalized_max_hops = None if max_hops is None else max(0, _as_int(max_hops, 0))
    allow_edge_type_ids = _sorted_unique_strings(payload.get("allow_edge_type_ids"))
    disallow_node_ids = _sorted_unique_strings(payload.get("disallow_node_ids"))
    return {
        "required_capacity": int(required_capacity),
        "max_hops": normalized_max_hops,
        "allow_edge_type_ids": list(allow_edge_type_ids),
        "disallow_node_ids": list(disallow_node_ids),
    }


def _metric_cost(edge_row: Mapping[str, object], metric: str) -> int:
    if str(metric) == "min_cost_units":
        if edge_row.get("cost_units") is not None:
            return max(0, _as_int(edge_row.get("cost_units"), 0))
        payload_ref = edge_row.get("payload_ref")
        if isinstance(payload_ref, dict):
            value = payload_ref.get("cost_units_per_mass")
            return max(0, _as_int(0 if value is None else value, 0))
        return 0
    return max(0, _as_int(edge_row.get("delay_ticks", 0), 0))


def _edge_index(graph_row: Mapping[str, object]) -> Dict[str, dict]:
    rows = {}
    for row in sorted((item for item in list((graph_row or {}).get("edges") or []) if isinstance(item, dict)), key=lambda item: str(item.get("edge_id", ""))):
        edge_id = str(row.get("edge_id", "")).strip()
        if edge_id:
            rows[edge_id] = dict(row)
    return rows


def _filtered_graph(graph_row: Mapping[str, object], constraints: Mapping[str, object]) -> dict:
    required_capacity = max(0, _as_int(constraints.get("required_capacity", 0), 0))
    allow_edge_type_ids = set(_sorted_unique_strings(constraints.get("allow_edge_type_ids")))
    disallow_node_ids = set(_sorted_unique_strings(constraints.get("disallow_node_ids")))
    graph = normalize_network_graph(graph_row)
    filtered_edges = []
    for row in list(graph.get("edges") or []):
        edge = dict(row)
        if allow_edge_type_ids and str(edge.get("edge_type_id", "")).strip() not in allow_edge_type_ids:
            continue
        if disallow_node_ids and (
            str(edge.get("from_node_id", "")).strip() in disallow_node_ids
            or str(edge.get("to_node_id", "")).strip() in disallow_node_ids
        ):
            continue
        if required_capacity > 0:
            capacity = edge.get("capacity")
            if capacity is None or _as_int(capacity, 0) < required_capacity:
                continue
        filtered_edges.append(edge)
    graph["edges"] = list(filtered_edges)
    return graph


def _path_node_ids(graph_row: Mapping[str, object], from_node_id: str, edge_ids: List[str]) -> List[str]:
    index = _edge_index(graph_row)
    current = str(from_node_id).strip()
    path = [current]
    for edge_id in list(edge_ids or []):
        row = dict(index.get(str(edge_id).strip()) or {})
        if not row:
            raise RoutingError(
                REFUSAL_ROUTE_INVALID,
                "route references unknown edge_id",
                {"edge_id": edge_id},
            )
        if str(row.get("from_node_id", "")).strip() != current:
            raise RoutingError(
                REFUSAL_ROUTE_INVALID,
                "route edge sequence is non-contiguous",
                {"edge_id": edge_id, "expected_from_node_id": current},
            )
        current = str(row.get("to_node_id", "")).strip()
        path.append(current)
    return path


def _route_total_cost(graph_row: Mapping[str, object], edge_ids: List[str], metric: str) -> int:
    index = _edge_index(graph_row)
    total = 0
    for edge_id in list(edge_ids or []):
        total += _metric_cost(dict(index.get(str(edge_id).strip()) or {}), metric)
    return int(max(0, total))


def build_route_cache_key(
    *,
    graph_hash: str,
    from_node_id: str,
    to_node_id: str,
    route_policy_id: str,
    constraints_hash: str,
) -> str:
    return canonical_sha256(
        {
            "graph_hash": str(graph_hash),
            "from_node_id": str(from_node_id),
            "to_node_id": str(to_node_id),
            "route_policy_id": str(route_policy_id),
            "constraints_hash": str(constraints_hash),
        }
    )


def _cache_lookup(
    cache_state: Mapping[str, object] | None,
    cache_key: str,
) -> dict:
    state = dict(cache_state or {})
    entries_by_key = dict(state.get("entries_by_key") or {})
    entry = dict(entries_by_key.get(str(cache_key), {}) or {})
    if entry:
        return {"cache_hit": True, "entry": entry}
    return {"cache_hit": False, "entry": {}}


def _cache_store(
    *,
    cache_state: Mapping[str, object] | None,
    cache_key: str,
    route_result: Mapping[str, object],
    max_entries: int,
) -> dict:
    state = dict(cache_state or {})
    entries_by_key = dict(state.get("entries_by_key") or {})
    next_sequence = max(0, _as_int(state.get("next_sequence", 0), 0))
    entries_by_key[str(cache_key)] = {
        "route_result": dict(route_result or {}),
        "sequence": int(next_sequence),
    }
    next_sequence += 1
    max_entries_norm = max(0, _as_int(max_entries, 0))
    if max_entries_norm > 0 and len(entries_by_key) > max_entries_norm:
        ranked = sorted(
            entries_by_key.keys(),
            key=lambda key: (
                _as_int((dict(entries_by_key.get(key) or {})).get("sequence", 0), 0),
                str(key),
            ),
        )
        for remove_key in ranked[: len(entries_by_key) - max_entries_norm]:
            if str(remove_key) == str(cache_key):
                continue
            entries_by_key.pop(remove_key, None)
        if len(entries_by_key) > max_entries_norm:
            ranked = sorted(
                entries_by_key.keys(),
                key=lambda key: (
                    _as_int((dict(entries_by_key.get(key) or {})).get("sequence", 0), 0),
                    str(key),
                ),
            )
            while len(entries_by_key) > max_entries_norm:
                remove_key = ranked.pop(0)
                if str(remove_key) == str(cache_key) and len(entries_by_key) > 1:
                    continue
                entries_by_key.pop(remove_key, None)
    return {
        "entries_by_key": dict((str(key), dict(entries_by_key[key])) for key in sorted(entries_by_key.keys())),
        "next_sequence": int(next_sequence),
    }


def _route_with_constraints(
    *,
    graph_row: Mapping[str, object],
    routing_policy_row: Mapping[str, object],
    from_node_id: str,
    to_node_id: str,
    constraints_row: Mapping[str, object],
) -> List[str]:
    constraints = _route_constraints(constraints_row)
    filtered_graph = _filtered_graph(graph_row, constraints)
    policy = _routing_policy(routing_policy_row)
    try:
        edge_ids = _route_query_base(filtered_graph, policy, str(from_node_id).strip(), str(to_node_id).strip())
    except NetworkGraphError:
        try:
            _route_query_base(normalize_network_graph(graph_row), policy, str(from_node_id).strip(), str(to_node_id).strip())
        except NetworkGraphError as exc:
            raise RoutingError(
                REFUSAL_ROUTE_NOT_FOUND,
                str(exc),
                dict(exc.details),
            ) from exc
        if int(constraints.get("required_capacity", 0)) > 0:
            raise RoutingError(
                REFUSAL_ROUTE_CAPACITY_INSUFFICIENT,
                "route exists but fails required capacity constraint",
                {
                    "from_node_id": str(from_node_id).strip(),
                    "to_node_id": str(to_node_id).strip(),
                    "required_capacity": int(constraints.get("required_capacity", 0)),
                },
            )
        raise RoutingError(
            REFUSAL_ROUTE_NOT_FOUND,
            "no route exists under provided constraints",
            {
                "from_node_id": str(from_node_id).strip(),
                "to_node_id": str(to_node_id).strip(),
            },
        )
    max_hops = constraints.get("max_hops")
    if max_hops is not None and len(edge_ids) > int(max_hops):
        raise RoutingError(
            REFUSAL_ROUTE_NOT_FOUND,
            "route exceeds max_hops constraint",
            {
                "max_hops": int(max_hops),
                "observed_hops": int(len(edge_ids)),
            },
        )
    return list(edge_ids)


def build_cross_shard_route_plan(
    *,
    graph_row: Mapping[str, object],
    partition_row: Mapping[str, object] | None,
    path_node_ids: List[str],
    path_edge_ids: List[str],
) -> dict:
    if not partition_row:
        return {
            "schema_version": "1.0.0",
            "partitioned": False,
            "segments": [],
            "cross_shard_boundaries": [],
            "deterministic_fingerprint": canonical_sha256(
                {
                    "partitioned": False,
                    "segments": [],
                    "cross_shard_boundaries": [],
                }
            ),
        }
    graph = normalize_network_graph(graph_row)
    partition = normalize_graph_partition_row(partition_row, graph_row=graph)
    edge_index = _edge_index(graph)
    node_shards = dict(partition.get("node_shard_map") or {})
    edge_shards = dict(partition.get("edge_shard_map") or {})
    default_shard = str(partition.get("partition_id", "")).strip()
    segments: List[dict] = []
    boundaries: List[dict] = []

    current_segment = None
    for idx, edge_id in enumerate(list(path_edge_ids or [])):
        edge_row = dict(edge_index.get(str(edge_id).strip()) or {})
        from_node_id = str(edge_row.get("from_node_id", "")).strip()
        to_node_id = str(edge_row.get("to_node_id", "")).strip()
        shard_id = str(edge_shards.get(str(edge_id).strip(), "")).strip()
        if not shard_id:
            shard_id = str(node_shards.get(from_node_id, "")).strip() or str(node_shards.get(to_node_id, "")).strip() or default_shard
        if current_segment is None or str(current_segment.get("shard_id", "")) != shard_id:
            if current_segment is not None:
                segments.append(dict(current_segment))
                boundaries.append(
                    {
                        "boundary_node_id": from_node_id,
                        "from_shard_id": str(current_segment.get("shard_id", "")),
                        "to_shard_id": shard_id,
                    }
                )
            current_segment = {
                "segment_index": len(segments),
                "shard_id": shard_id,
                "path_edge_ids": [],
                "path_node_ids": [from_node_id] if from_node_id else [],
            }
        current_segment["path_edge_ids"].append(str(edge_id).strip())
        if to_node_id:
            current_segment["path_node_ids"].append(to_node_id)
    if current_segment is not None:
        segments.append(dict(current_segment))

    normalized_segments = []
    for row in segments:
        normalized_segments.append(
            {
                "segment_index": int(_as_int(row.get("segment_index", 0), 0)),
                "shard_id": str(row.get("shard_id", "")).strip() or default_shard,
                "path_edge_ids": [str(item).strip() for item in list(row.get("path_edge_ids") or []) if str(item).strip()],
                "path_node_ids": [str(item).strip() for item in list(row.get("path_node_ids") or []) if str(item).strip()],
            }
        )
    plan = {
        "schema_version": "1.0.0",
        "partitioned": True,
        "partition_id": str(partition.get("partition_id", "")).strip(),
        "graph_id": str(partition.get("graph_id", "")).strip(),
        "segments": sorted(normalized_segments, key=lambda item: int(_as_int(item.get("segment_index", 0), 0))),
        "cross_shard_boundaries": sorted(
            [
                {
                    "boundary_node_id": str(item.get("boundary_node_id", "")).strip(),
                    "from_shard_id": str(item.get("from_shard_id", "")).strip(),
                    "to_shard_id": str(item.get("to_shard_id", "")).strip(),
                }
                for item in boundaries
                if str(item.get("boundary_node_id", "")).strip()
            ],
            key=lambda item: (str(item.get("boundary_node_id", "")), str(item.get("from_shard_id", "")), str(item.get("to_shard_id", ""))),
        ),
        "deterministic_fingerprint": "",
    }
    plan["deterministic_fingerprint"] = canonical_sha256(
        dict(plan, deterministic_fingerprint="")
    )
    return plan


def query_route_result(
    *,
    graph_row: Mapping[str, object],
    routing_policy_row: Mapping[str, object],
    from_node_id: str,
    to_node_id: str,
    constraints_row: Mapping[str, object] | None = None,
    partition_row: Mapping[str, object] | None = None,
    cache_state: Mapping[str, object] | None = None,
    max_cache_entries: int = 128,
    cost_units_per_query: int = 1,
) -> dict:
    graph = normalize_network_graph(graph_row)
    policy = _routing_policy(routing_policy_row)
    constraints = _route_constraints(constraints_row)
    graph_hash = canonical_sha256(graph)
    constraints_hash = canonical_sha256(constraints)
    cache_key = build_route_cache_key(
        graph_hash=str(graph_hash),
        from_node_id=str(from_node_id).strip(),
        to_node_id=str(to_node_id).strip(),
        route_policy_id=str(policy.get("policy_id", "")),
        constraints_hash=str(constraints_hash),
    )
    lookup = _cache_lookup(cache_state, cache_key)
    if bool(lookup.get("cache_hit", False)):
        entry = dict(lookup.get("entry") or {})
        route_result = normalize_route_result_row(dict(entry.get("route_result") or {}))
        return {
            "result": "complete",
            "cache_hit": True,
            "cache_key": str(cache_key),
            "graph_hash": str(graph_hash),
            "constraints_hash": str(constraints_hash),
            "route_result": route_result,
            "cross_shard_route_plan": dict(route_result.get("extensions", {}).get("cross_shard_route_plan") or {}),
            "route_cost_units": int(max(0, _as_int(cost_units_per_query, 1))),
            "cache_state": dict(cache_state or {"entries_by_key": {}, "next_sequence": 0}),
        }

    edge_ids = _route_with_constraints(
        graph_row=graph,
        routing_policy_row=policy,
        from_node_id=str(from_node_id).strip(),
        to_node_id=str(to_node_id).strip(),
        constraints_row=constraints,
    )
    path_node_ids = _path_node_ids(graph, str(from_node_id).strip(), edge_ids)
    total_cost = _route_total_cost(graph, edge_ids, str(policy.get("optimization_metric", "delay_ticks")))
    cross_shard_route_plan = build_cross_shard_route_plan(
        graph_row=graph,
        partition_row=partition_row,
        path_node_ids=list(path_node_ids),
        path_edge_ids=list(edge_ids),
    )
    route_result = normalize_route_result_row(
        {
            "schema_version": "1.0.0",
            "path_node_ids": list(path_node_ids),
            "path_edge_ids": list(edge_ids),
            "total_cost": int(total_cost),
            "deterministic_fingerprint": "",
            "extensions": {
                "graph_id": str(graph.get("graph_id", "")).strip(),
                "route_policy_id": str(policy.get("policy_id", "")).strip(),
                "graph_hash": str(graph_hash),
                "constraints_hash": str(constraints_hash),
                "cross_shard_route_plan": dict(cross_shard_route_plan),
            },
        }
    )
    next_cache_state = _cache_store(
        cache_state=cache_state,
        cache_key=str(cache_key),
        route_result=route_result,
        max_entries=int(max_cache_entries),
    )
    return {
        "result": "complete",
        "cache_hit": False,
        "cache_key": str(cache_key),
        "graph_hash": str(graph_hash),
        "constraints_hash": str(constraints_hash),
        "route_result": route_result,
        "cross_shard_route_plan": dict(cross_shard_route_plan),
        "route_cost_units": int(max(0, _as_int(cost_units_per_query, 1))),
        "cache_state": dict(next_cache_state),
    }


def route_query_edges(
    graph_row: Mapping[str, object],
    routing_policy_row: Mapping[str, object],
    from_node_id: str,
    to_node_id: str,
    *,
    constraints_row: Mapping[str, object] | None = None,
    partition_row: Mapping[str, object] | None = None,
) -> List[str]:
    result = query_route_result(
        graph_row=graph_row,
        routing_policy_row=routing_policy_row,
        from_node_id=from_node_id,
        to_node_id=to_node_id,
        constraints_row=constraints_row,
        partition_row=partition_row,
        cache_state={"entries_by_key": {}, "next_sequence": 0},
        max_cache_entries=0,
        cost_units_per_query=1,
    )
    return list((dict(result.get("route_result") or {})).get("path_edge_ids") or [])
