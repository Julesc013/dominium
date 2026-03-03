"""Deterministic ELEC-1 power-network helpers (E0/E1 baseline)."""

from __future__ import annotations

import math
from typing import Dict, List, Mapping

from src.core.flow import normalize_flow_channel
from src.core.graph.network_graph_engine import normalize_network_graph
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_ELEC_NETWORK_INVALID = "refusal.elec.network_invalid"
REFUSAL_ELEC_SPEC_NONCOMPLIANT = "refusal.elec.spec_noncompliant"

_VALID_NODE_KINDS = {"bus", "generator", "load", "storage", "breaker"}
_VALID_EDGE_KINDS = {"conductor", "switch", "transformer_stub"}

_Q_ACTIVE = "quantity.power.active_stub"
_Q_REACTIVE = "quantity.power.reactive_stub"
_Q_APPARENT = "quantity.power.apparent_stub"


class ElectricError(ValueError):
    """Deterministic electrical-domain refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code or REFUSAL_ELEC_NETWORK_INVALID)
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
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda token: str(token)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def compute_pf_permille(*, active_p: int, apparent_s: int) -> int:
    p = int(max(0, _as_int(active_p, 0)))
    s = int(max(0, _as_int(apparent_s, 0)))
    if s <= 0:
        return 1000
    return int(max(0, min(1000, (p * 1000) // s)))


def _apparent_from_components(*, active_p: int, reactive_q: int) -> int:
    p = int(max(0, _as_int(active_p, 0)))
    q = int(max(0, _as_int(reactive_q, 0)))
    return int(math.isqrt((p * p) + (q * q)))


def normalize_elec_node_payload(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    node_kind = str(payload.get("node_kind", "")).strip()
    if node_kind not in _VALID_NODE_KINDS:
        raise ElectricError(
            REFUSAL_ELEC_NETWORK_INVALID,
            "elec node payload requires valid node_kind",
            {"node_kind": node_kind},
        )
    result = {
        "schema_version": "1.0.0",
        "node_kind": node_kind,
        "spec_id": None if payload.get("spec_id") is None else str(payload.get("spec_id", "")).strip() or None,
        "model_bindings": _sorted_tokens(payload.get("model_bindings")),
        "safety_instances": _sorted_tokens(payload.get("safety_instances")),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(payload.get("extensions"))),
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def normalize_elec_edge_payload(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    edge_kind = str(payload.get("edge_kind", "")).strip()
    if edge_kind not in _VALID_EDGE_KINDS:
        raise ElectricError(
            REFUSAL_ELEC_NETWORK_INVALID,
            "elec edge payload requires valid edge_kind",
            {"edge_kind": edge_kind},
        )
    length = int(max(0, _as_int(payload.get("length", 0), 0)))
    resistance_proxy = int(max(0, _as_int(payload.get("resistance_proxy", 0), 0)))
    capacity_rating = int(max(0, _as_int(payload.get("capacity_rating", 0), 0)))
    result = {
        "schema_version": "1.0.0",
        "edge_kind": edge_kind,
        "length": int(length),
        "resistance_proxy": int(resistance_proxy),
        "capacity_rating": int(capacity_rating),
        "spec_id": None if payload.get("spec_id") is None else str(payload.get("spec_id", "")).strip() or None,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(payload.get("extensions"))),
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def deterministic_power_channel_id(*, graph_id: str, edge_id: str) -> str:
    digest = canonical_sha256(
        {
            "graph_id": str(graph_id or "").strip(),
            "edge_id": str(edge_id or "").strip(),
            "kind": "power_flow_channel",
        }
    )
    return "channel.elec.{}".format(digest[:16])


def build_power_flow_channel(
    *,
    graph_id: str,
    edge_id: str,
    source_node_id: str,
    sink_node_id: str,
    capacity_rating: int,
    solver_policy_id: str = "flow.solver.default",
    component_capacity_policy_id: str = "comp_capacity.default_bundle",
    component_loss_policy_id: str = "comp_loss.default_bundle",
) -> dict:
    channel_id = deterministic_power_channel_id(graph_id=graph_id, edge_id=edge_id)
    return normalize_flow_channel(
        {
            "schema_version": "1.1.0",
            "channel_id": channel_id,
            "graph_id": str(graph_id or "").strip(),
            "quantity_bundle_id": "bundle.power_phasor",
            "component_capacity_policy_id": str(component_capacity_policy_id or "").strip() or None,
            "component_loss_policy_id": str(component_loss_policy_id or "").strip() or None,
            "source_node_id": str(source_node_id or "").strip(),
            "sink_node_id": str(sink_node_id or "").strip(),
            "capacity_per_tick": int(max(0, _as_int(capacity_rating, 0))),
            "delay_ticks": 0,
            "loss_fraction": 0,
            "solver_policy_id": str(solver_policy_id or "").strip() or "flow.solver.default",
            "priority": 0,
            "extensions": {
                "edge_id": str(edge_id or "").strip(),
                "component_weights": {
                    _Q_ACTIVE: 1000,
                    _Q_REACTIVE: 1000,
                    _Q_APPARENT: 1000,
                },
            },
        }
    )


def _binding_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in list(rows or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("binding_id", ""))):
        binding_id = str(row.get("binding_id", "")).strip()
        if binding_id:
            out[binding_id] = dict(row)
    return out


def _load_binding_rows_for_node(*, node_payload: Mapping[str, object], model_binding_rows_by_id: Mapping[str, dict]) -> List[dict]:
    binding_ids = _sorted_tokens(node_payload.get("model_bindings"))
    rows = []
    for binding_id in binding_ids:
        row = dict(model_binding_rows_by_id.get(binding_id) or {})
        if row:
            rows.append(row)
    return sorted(rows, key=lambda row: (str(row.get("model_id", "")), str(row.get("binding_id", ""))))


def _evaluate_load_from_binding(binding_row: Mapping[str, object]) -> dict:
    model_id = str(binding_row.get("model_id", "")).strip()
    params = _as_map(binding_row.get("parameters"))
    demand_p = int(max(0, _as_int(params.get("demand_p", params.get("demand", 0)), 0)))
    if model_id == "model.elec_load_resistive_stub":
        p = int(demand_p)
        q = 0
        s = int(p)
    elif model_id == "model.elec_load_motor_stub":
        pf_permille = int(max(1, min(1000, _as_int(params.get("pf_permille", 850), 850))))
        p = int(demand_p)
        s = int((p * 1000 + pf_permille - 1) // pf_permille) if p > 0 else 0
        q2 = max(0, int(s * s) - int(p * p))
        q = int(math.isqrt(q2))
    else:
        p = 0
        q = 0
        s = 0
    return {"P": int(p), "Q": int(q), "S": int(max(s, _apparent_from_components(active_p=p, reactive_q=q)))}


def _aggregate_load_for_node(*, node_payload: Mapping[str, object], model_binding_rows_by_id: Mapping[str, dict]) -> dict:
    p = 0
    q = 0
    s = 0
    for binding_row in _load_binding_rows_for_node(node_payload=node_payload, model_binding_rows_by_id=model_binding_rows_by_id):
        load = _evaluate_load_from_binding(binding_row)
        p += int(load.get("P", 0))
        q += int(load.get("Q", 0))
        s += int(load.get("S", 0))
    if s <= 0:
        s = _apparent_from_components(active_p=p, reactive_q=q)
    return {"P": int(max(0, p)), "Q": int(max(0, q)), "S": int(max(0, s))}


def _weighted_integer_split(*, total: int, keys: List[str], weights: Mapping[str, int]) -> Dict[str, int]:
    amount = int(max(0, _as_int(total, 0)))
    ordered_keys = [str(key).strip() for key in list(keys or []) if str(key).strip()]
    if not ordered_keys:
        return {}
    total_weight = 0
    for key in ordered_keys:
        total_weight += int(max(0, _as_int(weights.get(key, 1), 1)))
    if total_weight <= 0:
        total_weight = len(ordered_keys)
    base: Dict[str, int] = {}
    remainders: List[tuple] = []
    allocated = 0
    for key in ordered_keys:
        weight = int(max(0, _as_int(weights.get(key, 1), 1)))
        numer = int(amount * weight)
        part = int(numer // total_weight)
        rem = int(numer % total_weight)
        base[key] = int(part)
        allocated += int(part)
        remainders.append((rem, key))
    remaining = int(max(0, amount - allocated))
    for _rem, key in sorted(remainders, key=lambda row: (-1 * int(row[0]), str(row[1]))):
        if remaining <= 0:
            break
        base[key] = int(base.get(key, 0) + 1)
        remaining -= 1
    return dict((key, int(base.get(key, 0))) for key in ordered_keys)


def solve_power_network_e1(
    *,
    graph_row: Mapping[str, object],
    model_binding_rows: object,
    current_tick: int,
    max_processed_edges: int,
) -> dict:
    graph = normalize_network_graph(graph_row)
    graph_id = str(graph.get("graph_id", "")).strip()
    nodes = [dict(item) for item in list(graph.get("nodes") or []) if isinstance(item, Mapping)]
    edges = [dict(item) for item in list(graph.get("edges") or []) if isinstance(item, Mapping)]
    if not graph_id:
        raise ElectricError(REFUSAL_ELEC_NETWORK_INVALID, "power graph missing graph_id", {})

    binding_rows_by_id = _binding_rows_by_id(model_binding_rows)
    node_loads: Dict[str, dict] = {}
    for node in sorted(nodes, key=lambda row: str(row.get("node_id", ""))):
        node_id = str(node.get("node_id", "")).strip()
        payload = normalize_elec_node_payload(_as_map(node.get("payload")))
        if payload.get("node_kind") == "load":
            node_loads[node_id] = _aggregate_load_for_node(node_payload=payload, model_binding_rows_by_id=binding_rows_by_id)

    total_p = sum(int(_as_int(row.get("P", 0), 0)) for row in node_loads.values())
    total_q = sum(int(_as_int(row.get("Q", 0), 0)) for row in node_loads.values())
    total_s = max(_apparent_from_components(active_p=total_p, reactive_q=total_q), sum(int(_as_int(row.get("S", 0), 0)) for row in node_loads.values()))

    edge_rows = sorted(edges, key=lambda row: str(row.get("edge_id", "")))
    if int(max_processed_edges) <= 0 or len(edge_rows) > int(max_processed_edges):
        return solve_power_network_e0(graph_row=graph, model_binding_rows=model_binding_rows, current_tick=current_tick, reason="degrade.elec.e1_budget")

    weights = {}
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        payload = normalize_elec_edge_payload(_as_map(edge.get("payload")))
        weights[edge_id] = int(max(1, _as_int(payload.get("capacity_rating", 0), 0)))
    p_by_edge = _weighted_integer_split(total=total_p, keys=[str(edge.get("edge_id", "")).strip() for edge in edge_rows], weights=weights)
    q_by_edge = _weighted_integer_split(total=total_q, keys=[str(edge.get("edge_id", "")).strip() for edge in edge_rows], weights=weights)
    s_by_edge = _weighted_integer_split(total=total_s, keys=[str(edge.get("edge_id", "")).strip() for edge in edge_rows], weights=weights)

    edge_status_rows: List[dict] = []
    flow_channels: List[dict] = []
    overloaded_channel_ids: List[str] = []
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        from_node_id = str(edge.get("from_node_id", "")).strip()
        to_node_id = str(edge.get("to_node_id", "")).strip()
        payload = normalize_elec_edge_payload(_as_map(edge.get("payload")))
        capacity = int(max(0, _as_int(payload.get("capacity_rating", 0), 0)))
        resistance = int(max(0, _as_int(payload.get("resistance_proxy", 0), 0)))
        p_req = int(max(0, _as_int(p_by_edge.get(edge_id, 0), 0)))
        q_req = int(max(0, _as_int(q_by_edge.get(edge_id, 0), 0)))
        s_req = int(max(0, _as_int(s_by_edge.get(edge_id, 0), 0)))
        overloaded = bool((capacity <= 0 and s_req > 0) or (capacity > 0 and s_req > capacity))
        if capacity > 0 and s_req > capacity:
            scale = capacity
            p_req = int((p_req * scale) // max(1, s_req))
            q_req = int((q_req * scale) // max(1, s_req))
            s_req = int(scale)
        loss_p = int((p_req * resistance) // max(1, capacity if capacity > 0 else 1))
        p_del = int(max(0, p_req - loss_p))
        q_del = int(max(0, q_req))
        s_del = int(max(_apparent_from_components(active_p=p_del, reactive_q=q_del), min(s_req, p_del + q_del)))
        channel = build_power_flow_channel(
            graph_id=graph_id,
            edge_id=edge_id,
            source_node_id=from_node_id,
            sink_node_id=to_node_id,
            capacity_rating=capacity,
        )
        flow_channels.append(channel)
        channel_id = str(channel.get("channel_id", "")).strip()
        if overloaded and channel_id:
            overloaded_channel_ids.append(channel_id)
        pf_permille = compute_pf_permille(active_p=p_del, apparent_s=s_del)
        edge_status_rows.append(
            {
                "edge_id": edge_id,
                "channel_id": channel_id,
                "tier": "E1",
                "P": int(p_del),
                "Q": int(q_del),
                "S": int(s_del),
                "pf_permille": int(pf_permille),
                "heat_loss_stub": int(loss_p),
                "capacity_rating": int(capacity),
                "overloaded": bool(overloaded),
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "edge_id": edge_id,
                        "P": int(p_del),
                        "Q": int(q_del),
                        "S": int(s_del),
                        "heat_loss_stub": int(loss_p),
                        "overloaded": bool(overloaded),
                    }
                ),
            }
        )

    power_flow_hash = canonical_sha256(
        [
            {"edge_id": str(row.get("edge_id", "")), "P": int(_as_int(row.get("P", 0), 0)), "Q": int(_as_int(row.get("Q", 0), 0)), "S": int(_as_int(row.get("S", 0), 0))}
            for row in sorted(edge_status_rows, key=lambda row: str(row.get("edge_id", "")))
        ]
    )
    return {
        "mode": "E1",
        "graph_id": graph_id,
        "flow_channels": flow_channels,
        "edge_status_rows": sorted(edge_status_rows, key=lambda row: str(row.get("edge_id", ""))),
        "node_status_rows": sorted(
            (
                {
                    "node_id": node_id,
                    "node_kind": "load",
                    "P_demand": int(max(0, _as_int(load.get("P", 0), 0))),
                    "Q_demand": int(max(0, _as_int(load.get("Q", 0), 0))),
                    "S_demand": int(max(0, _as_int(load.get("S", 0), 0))),
                }
                for node_id, load in node_loads.items()
            ),
            key=lambda row: str(row.get("node_id", "")),
        ),
        "overloaded_channel_ids": sorted(set(overloaded_channel_ids)),
        "budget_outcome": "complete",
        "power_flow_hash": power_flow_hash,
    }


def solve_power_network_e0(
    *,
    graph_row: Mapping[str, object],
    model_binding_rows: object,
    current_tick: int,
    reason: str = "degrade.elec.e1_disabled",
) -> dict:
    del current_tick
    graph = normalize_network_graph(graph_row)
    graph_id = str(graph.get("graph_id", "")).strip()
    binding_rows_by_id = _binding_rows_by_id(model_binding_rows)
    total_p = 0
    for node in sorted((dict(item) for item in list(graph.get("nodes") or []) if isinstance(item, Mapping)), key=lambda row: str(row.get("node_id", ""))):
        payload = normalize_elec_node_payload(_as_map(node.get("payload")))
        if payload.get("node_kind") != "load":
            continue
        load = _aggregate_load_for_node(node_payload=payload, model_binding_rows_by_id=binding_rows_by_id)
        total_p += int(max(0, _as_int(load.get("P", 0), 0)))
    edges = sorted((dict(item) for item in list(graph.get("edges") or []) if isinstance(item, Mapping)), key=lambda row: str(row.get("edge_id", "")))
    weights = dict((str(edge.get("edge_id", "")).strip(), int(max(1, _as_int(_as_map(edge.get("payload")).get("capacity_rating", 1), 1)))) for edge in edges)
    p_by_edge = _weighted_integer_split(total=total_p, keys=[str(edge.get("edge_id", "")).strip() for edge in edges], weights=weights)
    edge_status_rows = []
    flow_channels = []
    for edge in edges:
        edge_id = str(edge.get("edge_id", "")).strip()
        payload = normalize_elec_edge_payload(_as_map(edge.get("payload")))
        p = int(max(0, _as_int(p_by_edge.get(edge_id, 0), 0)))
        loss = int((p * 50) // 1000)
        p_del = int(max(0, p - loss))
        channel = build_power_flow_channel(
            graph_id=graph_id,
            edge_id=edge_id,
            source_node_id=str(edge.get("from_node_id", "")).strip(),
            sink_node_id=str(edge.get("to_node_id", "")).strip(),
            capacity_rating=int(max(0, _as_int(payload.get("capacity_rating", 0), 0))),
        )
        flow_channels.append(channel)
        edge_status_rows.append(
            {
                "edge_id": edge_id,
                "channel_id": str(channel.get("channel_id", "")).strip(),
                "tier": "E0",
                "P": int(p_del),
                "Q": 0,
                "S": int(p_del),
                "pf_permille": 1000,
                "heat_loss_stub": int(loss),
            }
        )
    return {
        "mode": "E0",
        "graph_id": graph_id,
        "flow_channels": sorted(flow_channels, key=lambda row: str(row.get("channel_id", ""))),
        "edge_status_rows": sorted(edge_status_rows, key=lambda row: str(row.get("edge_id", ""))),
        "node_status_rows": [],
        "overloaded_channel_ids": [],
        "budget_outcome": "degraded",
        "downgrade_reason": str(reason or "degrade.elec.e1_disabled"),
        "power_flow_hash": canonical_sha256(
            [{"edge_id": str(row.get("edge_id", "")), "P": int(_as_int(row.get("P", 0), 0))} for row in edge_status_rows]
        ),
    }


def _spec_numeric(spec_row: Mapping[str, object], keys: List[str]) -> int | None:
    params = _as_map(spec_row.get("parameters"))
    for key in keys:
        value = params.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return int(value)
    return None


def evaluate_connection_spec_compatibility(
    *,
    connector_spec_row: Mapping[str, object] | None,
    edge_spec_row: Mapping[str, object] | None,
) -> dict:
    connector = dict(connector_spec_row or {})
    edge = dict(edge_spec_row or {})
    reasons: List[str] = []
    connector_type = str(_as_map(connector.get("parameters")).get("connector_type", "")).strip()
    edge_type = str(_as_map(edge.get("parameters")).get("connector_type", "")).strip()
    if connector_type and edge_type and connector_type != edge_type:
        reasons.append("connector_type_mismatch")
    v_conn = _spec_numeric(connector, ["voltage_rating", "voltage_rating_v", "voltage"])
    v_edge = _spec_numeric(edge, ["voltage_rating", "voltage_rating_v", "voltage"])
    if v_conn is not None and v_edge is not None and v_conn != v_edge:
        reasons.append("voltage_mismatch")
    i_conn = _spec_numeric(connector, ["current_rating", "current_rating_a", "current"])
    i_edge = _spec_numeric(edge, ["current_rating", "current_rating_a", "current"])
    if i_conn is not None and i_edge is not None and i_conn > i_edge:
        reasons.append("current_over_edge_rating")
    return {
        "compatible": len(reasons) == 0,
        "reasons": sorted(reasons),
    }


__all__ = [
    "ElectricError",
    "REFUSAL_ELEC_NETWORK_INVALID",
    "REFUSAL_ELEC_SPEC_NONCOMPLIANT",
    "build_power_flow_channel",
    "compute_pf_permille",
    "deterministic_power_channel_id",
    "evaluate_connection_spec_compatibility",
    "normalize_elec_edge_payload",
    "normalize_elec_node_payload",
    "solve_power_network_e0",
    "solve_power_network_e1",
]
