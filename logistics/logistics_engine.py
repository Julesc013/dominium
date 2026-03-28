"""Deterministic MAT-4 logistics graph, manifest, and shipment progression helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from core.flow.flow_engine import (
    flow_solver_policy_rows_by_id,
    tick_flow_channels,
)
from core.graph.network_graph_engine import (
    NetworkGraphError,
    normalize_network_graph as core_normalize_network_graph,
    route_delay_ticks as core_route_delay_ticks,
    route_loss_fraction as core_route_loss_fraction,
)
from core.graph.routing_engine import RoutingError, route_query_edges
from materials.dimension_engine import fixed_point_config_from_policy
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_LOGISTICS_INSUFFICIENT_STOCK = "refusal.logistics.insufficient_stock"
REFUSAL_LOGISTICS_INVALID_ROUTE = "refusal.logistics.invalid_route"
REFUSAL_LOGISTICS_FLOW_FAILURE = "refusal.logistics.flow_failure"

LOGISTICS_FLOW_QUANTITY_ID = "quantity.mass"
LOGISTICS_FLOW_DEFAULT_SOLVER_POLICY_ID = "flow.coarse_default"

_MANIFEST_TERMINAL_STATUSES = {"delivered", "lost", "failed"}


class LogisticsError(ValueError):
    """Deterministic logistics refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in (values or []) if str(item).strip()))


def _rows_by_id(rows: object, key_field: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get(key_field, ""))):
        token = str(row.get(key_field, "")).strip()
        if token:
            out[token] = dict(row)
    return out


def _inventory_hash(node_id: str, material_stocks: Mapping[str, object], batch_refs: List[object]) -> str:
    payload = {
        "node_id": str(node_id),
        "material_stocks": dict(
            (str(key).strip(), int(_as_int(value, 0)))
            for key, value in sorted((material_stocks or {}).items(), key=lambda item: str(item[0]))
            if str(key).strip()
        ),
        "batch_refs": _sorted_unique_strings(list(batch_refs or [])),
    }
    return canonical_sha256(payload)


def normalize_node_inventory(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    node_id = str(payload.get("node_id", "")).strip()
    if not node_id:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            "node inventory missing node_id",
            {"field": "node_id"},
        )
    stocks = {}
    for key in sorted((dict(payload.get("material_stocks") or {})).keys()):
        material_id = str(key).strip()
        quantity_mass = int(_as_int((dict(payload.get("material_stocks") or {})).get(key, 0), 0))
        if not material_id:
            continue
        if quantity_mass < 0:
            raise LogisticsError(
                REFUSAL_LOGISTICS_INVALID_ROUTE,
                "node inventory quantity must be non-negative",
                {"node_id": node_id, "material_id": material_id, "quantity_mass": int(quantity_mass)},
            )
        stocks[material_id] = int(quantity_mass)
    batch_refs = _sorted_unique_strings(list(payload.get("batch_refs") or []))
    inventory_hash = str(payload.get("inventory_hash", "")).strip() or _inventory_hash(node_id, stocks, batch_refs)
    return {
        "schema_version": "1.0.0",
        "node_id": node_id,
        "material_stocks": dict(stocks),
        "batch_refs": list(batch_refs),
        "inventory_hash": inventory_hash,
        "extensions": dict(payload.get("extensions") or {}),
    }


def build_inventory_index(inventory_rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(inventory_rows, list):
        return out
    for row in sorted((item for item in inventory_rows if isinstance(item, dict)), key=lambda item: str(item.get("node_id", ""))):
        normalized = normalize_node_inventory(row)
        out[str(normalized.get("node_id", ""))] = dict(normalized)
    return out


def inventory_rows_from_index(inventory_index: Mapping[str, object]) -> List[dict]:
    rows: List[dict] = []
    for node_id in sorted((inventory_index or {}).keys()):
        row = normalize_node_inventory(dict((inventory_index or {}).get(node_id) or {}))
        rows.append(row)
    return rows


def _normalize_routing_rule(rule_row: Mapping[str, object]) -> dict:
    row = dict(rule_row or {})
    rule_id = str(row.get("rule_id", "")).strip()
    tie_break_policy = str(row.get("tie_break_policy", "")).strip() or "edge_id_lexicographic"
    if not rule_id:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            "routing rule missing rule_id",
            {},
        )
    return {
        "schema_version": "1.0.0",
        "rule_id": rule_id,
        "description": str(row.get("description", "")).strip(),
        "tie_break_policy": tie_break_policy,
        "allow_multi_hop": bool(row.get("allow_multi_hop", False)),
        "constraints": dict(row.get("constraints") or {}),
        "extensions": dict(row.get("extensions") or {}),
    }


def routing_rule_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(registry_payload or {})
    direct = root.get("routing_rules")
    if not isinstance(direct, list):
        direct = ((root.get("record") or {}).get("routing_rules") or [])
    rows: Dict[str, dict] = {}
    for row in sorted((item for item in list(direct or []) if isinstance(item, dict)), key=lambda item: str(item.get("rule_id", ""))):
        normalized = _normalize_routing_rule(row)
        rows[str(normalized.get("rule_id", ""))] = normalized
    return rows


