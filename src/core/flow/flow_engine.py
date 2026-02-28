"""Deterministic core FlowSystem helpers."""

from __future__ import annotations

from typing import Mapping


REFUSAL_CORE_FLOW_INVALID = "refusal.core.flow.invalid"


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
        normalized_delay = None
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
        normalized_loss_fraction = None
    else:
        normalized_loss_fraction = int(_as_int(loss_fraction, 0))
        if normalized_loss_fraction < 0:
            raise FlowEngineError(
                REFUSAL_CORE_FLOW_INVALID,
                "flow channel loss_fraction must be >= 0",
                {"channel_id": channel_id, "loss_fraction": int(normalized_loss_fraction)},
            )
    return {
        "schema_version": "1.0.0",
        "channel_id": channel_id,
        "graph_id": graph_id,
        "quantity_id": quantity_id,
        "source_node_id": source_node_id,
        "sink_node_id": sink_node_id,
        "capacity_per_tick": normalized_capacity,
        "delay_ticks": normalized_delay,
        "loss_fraction": normalized_loss_fraction,
        "solver_policy_id": solver_policy_id,
        "extensions": dict(payload.get("extensions") or {}),
    }


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

