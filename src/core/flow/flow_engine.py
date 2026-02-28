"""Deterministic core FlowSystem helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.core.graph.network_graph_engine import normalize_network_graph
from src.core.graph.routing_engine import build_cross_shard_route_plan, normalize_graph_partition_row


REFUSAL_CORE_FLOW_INVALID = "refusal.core.flow.invalid"
REFUSAL_CORE_FLOW_SOLVER_POLICY_INVALID = "refusal.core.flow.solver_policy_invalid"
REFUSAL_CORE_FLOW_CAPACITY_INSUFFICIENT = "refusal.core.flow.capacity_insufficient"
REFUSAL_CORE_FLOW_OVERFLOW_REFUSED = "refusal.core.flow.overflow_refused"


class FlowEngineError(ValueError):
    """Deterministic FlowSystem refusal."""

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
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_INVALID,
            "division by zero in FlowSystem fixed-point calculation",
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


def _canonicalize_value(value: object) -> object:
    if isinstance(value, dict):
        out: Dict[str, object] = {}
        for key in sorted(value.keys(), key=lambda item: str(item)):
            out[str(key)] = _canonicalize_value(value[key])
        return out
    if isinstance(value, list):
        return [_canonicalize_value(item) for item in list(value)]
    return value


def normalize_flow_solver_policy(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    solver_policy_id = str(payload.get("solver_policy_id", "")).strip()
    mode = str(payload.get("mode", "")).strip()
    allow_partial_transfer = payload.get("allow_partial_transfer")
    overflow_policy = str(payload.get("overflow_policy", "")).strip()
    if not solver_policy_id or mode not in {"bulk", "segmented"} or not isinstance(allow_partial_transfer, bool):
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_SOLVER_POLICY_INVALID,
            "flow solver policy missing required deterministic fields",
            {
                "solver_policy_id": solver_policy_id,
                "mode": mode,
                "allow_partial_transfer": str(allow_partial_transfer),
            },
        )
    if overflow_policy not in {"refuse", "queue", "spill"}:
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_SOLVER_POLICY_INVALID,
            "flow solver policy overflow_policy must be refuse|queue|spill",
            {"solver_policy_id": solver_policy_id, "overflow_policy": overflow_policy},
        )
    return {
        "schema_version": "1.0.0",
        "solver_policy_id": solver_policy_id,
        "mode": mode,
        "allow_partial_transfer": bool(allow_partial_transfer),
        "overflow_policy": overflow_policy,
        "extensions": dict(_canonicalize_value(dict(payload.get("extensions") or {}))),
    }


def flow_solver_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    root = dict(registry_payload or {})
    rows = root.get("solver_policies")
    if not isinstance(rows, list):
        rows = ((root.get("record") or {}).get("solver_policies") or [])
    out: Dict[str, dict] = {}
    for row in sorted((item for item in list(rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("solver_policy_id", ""))):
        normalized = normalize_flow_solver_policy(row)
        out[str(normalized.get("solver_policy_id", ""))] = normalized
    return out


def normalize_flow_channel(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    channel_id = str(payload.get("channel_id", "")).strip()
    graph_id = str(payload.get("graph_id", "")).strip()
    quantity_id = str(payload.get("quantity_id", "")).strip()
    source_node_id = str(payload.get("source_node_id", "")).strip()
    sink_node_id = str(payload.get("sink_node_id", "")).strip()
    solver_policy_id = str(payload.get("solver_policy_id", "")).strip()
    if not channel_id or not graph_id or not quantity_id or not source_node_id or not sink_node_id or not solver_policy_id:
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_INVALID,
            "flow channel missing required identifiers",
            {
                "channel_id": channel_id,
                "graph_id": graph_id,
                "quantity_id": quantity_id,
                "source_node_id": source_node_id,
                "sink_node_id": sink_node_id,
                "solver_policy_id": solver_policy_id,
            },
        )
    capacity_per_tick = payload.get("capacity_per_tick")
    if capacity_per_tick is None:
        normalized_capacity = None
    else:
        normalized_capacity = int(_as_int(capacity_per_tick, 0))
        if normalized_capacity < 0:
            raise FlowEngineError(
                REFUSAL_CORE_FLOW_INVALID,
                "flow channel capacity_per_tick must be >= 0",
                {"channel_id": channel_id, "capacity_per_tick": int(normalized_capacity)},
            )
    delay_ticks = payload.get("delay_ticks")
    if delay_ticks is None:
        normalized_delay = 0
    else:
        normalized_delay = int(_as_int(delay_ticks, 0))
        if normalized_delay < 0:
            raise FlowEngineError(
                REFUSAL_CORE_FLOW_INVALID,
                "flow channel delay_ticks must be >= 0",
                {"channel_id": channel_id, "delay_ticks": int(normalized_delay)},
            )
    loss_fraction = payload.get("loss_fraction")
    if loss_fraction is None:
        normalized_loss_fraction = 0
    else:
        normalized_loss_fraction = int(_as_int(loss_fraction, 0))
        if normalized_loss_fraction < 0:
            raise FlowEngineError(
                REFUSAL_CORE_FLOW_INVALID,
                "flow channel loss_fraction must be >= 0",
                {"channel_id": channel_id, "loss_fraction": int(normalized_loss_fraction)},
            )
    priority = int(_as_int(payload.get("priority", 0), 0))
    if priority < 0:
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_INVALID,
            "flow channel priority must be >= 0",
            {"channel_id": channel_id, "priority": int(priority)},
        )
    return {
        "schema_version": "1.0.0",
        "channel_id": channel_id,
        "graph_id": graph_id,
        "quantity_id": quantity_id,
        "source_node_id": source_node_id,
        "sink_node_id": sink_node_id,
        "capacity_per_tick": normalized_capacity,
        "delay_ticks": int(normalized_delay),
        "loss_fraction": int(normalized_loss_fraction),
        "solver_policy_id": solver_policy_id,
        "priority": int(priority),
        "extensions": dict(_canonicalize_value(dict(payload.get("extensions") or {}))),
    }


def normalize_flow_transfer_event(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    event_id = str(payload.get("event_id", "")).strip()
    channel_id = str(payload.get("channel_id", "")).strip()
    if not event_id or not channel_id:
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_INVALID,
            "flow transfer event requires event_id and channel_id",
            {"event_id": event_id, "channel_id": channel_id},
        )
    tick = max(0, _as_int(payload.get("tick", 0), 0))
    transferred_amount = max(0, _as_int(payload.get("transferred_amount", 0), 0))
    lost_amount = max(0, _as_int(payload.get("lost_amount", 0), 0))
    ledger_delta_refs = _sorted_unique_strings(payload.get("ledger_delta_refs"))
    row_out = {
        "schema_version": "1.0.0",
        "event_id": event_id,
        "tick": int(tick),
        "channel_id": channel_id,
        "transferred_amount": int(transferred_amount),
        "lost_amount": int(lost_amount),
        "ledger_delta_refs": list(ledger_delta_refs),
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": dict(_canonicalize_value(dict(payload.get("extensions") or {}))),
    }
    if not row_out["deterministic_fingerprint"]:
        row_out["deterministic_fingerprint"] = canonical_sha256(dict(row_out, deterministic_fingerprint=""))
    return row_out


def _ledger_delta_refs(channel_id: str, tick: int, source_debit: int, sink_credit: int, lost_amount: int) -> List[str]:
    refs = []
    if int(source_debit) > 0:
        refs.append(
            "ledger.delta.debit.{}".format(
                canonical_sha256({"channel_id": channel_id, "tick": int(tick), "kind": "debit"})[:24]
            )
        )
    if int(sink_credit) > 0:
        refs.append(
            "ledger.delta.credit.{}".format(
                canonical_sha256({"channel_id": channel_id, "tick": int(tick), "kind": "credit"})[:24]
            )
        )
    if int(lost_amount) > 0:
        refs.append(
            "ledger.delta.loss.{}".format(
                canonical_sha256({"channel_id": channel_id, "tick": int(tick), "kind": "loss"})[:24]
            )
        )
    return sorted(refs)


def flow_transfer(
    *,
    quantity: int,
    loss_fraction: int,
    scale: int,
    capacity_per_tick: int | None = None,
    delay_ticks: int = 0,
) -> dict:
    quantity_mass = int(max(0, _as_int(quantity, 0)))
    normalized_capacity = None if capacity_per_tick is None else int(max(0, _as_int(capacity_per_tick, 0)))
    processed_mass = quantity_mass if normalized_capacity is None else int(min(quantity_mass, normalized_capacity))
    normalized_loss_fraction = int(max(0, _as_int(loss_fraction, 0)))
    if normalized_loss_fraction > int(scale):
        normalized_loss_fraction = int(scale)
    if processed_mass <= 0 or normalized_loss_fraction <= 0:
        loss_mass = 0
    else:
        loss_mass = int(max(0, _round_div_away_from_zero(int(processed_mass) * int(normalized_loss_fraction), int(scale))))
    delivered_mass = int(max(0, int(processed_mass) - int(loss_mass)))
    deferred_mass = int(max(0, int(quantity_mass) - int(processed_mass)))
    return {
        "processed_mass": int(processed_mass),
        "delivered_mass": int(delivered_mass),
        "loss_mass": int(loss_mass),
        "deferred_mass": int(deferred_mass),
        "delay_ticks": int(max(0, _as_int(delay_ticks, 0))),
    }


def _solver_policy_for_channel(*, channel_row: Mapping[str, object], solver_policies: Mapping[str, object] | None) -> dict:
    rows = dict(solver_policies or {})
    solver_policy_id = str(channel_row.get("solver_policy_id", "")).strip()
    row = dict(rows.get(solver_policy_id) or {})
    if not row:
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_SOLVER_POLICY_INVALID,
            "flow channel references unknown solver policy",
            {"channel_id": str(channel_row.get("channel_id", "")), "solver_policy_id": solver_policy_id},
        )
    return normalize_flow_solver_policy(row)


def _normalize_balances(value: Mapping[str, object] | None) -> Dict[str, int]:
    rows = dict(value or {})
    out: Dict[str, int] = {}
    for key in sorted(rows.keys(), key=lambda item: str(item)):
        node_id = str(key).strip()
        if not node_id:
            continue
        out[node_id] = max(0, _as_int(rows.get(key, 0), 0))
    return out


def _normalize_sink_caps(value: Mapping[str, object] | None) -> Dict[str, int]:
    rows = dict(value or {})
    out: Dict[str, int] = {}
    for key in sorted(rows.keys(), key=lambda item: str(item)):
        node_id = str(key).strip()
        if not node_id:
            continue
        out[node_id] = max(0, _as_int(rows.get(key, 0), 0))
    return out


def _normalize_channel_runtime(value: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = dict(value or {})
    out: Dict[str, dict] = {}
    for key in sorted(rows.keys(), key=lambda item: str(item)):
        channel_id = str(key).strip()
        if not channel_id:
            continue
        row = dict(rows.get(key) or {})
        queued_amount = max(0, _as_int(row.get("queued_amount", 0), 0))
        in_transit = []
        for item in sorted((entry for entry in list(row.get("in_transit") or []) if isinstance(entry, dict)), key=lambda entry: (_as_int(entry.get("ready_tick", 0), 0), _as_int(entry.get("amount", 0), 0))):
            amount = max(0, _as_int(item.get("amount", 0), 0))
            ready_tick = max(0, _as_int(item.get("ready_tick", 0), 0))
            if amount <= 0:
                continue
            in_transit.append({"ready_tick": int(ready_tick), "amount": int(amount)})
        out[channel_id] = {
            "queued_amount": int(queued_amount),
            "in_transit": list(in_transit),
        }
    return out


def _route_node_ids_from_edges(graph_row: Mapping[str, object], source_node_id: str, edge_ids: List[str]) -> List[str]:
    graph = normalize_network_graph(graph_row)
    edge_index: Dict[str, dict] = {}
    for edge in list(graph.get("edges") or []):
        row = dict(edge or {})
        edge_id = str(row.get("edge_id", "")).strip()
        if edge_id:
            edge_index[edge_id] = row
    current = str(source_node_id).strip()
    node_ids = [current] if current else []
    for edge_id in list(edge_ids or []):
        row = dict(edge_index.get(str(edge_id).strip()) or {})
        if not row:
            return []
        from_node_id = str(row.get("from_node_id", "")).strip()
        to_node_id = str(row.get("to_node_id", "")).strip()
        if current and from_node_id != current:
            return []
        current = to_node_id
        if current:
            node_ids.append(current)
    return node_ids


def _cross_shard_flow_plan(*, channel_row: Mapping[str, object], graph_row: Mapping[str, object] | None, partition_row: Mapping[str, object] | None) -> dict:
    if not graph_row or not partition_row:
        return {
            "partitioned": False,
            "deterministic_fingerprint": canonical_sha256({"partitioned": False, "channel_id": str(channel_row.get("channel_id", ""))}),
            "segments": [],
            "cross_shard_boundaries": [],
        }
    graph = normalize_network_graph(graph_row)
    partition = normalize_graph_partition_row(partition_row, graph_row=graph)
    ext = dict(channel_row.get("extensions") or {})
    route_edge_ids = _sorted_unique_strings(ext.get("route_edge_ids"))
    route_node_ids = _sorted_unique_strings(ext.get("route_node_ids"))
    if not route_edge_ids:
        return {
            "partitioned": False,
            "deterministic_fingerprint": canonical_sha256({"partitioned": False, "channel_id": str(channel_row.get("channel_id", ""))}),
            "segments": [],
            "cross_shard_boundaries": [],
        }
    if not route_node_ids:
        route_node_ids = _route_node_ids_from_edges(graph, str(channel_row.get("source_node_id", "")), route_edge_ids)
    return build_cross_shard_route_plan(
        graph_row=graph,
        partition_row=partition,
        path_node_ids=list(route_node_ids),
        path_edge_ids=list(route_edge_ids),
    )


def tick_flow_channels(
    *,
    channels: object,
    node_balances: Mapping[str, object] | None,
    current_tick: int,
    fixed_point_scale: int,
    solver_policies: Mapping[str, object] | None,
    conserved_quantity_ids: object = None,
    max_channels: int | None = None,
    strict_budget: bool = False,
    sink_capacities: Mapping[str, object] | None = None,
    channel_runtime: Mapping[str, object] | None = None,
    graph_row: Mapping[str, object] | None = None,
    partition_row: Mapping[str, object] | None = None,
    cost_units_per_channel: int = 1,
) -> dict:
    if not isinstance(channels, list):
        channels = []
    normalized_channels = sorted(
        (normalize_flow_channel(dict(row)) for row in list(channels or []) if isinstance(row, dict)),
        key=lambda row: (str(row.get("channel_id", "")), int(_as_int(row.get("priority", 0), 0))),
    )
    balances = _normalize_balances(node_balances)
    sink_caps = _normalize_sink_caps(sink_capacities)
    runtime_by_channel = _normalize_channel_runtime(channel_runtime)
    conserved_ids = set(_sorted_unique_strings(list(conserved_quantity_ids or [])))
    policy_rows = dict(solver_policies or {})

    scale = max(1, _as_int(fixed_point_scale, 1))
    tick = max(0, _as_int(current_tick, 0))
    limit = len(normalized_channels) if max_channels is None else max(0, _as_int(max_channels, 0))

    transfer_events: List[dict] = []
    loss_entries: List[dict] = []
    channel_results: List[dict] = []
    cross_shard_transfer_plans: List[dict] = []
    processed_count = 0
    remaining_count = 0

    for channel_row in normalized_channels:
        channel_id = str(channel_row.get("channel_id", ""))
        if processed_count >= int(limit):
            remaining_count += 1
            continue
        policy_row = _solver_policy_for_channel(channel_row=channel_row, solver_policies=policy_rows)
        overflow_policy = str(policy_row.get("overflow_policy", "queue"))
        allow_partial = bool(policy_row.get("allow_partial_transfer", True))

        source_node_id = str(channel_row.get("source_node_id", ""))
        sink_node_id = str(channel_row.get("sink_node_id", ""))
        source_available = max(0, _as_int(balances.get(source_node_id, 0), 0))
        sink_current = max(0, _as_int(balances.get(sink_node_id, 0), 0))
        runtime_row = dict(runtime_by_channel.get(channel_id) or {"queued_amount": 0, "in_transit": []})
        queued_amount = max(0, _as_int(runtime_row.get("queued_amount", 0), 0))
        in_transit_rows = [
            dict(item)
            for item in sorted(
                (entry for entry in list(runtime_row.get("in_transit") or []) if isinstance(entry, dict)),
                key=lambda entry: (_as_int(entry.get("ready_tick", 0), 0), _as_int(entry.get("amount", 0), 0)),
            )
        ]

        releasable_amount = 0
        future_in_transit: List[dict] = []
        for row in in_transit_rows:
            amount = max(0, _as_int(row.get("amount", 0), 0))
            ready_tick = max(0, _as_int(row.get("ready_tick", 0), 0))
            if amount <= 0:
                continue
            if ready_tick <= int(tick):
                releasable_amount += int(amount)
            else:
                future_in_transit.append({"ready_tick": int(ready_tick), "amount": int(amount)})

        requested_outbound = int(source_available + queued_amount)
        channel_capacity = channel_row.get("capacity_per_tick")
        if channel_capacity is None:
            capacity_processed = requested_outbound
        else:
            capacity_processed = min(requested_outbound, max(0, _as_int(channel_capacity, 0)))
        overflow_from_capacity = int(max(0, requested_outbound - capacity_processed))
        if overflow_from_capacity > 0 and (not allow_partial) and overflow_policy == "refuse":
            raise FlowEngineError(
                REFUSAL_CORE_FLOW_CAPACITY_INSUFFICIENT,
                "flow channel exceeds capacity and policy refuses partial transfer",
                {
                    "channel_id": channel_id,
                    "requested": int(requested_outbound),
                    "capacity_per_tick": int(_as_int(channel_capacity, 0)),
                },
            )

        consumed_from_queue = min(int(queued_amount), int(capacity_processed))
        consumed_from_source = int(max(0, int(capacity_processed) - int(consumed_from_queue)))
        queued_after = int(max(0, int(queued_amount) - int(consumed_from_queue)))

        spill_loss = 0
        if overflow_from_capacity > 0:
            if overflow_policy == "refuse":
                raise FlowEngineError(
                    REFUSAL_CORE_FLOW_OVERFLOW_REFUSED,
                    "flow channel overflow policy refused capacity overflow",
                    {"channel_id": channel_id, "overflow_amount": int(overflow_from_capacity)},
                )
            if overflow_policy == "queue":
                queued_after += int(overflow_from_capacity)
            elif overflow_policy == "spill":
                spill_loss += int(overflow_from_capacity)

        launched_amount = int(capacity_processed)
        if consumed_from_source > 0:
            balances[source_node_id] = int(max(0, int(source_available) - int(consumed_from_source)))

        delay_ticks = int(max(0, _as_int(channel_row.get("delay_ticks", 0), 0)))
        immediate_arrival = 0
        if launched_amount > 0:
            if delay_ticks > 0:
                future_in_transit.append({"ready_tick": int(tick + delay_ticks), "amount": int(launched_amount)})
            else:
                immediate_arrival = int(launched_amount)

        arriving_amount = int(max(0, int(releasable_amount) + int(immediate_arrival)))
        sink_capacity = sink_caps.get(sink_node_id)
        overflow_at_sink = 0
        if sink_capacity is not None:
            sink_room = max(0, int(_as_int(sink_capacity, 0)) - int(sink_current))
            if arriving_amount > sink_room:
                overflow_at_sink = int(arriving_amount - sink_room)
                arriving_amount = int(sink_room)
        if overflow_at_sink > 0:
            if overflow_policy == "refuse":
                raise FlowEngineError(
                    REFUSAL_CORE_FLOW_OVERFLOW_REFUSED,
                    "flow channel overflow policy refused sink overflow",
                    {"channel_id": channel_id, "overflow_amount": int(overflow_at_sink)},
                )
            if overflow_policy == "queue":
                future_in_transit.append({"ready_tick": int(tick + 1), "amount": int(overflow_at_sink)})
            elif overflow_policy == "spill":
                spill_loss += int(overflow_at_sink)

        transfer_result = flow_transfer(
            quantity=int(arriving_amount),
            loss_fraction=int(channel_row.get("loss_fraction", 0)),
            scale=int(scale),
            capacity_per_tick=None,
            delay_ticks=0,
        )
        net_transfer = int(max(0, _as_int(transfer_result.get("delivered_mass", 0), 0)))
        loss_fraction_loss = int(max(0, _as_int(transfer_result.get("loss_mass", 0), 0)))
        total_lost = int(max(0, int(loss_fraction_loss) + int(spill_loss)))
        if net_transfer > 0:
            balances[sink_node_id] = int(max(0, int(sink_current) + int(net_transfer)))

        runtime_by_channel[channel_id] = {
            "queued_amount": int(max(0, int(queued_after))),
            "in_transit": sorted(
                (
                    {
                        "ready_tick": int(max(0, _as_int(item.get("ready_tick", 0), 0))),
                        "amount": int(max(0, _as_int(item.get("amount", 0), 0))),
                    }
                    for item in future_in_transit
                    if max(0, _as_int(item.get("amount", 0), 0)) > 0
                ),
                key=lambda item: (int(item.get("ready_tick", 0)), int(item.get("amount", 0))),
            ),
        }

        ledger_refs = _ledger_delta_refs(
            channel_id=channel_id,
            tick=int(tick),
            source_debit=int(consumed_from_source),
            sink_credit=int(net_transfer),
            lost_amount=int(total_lost),
        )
        event_row = normalize_flow_transfer_event(
            {
                "schema_version": "1.0.0",
                "event_id": "flow.event.{}".format(
                    canonical_sha256({"channel_id": channel_id, "tick": int(tick), "sequence": int(processed_count)})[:24]
                ),
                "tick": int(tick),
                "channel_id": channel_id,
                "transferred_amount": int(net_transfer),
                "lost_amount": int(total_lost),
                "ledger_delta_refs": list(ledger_refs),
                "deterministic_fingerprint": "",
                "extensions": {
                    "quantity_id": str(channel_row.get("quantity_id", "")),
                    "source_node_id": source_node_id,
                    "sink_node_id": sink_node_id,
                    "launched_amount": int(launched_amount),
                    "releasable_amount": int(releasable_amount),
                    "spill_loss": int(spill_loss),
                    "policy_id": str(policy_row.get("solver_policy_id", "")),
                },
            }
        )
        transfer_events.append(event_row)

        if int(total_lost) > 0:
            loss_row = {
                "channel_id": channel_id,
                "quantity_id": str(channel_row.get("quantity_id", "")),
                "source_node_id": source_node_id,
                "sink_node_id": sink_node_id,
                "lost_amount": int(total_lost),
                "conserved": bool(str(channel_row.get("quantity_id", "")) in conserved_ids),
            }
            loss_entries.append(loss_row)

        deferred_amount = int(
            max(0, int(runtime_by_channel[channel_id]["queued_amount"]))
            + sum(int(_as_int(item.get("amount", 0), 0)) for item in list(runtime_by_channel[channel_id]["in_transit"]))
        )
        channel_results.append(
            {
                "channel_id": channel_id,
                "quantity_id": str(channel_row.get("quantity_id", "")),
                "source_node_id": source_node_id,
                "sink_node_id": sink_node_id,
                "launched_amount": int(launched_amount),
                "transferred_amount": int(net_transfer),
                "lost_amount": int(total_lost),
                "deferred_amount": int(max(0, deferred_amount)),
            }
        )

        plan_row = _cross_shard_flow_plan(
            channel_row=channel_row,
            graph_row=graph_row,
            partition_row=partition_row,
        )
        cross_shard_transfer_plans.append(
            {
                "channel_id": channel_id,
                "tick": int(tick),
                "plan": dict(plan_row),
            }
        )
        processed_count += 1

    if strict_budget and remaining_count > 0:
        raise FlowEngineError(
            REFUSAL_CORE_FLOW_CAPACITY_INSUFFICIENT,
            "flow tick exceeded deterministic channel budget",
            {"processed_count": int(processed_count), "remaining_count": int(remaining_count)},
        )

    return {
        "node_balances": dict((str(key), int(balances[key])) for key in sorted(balances.keys())),
        "channel_runtime": dict(
            (str(key), dict(runtime_by_channel[key]))
            for key in sorted(runtime_by_channel.keys())
            if str(key).strip()
        ),
        "transfer_events": sorted(
            (dict(row) for row in transfer_events if isinstance(row, dict)),
            key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))),
        ),
        "loss_entries": sorted(
            (dict(row) for row in loss_entries if isinstance(row, dict)),
            key=lambda row: (str(row.get("channel_id", "")), str(row.get("quantity_id", ""))),
        ),
        "channel_results": sorted(
            (dict(row) for row in channel_results if isinstance(row, dict)),
            key=lambda row: str(row.get("channel_id", "")),
        ),
        "cross_shard_transfer_plans": sorted(
            (dict(row) for row in cross_shard_transfer_plans if isinstance(row, dict)),
            key=lambda row: str(row.get("channel_id", "")),
        ),
        "processed_count": int(processed_count),
        "remaining_count": int(remaining_count),
        "cost_units": int(max(0, _as_int(cost_units_per_channel, 1)) * int(processed_count)),
        "budget_outcome": "degraded" if int(remaining_count) > 0 else "complete",
    }