def _normalize_node(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    node_id = str(payload.get("node_id", "")).strip()
    node_type = str(payload.get("node_type", "")).strip()
    location_ref = str(payload.get("location_ref", "")).strip()
    if not node_id or not node_type or not location_ref:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            "logistics node missing required fields",
            {"node_id": node_id},
        )
    capacity_storage_raw = payload.get("capacity_storage")
    if capacity_storage_raw is None:
        capacity_storage = None
    else:
        capacity_storage = int(_as_int(capacity_storage_raw, 0))
        if capacity_storage < 0:
            raise LogisticsError(
                REFUSAL_LOGISTICS_INVALID_ROUTE,
                "logistics node capacity_storage must be >= 0",
                {"node_id": node_id, "capacity_storage": int(capacity_storage)},
            )
    return {
        "schema_version": "1.0.0",
        "node_id": node_id,
        "node_type": node_type,
        "location_ref": location_ref,
        "capacity_storage": capacity_storage,
        "tags": _sorted_unique_strings(list(payload.get("tags") or [])),
        "extensions": dict(payload.get("extensions") or {}),
    }


def _normalize_edge(row: Mapping[str, object], node_ids: set[str]) -> dict:
    payload = dict(row or {})
    edge_id = str(payload.get("edge_id", "")).strip()
    from_node_id = str(payload.get("from_node_id", "")).strip()
    to_node_id = str(payload.get("to_node_id", "")).strip()
    transport_mode = str(payload.get("transport_mode", "")).strip()
    if not edge_id or not from_node_id or not to_node_id or not transport_mode:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            "logistics edge missing required fields",
            {"edge_id": edge_id},
        )
    if from_node_id not in node_ids or to_node_id not in node_ids:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            "logistics edge references unknown node_id",
            {
                "edge_id": edge_id,
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
            },
        )
    capacity_mass_per_tick = int(_as_int(payload.get("capacity_mass_per_tick", 0), 0))
    delay_ticks = int(_as_int(payload.get("delay_ticks", 0), 0))
    if capacity_mass_per_tick < 0 or delay_ticks < 0:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            "logistics edge capacity/delay must be non-negative",
            {
                "edge_id": edge_id,
                "capacity_mass_per_tick": int(capacity_mass_per_tick),
                "delay_ticks": int(delay_ticks),
            },
        )
    loss_fraction_raw = payload.get("loss_fraction")
    if loss_fraction_raw is None:
        normalized_loss_fraction = 0
    else:
        normalized_loss_fraction = int(_as_int(loss_fraction_raw, 0))
        if normalized_loss_fraction < 0:
            raise LogisticsError(
                REFUSAL_LOGISTICS_INVALID_ROUTE,
                "logistics edge loss_fraction must be >= 0",
                {"edge_id": edge_id, "loss_fraction": int(normalized_loss_fraction)},
            )
    cost_units_per_mass = payload.get("cost_units_per_mass")
    if cost_units_per_mass is None:
        normalized_cost_units = None
    else:
        normalized_cost_units = int(_as_int(cost_units_per_mass, 0))
        if normalized_cost_units < 0:
            raise LogisticsError(
                REFUSAL_LOGISTICS_INVALID_ROUTE,
                "logistics edge cost_units_per_mass must be >= 0",
                {"edge_id": edge_id, "cost_units_per_mass": int(normalized_cost_units)},
            )
    return {
        "schema_version": "1.0.0",
        "edge_id": edge_id,
        "from_node_id": from_node_id,
        "to_node_id": to_node_id,
        "transport_mode": transport_mode,
        "capacity_mass_per_tick": int(capacity_mass_per_tick),
        "delay_ticks": int(delay_ticks),
        "loss_fraction": int(normalized_loss_fraction),
        "cost_units_per_mass": normalized_cost_units,
        "tags": _sorted_unique_strings(list(payload.get("tags") or [])),
        "extensions": dict(payload.get("extensions") or {}),
    }


def normalize_logistics_graph(graph_row: Mapping[str, object]) -> dict:
    row = dict(graph_row or {})
    graph_id = str(row.get("graph_id", "")).strip()
    rule_id = str(row.get("deterministic_routing_rule_id", "")).strip()
    if not graph_id or not rule_id:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            "logistics graph missing graph_id or deterministic_routing_rule_id",
            {"graph_id": graph_id, "deterministic_routing_rule_id": rule_id},
        )

    nodes_raw = list(row.get("nodes") or [])
    edges_raw = list(row.get("edges") or [])
    if not isinstance(nodes_raw, list) or not isinstance(edges_raw, list):
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            "logistics graph nodes/edges must be arrays",
            {"graph_id": graph_id},
        )

    nodes: Dict[str, dict] = {}
    for node_row in nodes_raw:
        if not isinstance(node_row, dict):
            continue
        normalized = _normalize_node(node_row)
        node_id = str(normalized.get("node_id", ""))
        if node_id in nodes:
            raise LogisticsError(
                REFUSAL_LOGISTICS_INVALID_ROUTE,
                "duplicate logistics node_id in graph",
                {"graph_id": graph_id, "node_id": node_id},
            )
        nodes[node_id] = normalized

    node_ids = set(nodes.keys())
    edges: Dict[str, dict] = {}
    for edge_row in edges_raw:
        if not isinstance(edge_row, dict):
            continue
        normalized = _normalize_edge(edge_row, node_ids=node_ids)
        edge_id = str(normalized.get("edge_id", ""))
        if edge_id in edges:
            raise LogisticsError(
                REFUSAL_LOGISTICS_INVALID_ROUTE,
                "duplicate logistics edge_id in graph",
                {"graph_id": graph_id, "edge_id": edge_id},
            )
        edges[edge_id] = normalized

    return {
        "schema_version": "1.0.0",
        "graph_id": graph_id,
        "nodes": [dict(nodes[node_id]) for node_id in sorted(nodes.keys())],
        "edges": [dict(edges[edge_id]) for edge_id in sorted(edges.keys())],
        "deterministic_routing_rule_id": rule_id,
        "version_introduced": str(row.get("version_introduced", "")).strip() or "1.0.0",
        "extensions": dict(row.get("extensions") or {}),
    }


def graph_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(registry_payload or {})
    direct = root.get("graphs")
    if not isinstance(direct, list):
        direct = ((root.get("record") or {}).get("graphs") or [])
    rows: Dict[str, dict] = {}
    for row in sorted((item for item in list(direct or []) if isinstance(item, dict)), key=lambda item: str(item.get("graph_id", ""))):
        normalized = normalize_logistics_graph(row)
        rows[str(normalized.get("graph_id", ""))] = normalized
    return rows


def _core_graph_payload(graph_row: Mapping[str, object]) -> dict:
    graph = normalize_logistics_graph(graph_row)
    core_nodes = []
    core_edges = []
    for node in list(graph.get("nodes") or []):
        node_row = dict(node)
        core_nodes.append(
            {
                "schema_version": "1.0.0",
                "node_id": str(node_row.get("node_id", "")).strip(),
                "node_type_id": str(node_row.get("node_type", "")).strip(),
                "payload_ref": {
                    "location_ref": str(node_row.get("location_ref", "")).strip(),
                    "capacity_storage": node_row.get("capacity_storage"),
                    "tags": list(node_row.get("tags") or []),
                },
                "tags": list(node_row.get("tags") or []),
                "extensions": dict(node_row.get("extensions") or {}),
            }
        )
    for edge in list(graph.get("edges") or []):
        edge_row = dict(edge)
        core_edges.append(
            {
                "schema_version": "1.0.0",
                "edge_id": str(edge_row.get("edge_id", "")).strip(),
                "from_node_id": str(edge_row.get("from_node_id", "")).strip(),
                "to_node_id": str(edge_row.get("to_node_id", "")).strip(),
                "edge_type_id": str(edge_row.get("transport_mode", "")).strip(),
                "payload_ref": {
                    "cost_units_per_mass": edge_row.get("cost_units_per_mass"),
                    "transport_mode": str(edge_row.get("transport_mode", "")).strip(),
                },
                "capacity": edge_row.get("capacity_mass_per_tick"),
                "delay_ticks": edge_row.get("delay_ticks"),
                "loss_fraction": edge_row.get("loss_fraction"),
                "extensions": dict(edge_row.get("extensions") or {}),
            }
        )
    return core_normalize_network_graph(
        {
        "schema_version": "1.0.0",
        "graph_id": str(graph.get("graph_id", "")).strip(),
        "node_type_schema_id": "logistics_node",
        "edge_type_schema_id": "logistics_edge",
        "nodes": core_nodes,
        "edges": core_edges,
        "deterministic_routing_policy_id": str(graph.get("deterministic_routing_rule_id", "")).strip(),
        "extensions": {"source_subsystem": "materials.logistics"},
        }
    )


def _core_routing_policy(rule_row: Mapping[str, object]) -> dict:
    rule = _normalize_routing_rule(rule_row)
    rule_id = str(rule.get("rule_id", "")).strip()
    optimization_metric = "delay_ticks"
    # Deterministic shortest-path tie-break is delegated to core_route_query (heapq-based).
    if rule_id == "route.shortest_delay":
        optimization_metric = "delay_ticks"
    elif rule_id == "route.min_cost_units":
        optimization_metric = "min_cost_units"
    return {
        "policy_id": rule_id,
        "description": str(rule.get("description", "")).strip(),
        "tie_break_policy": str(rule.get("tie_break_policy", "")).strip() or "edge_id_lexicographic",
        "allow_multi_hop": bool(rule.get("allow_multi_hop", False)),
        "optimization_metric": optimization_metric,
        "extensions": dict(rule.get("extensions") or {}),
    }


def _best_route(graph_row: Mapping[str, object], from_node_id: str, to_node_id: str, routing_rule: Mapping[str, object]) -> List[str]:
    try:
        return route_query_edges(
            _core_graph_payload(graph_row),
            _core_routing_policy(routing_rule),
            str(from_node_id).strip(),
            str(to_node_id).strip(),
            constraints_row=dict(_normalize_routing_rule(routing_rule).get("constraints") or {}),
        )
    except RoutingError as exc:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            str(exc),
            dict(exc.details),
        ) from exc
    except NetworkGraphError as exc:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            str(exc),
            dict(exc.details),
        ) from exc


def _route_delay_ticks(graph_row: Mapping[str, object], edge_ids: List[str]) -> int:
    try:
        return int(core_route_delay_ticks(_core_graph_payload(graph_row), list(edge_ids or [])))
    except NetworkGraphError as exc:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            str(exc),
            dict(exc.details),
        ) from exc


def _route_loss_fraction_raw(graph_row: Mapping[str, object], edge_ids: List[str], *, scale: int) -> int:
    try:
        return int(core_route_loss_fraction(_core_graph_payload(graph_row), list(edge_ids or []), scale=int(scale)))
    except NetworkGraphError as exc:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            str(exc),
            dict(exc.details),
        ) from exc


def _route_node_ids(graph_row: Mapping[str, object], *, from_node_id: str, edge_ids: List[str]) -> List[str]:
    graph = normalize_logistics_graph(graph_row)
    edge_index: Dict[str, dict] = {}
    for edge in list(graph.get("edges") or []):
        row = dict(edge or {})
        edge_id = str(row.get("edge_id", "")).strip()
        if edge_id:
            edge_index[edge_id] = row
    current = str(from_node_id).strip()
    nodes = [current] if current else []
    for edge_id in list(edge_ids or []):
        row = dict(edge_index.get(str(edge_id).strip()) or {})
        if not row:
            return []
        from_node = str(row.get("from_node_id", "")).strip()
        to_node = str(row.get("to_node_id", "")).strip()
        if current and from_node != current:
            return []
        current = to_node
        if current:
            nodes.append(current)
    return nodes


def _manifest_flow_channel(
    *,
    manifest_row: Mapping[str, object],
    fallback_solver_policy_id: str = LOGISTICS_FLOW_DEFAULT_SOLVER_POLICY_ID,
) -> dict:
    row = dict(manifest_row or {})
    ext = dict(row.get("extensions") or {})
    flow_channel = dict(ext.get("flow_channel") or {})
    if flow_channel:
        return flow_channel
    channel_id = str(ext.get("flow_channel_id", "")).strip()
    if not channel_id:
        channel_id = "flow.channel.{}".format(
            canonical_sha256(
                {
                    "manifest_id": str(row.get("manifest_id", "")).strip(),
                    "batch_id": str(row.get("batch_id", "")).strip(),
                    "material_id": str(row.get("material_id", "")).strip(),
                }
            )[:20]
        )
    return {
        "schema_version": "1.0.0",
        "channel_id": channel_id,
        "graph_id": str(row.get("graph_id", "")).strip(),
        "quantity_id": str(ext.get("flow_quantity_id", "")).strip() or LOGISTICS_FLOW_QUANTITY_ID,
        "source_node_id": str(row.get("from_node_id", "")).strip(),
        "sink_node_id": str(row.get("to_node_id", "")).strip(),
        "capacity_per_tick": None,
        "delay_ticks": 0,
        "loss_fraction": int(_as_int(ext.get("loss_fraction", 0), 0)),
        "solver_policy_id": str(ext.get("flow_solver_policy_id", "")).strip() or str(fallback_solver_policy_id).strip() or LOGISTICS_FLOW_DEFAULT_SOLVER_POLICY_ID,
        "priority": int(max(0, _as_int(ext.get("flow_priority", 0), 0))),
        "extensions": {
            "manifest_id": str(row.get("manifest_id", "")).strip(),
            "batch_id": str(row.get("batch_id", "")).strip(),
            "material_id": str(row.get("material_id", "")).strip(),
            "route_edge_ids": _sorted_unique_strings(list(ext.get("route_edge_ids") or [])),
            "route_node_ids": _sorted_unique_strings(list(ext.get("route_node_ids") or [])),
        },
    }


def _manifest_fingerprint(manifest_row: Mapping[str, object]) -> str:
    seed = dict(manifest_row or {})
    seed["deterministic_fingerprint"] = ""
    return canonical_sha256(seed)


def _event_fingerprint(event_row: Mapping[str, object]) -> str:
    seed = dict(event_row or {})
    seed["deterministic_fingerprint"] = ""
    return canonical_sha256(seed)


def _event_row(
    *,
    manifest_id: str,
    commitment_id: str,
    event_type: str,
    tick: int,
    quantity_mass: int,
    material_id: str,
    batch_id: str,
    route_edge_ids: List[str],
    actor_subject_id: str,
    sequence: int,
) -> dict:
    event_id = "event.shipment.{}".format(
        canonical_sha256(
            {
                "manifest_id": str(manifest_id),
                "commitment_id": str(commitment_id),
                "event_type": str(event_type),
                "tick": int(tick),
                "sequence": int(sequence),
            }
        )[:20]
    )
    row = {
        "event_id": event_id,
        "event_type": str(event_type),
        "manifest_id": str(manifest_id),
        "commitment_id": str(commitment_id),
        "tick": int(tick),
        "quantity_mass": int(quantity_mass),
        "material_id": str(material_id),
        "batch_id": str(batch_id),
        "route_edge_ids": _sorted_unique_strings(route_edge_ids),
        "actor_subject_id": str(actor_subject_id),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    row["deterministic_fingerprint"] = _event_fingerprint(row)
    return row


def _inventory_ensure(index: Dict[str, dict], node_id: str) -> dict:
    token = str(node_id).strip()
    row = dict(index.get(token) or {})
    if not row:
        row = {
            "schema_version": "1.0.0",
            "node_id": token,
            "material_stocks": {},
            "batch_refs": [],
            "inventory_hash": "",
            "extensions": {},
        }
    normalized = normalize_node_inventory(row)
    index[token] = normalized
    return normalized


def _inventory_apply(
    index: Dict[str, dict],
    *,
    node_id: str,
    material_id: str,
    delta_mass: int,
    batch_id: str = "",
    allow_negative: bool = False,
) -> dict:
    token = str(material_id).strip()
    if not token:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            "inventory mutation requires material_id",
            {"node_id": str(node_id)},
        )
    row = _inventory_ensure(index, node_id)
    stocks = dict(row.get("material_stocks") or {})
    current = int(_as_int(stocks.get(token, 0), 0))
    updated = int(current + int(delta_mass))
    if (not allow_negative) and updated < 0:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INSUFFICIENT_STOCK,
            "inventory mutation would produce negative stock",
            {
                "node_id": str(node_id),
                "material_id": token,
                "current_mass": int(current),
                "delta_mass": int(delta_mass),
            },
        )
    if updated <= 0:
        stocks.pop(token, None)
    else:
        stocks[token] = int(updated)
    batch_refs = _sorted_unique_strings(list(row.get("batch_refs") or []) + ([str(batch_id)] if str(batch_id).strip() else []))
    row["material_stocks"] = dict((key, int(stocks[key])) for key in sorted(stocks.keys()))
    row["batch_refs"] = list(batch_refs)
    row["inventory_hash"] = _inventory_hash(str(node_id), row["material_stocks"], batch_refs)
    index[str(node_id)] = row
    return row


def create_manifest_and_commitment(
    *,
    graph_row: Mapping[str, object],
    routing_rule_row: Mapping[str, object],
    inventory_index: Mapping[str, object] | None,
    from_node_id: str,
    to_node_id: str,
    batch_id: str,
    material_id: str,
    quantity_mass: int,
    earliest_depart_tick: int,
    actor_subject_id: str,
    intent_id: str,
    current_tick: int,
    numeric_policy: Mapping[str, object] | None = None,
    flow_solver_policy_registry: Mapping[str, object] | None = None,
) -> Dict[str, object]:
    graph = normalize_logistics_graph(graph_row)
    routing_rule = _normalize_routing_rule(routing_rule_row)

    source_node = str(from_node_id).strip()
    destination_node = str(to_node_id).strip()
    batch_token = str(batch_id).strip()
    material_token = str(material_id).strip()
    actor_token = str(actor_subject_id).strip() or "subject.unknown"
    intent_token = str(intent_id).strip() or "intent.unknown"

    if not source_node or not destination_node or not batch_token or not material_token:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            "manifest creation missing required identifiers",
            {
                "from_node_id": source_node,
                "to_node_id": destination_node,
                "batch_id": batch_token,
                "material_id": material_token,
            },
        )

    quantity_mass_raw = int(_as_int(quantity_mass, -1))
    if quantity_mass_raw < 0:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INVALID_ROUTE,
            "manifest quantity_mass must be >= 0",
            {"quantity_mass": int(quantity_mass_raw)},
        )

    inventory = build_inventory_index(list((inventory_index or {}).values()) if isinstance(inventory_index, dict) else inventory_index)
    source_inventory = _inventory_ensure(inventory, source_node)
    available_mass = int(_as_int((dict(source_inventory.get("material_stocks") or {})).get(material_token, 0), 0))
    if available_mass < quantity_mass_raw:
        raise LogisticsError(
            REFUSAL_LOGISTICS_INSUFFICIENT_STOCK,
            "source logistics node does not have enough stock for manifest",
            {
                "node_id": source_node,
                "material_id": material_token,
                "available_mass": int(available_mass),
                "requested_mass": int(quantity_mass_raw),
            },
        )

    route_edge_ids = _best_route(graph, source_node, destination_node, routing_rule)
    route_node_ids = _route_node_ids(graph, from_node_id=source_node, edge_ids=route_edge_ids)
    policy = fixed_point_config_from_policy(numeric_policy)
    loss_fraction_raw = _route_loss_fraction_raw(graph, route_edge_ids, scale=int(policy.scale))
    depart_tick = int(max(int(_as_int(current_tick, 0)), int(_as_int(earliest_depart_tick, 0))))
    arrive_tick = int(depart_tick + _route_delay_ticks(graph, route_edge_ids))

    solver_policies = flow_solver_policy_rows_by_id(flow_solver_policy_registry)
    if not solver_policies:
        solver_policies = {
            LOGISTICS_FLOW_DEFAULT_SOLVER_POLICY_ID: {
                "schema_version": "1.0.0",
                "solver_policy_id": LOGISTICS_FLOW_DEFAULT_SOLVER_POLICY_ID,
                "mode": "bulk",
                "allow_partial_transfer": True,
                "overflow_policy": "queue",
                "extensions": {},
            }
        }
    selected_solver_policy_id = str(
        (dict(routing_rule.get("extensions") or {})).get("flow_solver_policy_id", "")
    ).strip() or LOGISTICS_FLOW_DEFAULT_SOLVER_POLICY_ID
    if selected_solver_policy_id not in solver_policies:
        selected_solver_policy_id = LOGISTICS_FLOW_DEFAULT_SOLVER_POLICY_ID

    identity = {
        "graph_id": str(graph.get("graph_id", "")),
        "rule_id": str(routing_rule.get("rule_id", "")),
        "from_node_id": source_node,
        "to_node_id": destination_node,
        "batch_id": batch_token,
        "material_id": material_token,
        "quantity_mass": int(quantity_mass_raw),
        "scheduled_depart_tick": int(depart_tick),
        "scheduled_arrive_tick": int(arrive_tick),
        "route_edge_ids": list(route_edge_ids),
        "intent_id": intent_token,
        "created_tick": int(_as_int(current_tick, 0)),
    }
    digest = canonical_sha256(identity)
    manifest_id = "manifest.{}".format(digest[:20])
    commitment_id = "commitment.shipment.{}".format(digest[:20])
    flow_channel_id = "flow.channel.{}".format(digest[:20])
    flow_channel = {
        "schema_version": "1.0.0",
        "channel_id": flow_channel_id,
        "graph_id": str(graph.get("graph_id", "")),
        "quantity_id": LOGISTICS_FLOW_QUANTITY_ID,
        "source_node_id": source_node,
        "sink_node_id": destination_node,
        "capacity_per_tick": None,
        "delay_ticks": 0,
        "loss_fraction": int(loss_fraction_raw),
        "solver_policy_id": selected_solver_policy_id,
        "priority": 0,
        "extensions": {
            "manifest_id": manifest_id,
            "batch_id": batch_token,
            "material_id": material_token,
            "route_edge_ids": list(route_edge_ids),
            "route_node_ids": list(route_node_ids),
        },
    }

    manifest = {
        "schema_version": "1.0.0",
        "manifest_id": manifest_id,
        "graph_id": str(graph.get("graph_id", "")),
        "from_node_id": source_node,
        "to_node_id": destination_node,
        "batch_id": batch_token,
        "material_id": material_token,
        "quantity_mass": int(quantity_mass_raw),
        "scheduled_depart_tick": int(depart_tick),
        "scheduled_arrive_tick": int(arrive_tick),
        "status": "planned",
        "provenance_event_ids": [],
        "deterministic_fingerprint": "",
        "extensions": {
            "routing_rule_id": str(routing_rule.get("rule_id", "")),
            "route_edge_ids": list(route_edge_ids),
            "route_node_ids": list(route_node_ids),
            "loss_fraction": int(loss_fraction_raw),
            "commitment_id": commitment_id,
            "created_tick": int(_as_int(current_tick, 0)),
            "actor_subject_id": actor_token,
            "flow_channel_id": flow_channel_id,
            "flow_quantity_id": LOGISTICS_FLOW_QUANTITY_ID,
            "flow_solver_policy_id": selected_solver_policy_id,
            "flow_channel": dict(flow_channel),
            "reenactment_descriptor": {
                "route_edge_ids": list(route_edge_ids),
                "route_node_ids": list(route_node_ids),
                "departure_tick": int(depart_tick),
                "arrival_tick": int(arrive_tick),
                "quantity_mass": int(quantity_mass_raw),
                "actor_subject_id": actor_token,
            },
        },
    }
    manifest["deterministic_fingerprint"] = _manifest_fingerprint(manifest)

    commitment = {
        "schema_version": "1.0.0",
        "commitment_id": commitment_id,
        "manifest_id": manifest_id,
        "actor_subject_id": actor_token,
        "created_tick": int(_as_int(current_tick, 0)),
        "status": "planned",
        "extensions": {
            "process_id": "process.manifest_create",
            "graph_id": str(graph.get("graph_id", "")),
        },
    }

    return {
        "manifest": manifest,
        "commitment": commitment,
        "route_edge_ids": list(route_edge_ids),
        "route_node_ids": list(route_node_ids),
        "loss_fraction": int(loss_fraction_raw),
        "flow_channel": dict(flow_channel),
        "inventory_index": inventory,
    }


def _manifest_rows_by_id(rows: object) -> Dict[str, dict]:
    return _rows_by_id(rows, "manifest_id")


def _commitment_rows_by_manifest(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("commitment_id", ""))):
        manifest_id = str(row.get("manifest_id", "")).strip()
        commitment_id = str(row.get("commitment_id", "")).strip()
        if manifest_id and commitment_id:
            out[manifest_id] = dict(row)
    return out


def tick_manifests(
    *,
    graph_row: Mapping[str, object],
    manifests: object,
    commitments: object,
    inventory_index: Mapping[str, object] | None,
    current_tick: int,
    max_updates: int,
    actor_subject_id: str,
    numeric_policy: Mapping[str, object] | None = None,
    event_sequence_start: int = 0,
    flow_solver_policy_registry: Mapping[str, object] | None = None,
    graph_partition_row: Mapping[str, object] | None = None,
) -> Dict[str, object]:
    graph = normalize_logistics_graph(graph_row)
    policy = fixed_point_config_from_policy(numeric_policy)

    manifest_map = _manifest_rows_by_id(manifests)
    commitment_by_manifest = _commitment_rows_by_manifest(commitments)
    inventory = build_inventory_index(list((inventory_index or {}).values()) if isinstance(inventory_index, dict) else inventory_index)

    processed_count = 0
    remaining_count = 0
    events: List[dict] = []
    flow_transfer_events: List[dict] = []
    flow_cross_shard_plans: List[dict] = []
    sequence = int(max(0, _as_int(event_sequence_start, 0)))
    loss_entries: List[dict] = []
    solver_policies = flow_solver_policy_rows_by_id(flow_solver_policy_registry)
    if not solver_policies:
        solver_policies = {
            LOGISTICS_FLOW_DEFAULT_SOLVER_POLICY_ID: {
                "schema_version": "1.0.0",
                "solver_policy_id": LOGISTICS_FLOW_DEFAULT_SOLVER_POLICY_ID,
                "mode": "bulk",
                "allow_partial_transfer": True,
                "overflow_policy": "queue",
                "extensions": {},
            }
        }

    for manifest_id in sorted(manifest_map.keys()):
        row = dict(manifest_map.get(manifest_id) or {})
        status = str(row.get("status", "")).strip() or "planned"
        if status in _MANIFEST_TERMINAL_STATUSES:
            continue

        if processed_count >= int(max_updates):
            remaining_count += 1
            continue

        processed_count += 1
        extensions = dict(row.get("extensions") or {})
        provenance_event_ids = _sorted_unique_strings(list(row.get("provenance_event_ids") or []))
        commitment = dict(commitment_by_manifest.get(manifest_id) or {})
        commitment_status = str(commitment.get("status", "")).strip() or "planned"

        source_node = str(row.get("from_node_id", "")).strip()
        destination_node = str(row.get("to_node_id", "")).strip()
        batch_id = str(row.get("batch_id", "")).strip()
        material_id = str(row.get("material_id", "")).strip()
        quantity_mass = int(_as_int(row.get("quantity_mass", 0), 0))
        depart_tick = int(_as_int(row.get("scheduled_depart_tick", 0), 0))
        arrive_tick = int(_as_int(row.get("scheduled_arrive_tick", depart_tick), depart_tick))
        route_edge_ids = _sorted_unique_strings(list(extensions.get("route_edge_ids") or []))
        commitment_id = str(extensions.get("commitment_id", "")).strip() or str(commitment.get("commitment_id", "")).strip()

        if status == "planned" and int(current_tick) >= int(depart_tick):
            source_inventory = _inventory_ensure(inventory, source_node)
            available_mass = int(_as_int((dict(source_inventory.get("material_stocks") or {})).get(material_id, 0), 0))
            if available_mass < quantity_mass:
                row["status"] = "failed"
                if commitment:
                    commitment_status = "failed"
                extensions["failure_reason"] = REFUSAL_LOGISTICS_INSUFFICIENT_STOCK
            else:
                _inventory_apply(
                    inventory,
                    node_id=source_node,
                    material_id=material_id,
                    delta_mass=-1 * int(quantity_mass),
                    batch_id=batch_id,
                    allow_negative=False,
                )
                row["status"] = "in_transit"
                if commitment:
                    commitment_status = "executing"
                event = _event_row(
                    manifest_id=manifest_id,
                    commitment_id=commitment_id,
                    event_type="shipment_depart",
                    tick=int(current_tick),
                    quantity_mass=int(quantity_mass),
                    material_id=material_id,
                    batch_id=batch_id,
                    route_edge_ids=route_edge_ids,
                    actor_subject_id=actor_subject_id,
                    sequence=sequence,
                )
                sequence += 1
                events.append(event)
                provenance_event_ids = _sorted_unique_strings(provenance_event_ids + [str(event.get("event_id", ""))])
                status = "in_transit"

        if str(row.get("status", "")).strip() == "in_transit" and int(current_tick) >= int(arrive_tick):
            flow_channel = _manifest_flow_channel(
                manifest_row=row,
                fallback_solver_policy_id=LOGISTICS_FLOW_DEFAULT_SOLVER_POLICY_ID,
            )
            try:
                flow_tick = tick_flow_channels(
                    channels=[flow_channel],
                    node_balances={
                        str(flow_channel.get("source_node_id", "")): int(quantity_mass),
                        str(flow_channel.get("sink_node_id", "")): 0,
                    },
                    current_tick=int(current_tick),
                    fixed_point_scale=int(policy.scale),
                    solver_policies=solver_policies,
                    conserved_quantity_ids=[LOGISTICS_FLOW_QUANTITY_ID],
                    max_channels=1,
                    strict_budget=False,
                    sink_capacities={},
                    channel_runtime={},
                    graph_row=_core_graph_payload(graph),
                    partition_row=graph_partition_row,
                    cost_units_per_channel=1,
                )
            except Exception as exc:
                raise LogisticsError(
                    REFUSAL_LOGISTICS_FLOW_FAILURE,
                    "flow channel tick failed during manifest delivery",
                    {
                        "manifest_id": manifest_id,
                        "channel_id": str(flow_channel.get("channel_id", "")),
                        "error": str(exc),
                    },
                ) from exc

            flow_transfer_events.extend(
                dict(item)
                for item in list(flow_tick.get("transfer_events") or [])
                if isinstance(item, dict)
            )
            flow_cross_shard_plans.extend(
                dict(item)
                for item in list(flow_tick.get("cross_shard_transfer_plans") or [])
                if isinstance(item, dict)
            )
            channel_results = list(flow_tick.get("channel_results") or [])
            channel_result = dict(channel_results[0] if channel_results else {})
            loss_mass = int(_as_int(channel_result.get("lost_amount", 0), 0))
            delivered_mass = int(_as_int(channel_result.get("transferred_amount", 0), 0))
            if delivered_mass > 0:
                _inventory_apply(
                    inventory,
                    node_id=destination_node,
                    material_id=material_id,
                    delta_mass=int(delivered_mass),
                    batch_id=batch_id,
                    allow_negative=False,
                )
            arrive_event = _event_row(
                manifest_id=manifest_id,
                commitment_id=commitment_id,
                event_type="shipment_arrive",
                tick=int(current_tick),
                quantity_mass=int(delivered_mass),
                material_id=material_id,
                batch_id=batch_id,
                route_edge_ids=route_edge_ids,
                actor_subject_id=actor_subject_id,
                sequence=sequence,
            )
            sequence += 1
            events.append(arrive_event)
            provenance_event_ids = _sorted_unique_strings(provenance_event_ids + [str(arrive_event.get("event_id", ""))])
            extensions["flow_channel"] = dict(flow_channel)
            if flow_transfer_events:
                latest_flow_event = dict(flow_transfer_events[-1])
                extensions["last_flow_transfer_event_id"] = str(latest_flow_event.get("event_id", "")).strip()

            if loss_mass > 0:
                loss_event = _event_row(
                    manifest_id=manifest_id,
                    commitment_id=commitment_id,
                    event_type="shipment_lost",
                    tick=int(current_tick),
                    quantity_mass=int(loss_mass),
                    material_id=material_id,
                    batch_id=batch_id,
                    route_edge_ids=route_edge_ids,
                    actor_subject_id=actor_subject_id,
                    sequence=sequence,
                )
                sequence += 1
                events.append(loss_event)
                provenance_event_ids = _sorted_unique_strings(provenance_event_ids + [str(loss_event.get("event_id", ""))])
                loss_entries.append(
                    {
                        "manifest_id": manifest_id,
                        "material_id": material_id,
                        "lost_mass": int(loss_mass),
                    }
                )
                row["status"] = "lost"
                if commitment:
                    commitment_status = "failed"
            else:
                row["status"] = "delivered"
                if commitment:
                    commitment_status = "completed"

        row["provenance_event_ids"] = list(provenance_event_ids)
        row["extensions"] = dict(extensions)
        row["deterministic_fingerprint"] = _manifest_fingerprint(row)
        manifest_map[manifest_id] = row

        if commitment:
            commitment["status"] = commitment_status
            commitment_by_manifest[manifest_id] = commitment

    manifest_rows = [dict(manifest_map[manifest_id]) for manifest_id in sorted(manifest_map.keys())]
    commitment_rows = [dict(commitment_by_manifest[manifest_id]) for manifest_id in sorted(commitment_by_manifest.keys())]

    return {
        "manifests": manifest_rows,
        "commitments": commitment_rows,
        "inventory_index": inventory,
        "events": sorted(events, key=lambda item: (int(item.get("tick", 0)), str(item.get("event_id", "")))),
        "flow_transfer_events": sorted(
            (dict(item) for item in flow_transfer_events if isinstance(item, dict)),
            key=lambda item: (int(item.get("tick", 0)), str(item.get("event_id", ""))),
        ),
        "flow_cross_shard_plans": sorted(
            (dict(item) for item in flow_cross_shard_plans if isinstance(item, dict)),
            key=lambda item: (str(item.get("channel_id", "")), int(item.get("tick", 0))),
        ),
        "processed_count": int(processed_count),
        "remaining_count": int(remaining_count),
        "loss_entries": sorted(
            (dict(item) for item in loss_entries if isinstance(item, dict)),
            key=lambda item: (str(item.get("manifest_id", "")), str(item.get("material_id", ""))),
        ),
        "route_computation_count": 0,
        "next_event_sequence": int(sequence),
    }


def manifest_summary(manifests: object) -> dict:
    rows = [dict(item) for item in list(manifests or []) if isinstance(item, dict)]
    by_status = {"planned": 0, "in_transit": 0, "delivered": 0, "lost": 0, "failed": 0}
    total_mass = 0
    for row in sorted(rows, key=lambda item: str(item.get("manifest_id", ""))):
        status = str(row.get("status", "")).strip() or "planned"
        if status not in by_status:
            by_status[status] = 0
        by_status[status] += 1
        total_mass += int(_as_int(row.get("quantity_mass", 0), 0))
    payload = {
        "manifest_count": len(rows),
        "total_quantity_mass": int(total_mass),
        "status_counts": dict((key, int(by_status[key])) for key in sorted(by_status.keys())),
    }
    payload["summary_hash"] = canonical_sha256(payload)
    return payload
