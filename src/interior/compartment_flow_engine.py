"""Deterministic INT-2 compartment flow engine over InteriorVolumeGraph + FlowSystem."""

from __future__ import annotations

from typing import Dict, List, Mapping

from src.core.flow.flow_engine import FlowEngineError, flow_solver_policy_rows_by_id, tick_flow_channels
from src.core.hazards.hazard_engine import tick_hazard_models
from src.interior.compartment_flow_builder import (
    CompartmentFlowBuilderError,
    build_compartment_flow_channels,
    compartment_flow_policy_rows_by_id,
    compartment_state_rows_by_volume_id,
    leak_hazard_rows_by_id,
)
from src.interior.interior_engine import normalize_interior_volume, volume_rows_by_id
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_COMPARTMENT_FLOW_INVALID = "refusal.interior.flow.invalid"
REFUSAL_COMPARTMENT_FLOW_BUDGET_EXCEEDED = "refusal.interior.flow.budget_exceeded"


class CompartmentFlowEngineError(ValueError):
    """Deterministic compartment flow refusal."""

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


def _safe_extensions(payload: Mapping[str, object]) -> dict:
    ext = payload.get("extensions")
    return dict(ext or {}) if isinstance(ext, dict) else {}


def _volume_capacity_mm3(volume_row: Mapping[str, object]) -> int:
    volume = normalize_interior_volume(volume_row)
    shape = dict(volume.get("bounding_shape") or {})
    shape_type = str(shape.get("shape_type", "")).strip()
    shape_data = dict(shape.get("shape_data") or {})
    if shape_type == "aabb":
        half_extents = dict(shape_data.get("half_extents_mm") or {})
        hx = max(1, _as_int(half_extents.get("x", 0), 0))
        hy = max(1, _as_int(half_extents.get("y", 0), 0))
        hz = max(1, _as_int(half_extents.get("z", 0), 0))
        return int(max(1, 8 * hx * hy * hz))
    approx_mm3 = max(0, _as_int(shape_data.get("approx_volume_mm3", 0), 0))
    if approx_mm3 > 0:
        return int(approx_mm3)
    return 1


def _volume_capacity_liters(volume_row: Mapping[str, object]) -> int:
    return int(max(1, _volume_capacity_mm3(volume_row) // 1_000_000))


def _pressure_from_air_mass(*, air_mass: int, volume_liters: int, fixed_point_scale: int) -> int:
    liters = int(max(1, _as_int(volume_liters, 1)))
    scale = int(max(1, _as_int(fixed_point_scale, 1000)))
    return int(max(0, (_as_int(air_mass, 0) * scale) // liters))


def _warning_band_low(*, value: int, warn: int, danger: int) -> str:
    token = int(max(0, _as_int(value, 0)))
    warn_token = int(max(0, _as_int(warn, 0)))
    danger_token = int(max(0, _as_int(danger, 0)))
    if token <= danger_token:
        return "DANGER"
    if token <= warn_token:
        return "WARN"
    return "OK"


def _warning_band_high(*, value: int, warn: int, danger: int) -> str:
    token = int(max(0, _as_int(value, 0)))
    warn_token = int(max(0, _as_int(warn, 0)))
    danger_token = int(max(0, _as_int(danger, 0)))
    if token >= danger_token:
        return "DANGER"
    if token >= warn_token:
        return "WARN"
    return "OK"


def normalize_compartment_flow_policy_row(row: Mapping[str, object] | None) -> dict:
    payload = dict(row or {})
    return {
        "schema_version": "1.0.0",
        "policy_id": str(payload.get("policy_id", "flow.policy.default")).strip() or "flow.policy.default",
        "description": str(payload.get("description", "")).strip(),
        "flow_solver_policy_id": str(payload.get("flow_solver_policy_id", "flow.coarse_default")).strip()
        or "flow.coarse_default",
        "update_interval_ticks": max(0, _as_int(payload.get("update_interval_ticks", 1), 1)),
        "max_substep_ticks": max(1, _as_int(payload.get("max_substep_ticks", 16), 16)),
        "strict_budget": bool(payload.get("strict_budget", False)),
        "max_channels_per_tick": max(0, _as_int(payload.get("max_channels_per_tick", 1024), 1024)),
        "max_hazards_per_tick": max(0, _as_int(payload.get("max_hazards_per_tick", 1024), 1024)),
        "pressure_warn_threshold": max(0, _as_int(payload.get("pressure_warn_threshold", 200), 200)),
        "pressure_danger_threshold": max(0, _as_int(payload.get("pressure_danger_threshold", 100), 100)),
        "oxygen_warn_fraction": max(0, _as_int(payload.get("oxygen_warn_fraction", 190), 190)),
        "oxygen_danger_fraction": max(0, _as_int(payload.get("oxygen_danger_fraction", 150), 150)),
        "smoke_warn_density": max(0, _as_int(payload.get("smoke_warn_density", 200), 200)),
        "smoke_danger_density": max(0, _as_int(payload.get("smoke_danger_density", 450), 450)),
        "flood_warn_volume": max(0, _as_int(payload.get("flood_warn_volume", 250), 250)),
        "flood_danger_volume": max(0, _as_int(payload.get("flood_danger_volume", 700), 700)),
        "movement_slow_flood_volume": max(0, _as_int(payload.get("movement_slow_flood_volume", 350), 350)),
        "movement_block_flood_volume": max(0, _as_int(payload.get("movement_block_flood_volume", 850), 850)),
        "extensions": _safe_extensions(payload),
    }


def resolve_compartment_flow_policy_row(
    *,
    policy_id: str,
    policy_registry_payload: Mapping[str, object] | None,
) -> dict:
    rows_by_id = compartment_flow_policy_rows_by_id(policy_registry_payload)
    token = str(policy_id).strip()
    row = dict(rows_by_id.get(token) or rows_by_id.get("flow.policy.default") or {})
    return normalize_compartment_flow_policy_row(row)


def _channel_rows_by_medium(flow_build: Mapping[str, object]) -> Dict[str, List[dict]]:
    rows = [dict(item) for item in list((dict(flow_build or {})).get("channels") or []) if isinstance(item, dict)]
    out: Dict[str, List[dict]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("channel_id", ""))):
        ext = dict(row.get("extensions") or {})
        medium_id = str(ext.get("medium_id", "")).strip() or "air"
        out.setdefault(medium_id, []).append(dict(row))
    return dict((key, sorted(out[key], key=lambda item: str(item.get("channel_id", "")))) for key in sorted(out.keys()))


def _default_outside_reservoir(*, include_smoke: bool) -> dict:
    payload = {
        "air": 0,
        "water": 0,
    }
    if include_smoke:
        payload["smoke"] = 0
    return payload


def _substeps_for_dt(*, dt_ticks: int, max_substep_ticks: int) -> List[int]:
    requested = int(max(1, _as_int(dt_ticks, 1)))
    max_step = int(max(1, _as_int(max_substep_ticks, 16)))
    remaining = int(requested)
    out: List[int] = []
    while remaining > 0:
        step = min(max_step, remaining)
        out.append(int(step))
        remaining -= int(step)
    return out


def _flow_balance_for_medium(
    *,
    medium_id: str,
    states_by_volume_id: Mapping[str, dict],
    volume_ids: List[str],
    outside_node_id: str,
    outside_reservoir: Mapping[str, object],
) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for volume_id in sorted(_sorted_unique_strings(volume_ids)):
        state_row = dict(states_by_volume_id.get(volume_id) or {})
        if medium_id == "air":
            value = max(0, _as_int(state_row.get("air_mass", 0), 0))
        elif medium_id == "water":
            value = max(0, _as_int(state_row.get("water_volume", 0), 0))
        elif medium_id == "smoke":
            value = max(0, _as_int(state_row.get("smoke_density", 0), 0))
        else:
            value = 0
        out[volume_id] = int(value)
    outside_value = max(0, _as_int((dict(outside_reservoir or {})).get(medium_id, 0), 0))
    if outside_node_id:
        out[outside_node_id] = int(outside_value)
    return dict((key, int(out[key])) for key in sorted(out.keys()))


def _apply_medium_balance(
    *,
    medium_id: str,
    balances: Mapping[str, object],
    states_by_volume_id: Dict[str, dict],
    volume_ids: List[str],
    outside_node_id: str,
    outside_reservoir: Dict[str, int],
) -> None:
    balance_rows = dict(balances or {})
    for volume_id in sorted(_sorted_unique_strings(volume_ids)):
        state_row = dict(states_by_volume_id.get(volume_id) or {})
        value = max(0, _as_int(balance_rows.get(volume_id, 0), 0))
        if medium_id == "air":
            state_row["air_mass"] = int(value)
        elif medium_id == "water":
            state_row["water_volume"] = int(value)
        elif medium_id == "smoke":
            state_row["smoke_density"] = int(value)
        states_by_volume_id[volume_id] = state_row
    if outside_node_id:
        outside_reservoir[medium_id] = int(max(0, _as_int(balance_rows.get(outside_node_id, 0), 0)))


def _gradient_limited_channels(
    *,
    medium_balances: Mapping[str, object],
    channel_rows: List[dict],
) -> List[dict]:
    """Limit directed channel capacity to deterministic high->low net transfer.

    Without this pass, symmetric bidirectional channels can immediately cancel
    each other within a single tick due to deterministic channel ordering.
    """
    balances = dict(medium_balances or {})
    out: List[dict] = []
    for row in sorted((dict(item) for item in list(channel_rows or []) if isinstance(item, dict)), key=lambda item: str(item.get("channel_id", ""))):
        source_node_id = str(row.get("source_node_id", "")).strip()
        sink_node_id = str(row.get("sink_node_id", "")).strip()
        source_amount = max(0, _as_int(balances.get(source_node_id, 0), 0))
        sink_amount = max(0, _as_int(balances.get(sink_node_id, 0), 0))
        base_capacity = row.get("capacity_per_tick")
        if base_capacity is None:
            base_capacity_value = max(0, source_amount)
        else:
            base_capacity_value = max(0, _as_int(base_capacity, 0))
        # Move at most half the local gradient to prevent one-step overshoot.
        gradient_capacity = max(0, (source_amount - sink_amount) // 2)
        effective_capacity = min(base_capacity_value, gradient_capacity)
        updated = dict(row)
        updated["capacity_per_tick"] = int(max(0, effective_capacity))
        out.append(updated)
    return sorted(out, key=lambda item: str(item.get("channel_id", "")))


def _compose_alarm_row(*, volume_id: str, state_row: Mapping[str, object], policy_row: Mapping[str, object]) -> dict:
    pressure = max(0, _as_int(state_row.get("derived_pressure", 0), 0))
    oxygen = max(0, _as_int(state_row.get("oxygen_fraction", 0), 0))
    smoke = max(0, _as_int(state_row.get("smoke_density", 0), 0))
    flood = max(0, _as_int(state_row.get("water_volume", 0), 0))
    pressure_state = _warning_band_low(
        value=pressure,
        warn=_as_int(policy_row.get("pressure_warn_threshold", 0), 0),
        danger=_as_int(policy_row.get("pressure_danger_threshold", 0), 0),
    )
    oxygen_state = _warning_band_low(
        value=oxygen,
        warn=_as_int(policy_row.get("oxygen_warn_fraction", 0), 0),
        danger=_as_int(policy_row.get("oxygen_danger_fraction", 0), 0),
    )
    smoke_state = _warning_band_high(
        value=smoke,
        warn=_as_int(policy_row.get("smoke_warn_density", 0), 0),
        danger=_as_int(policy_row.get("smoke_danger_density", 0), 0),
    )
    flood_state = _warning_band_high(
        value=flood,
        warn=_as_int(policy_row.get("flood_warn_volume", 0), 0),
        danger=_as_int(policy_row.get("flood_danger_volume", 0), 0),
    )
    states = [pressure_state, oxygen_state, smoke_state, flood_state]
    overall = "DANGER" if "DANGER" in states else ("WARN" if "WARN" in states else "OK")
    return {
        "volume_id": str(volume_id),
        "overall": overall,
        "pressure": pressure_state,
        "oxygen": oxygen_state,
        "smoke": smoke_state,
        "flood": flood_state,
    }


def _movement_constraint_rows(*, states_by_volume_id: Mapping[str, dict], policy_row: Mapping[str, object]) -> List[dict]:
    slow_threshold = max(0, _as_int(policy_row.get("movement_slow_flood_volume", 0), 0))
    block_threshold = max(0, _as_int(policy_row.get("movement_block_flood_volume", 0), 0))
    pressure_danger = max(0, _as_int(policy_row.get("pressure_danger_threshold", 0), 0))
    rows: List[dict] = []
    for volume_id in sorted(states_by_volume_id.keys()):
        state_row = dict(states_by_volume_id.get(volume_id) or {})
        water_volume = max(0, _as_int(state_row.get("water_volume", 0), 0))
        pressure = max(0, _as_int(state_row.get("derived_pressure", 0), 0))
        if water_volume >= block_threshold:
            movement_state = "blocked"
        elif water_volume >= slow_threshold:
            movement_state = "slowed"
        else:
            movement_state = "normal"
        rows.append(
            {
                "volume_id": volume_id,
                "movement_state": movement_state,
                "water_volume": int(water_volume),
                "pressure_exposure_low": bool(pressure <= pressure_danger),
            }
        )
    return sorted(rows, key=lambda row: str(row.get("volume_id", "")))


def tick_compartment_flows(
    *,
    interior_graph_row: Mapping[str, object],
    volume_rows: object,
    portal_rows: object,
    portal_state_rows: object | None,
    compartment_state_rows: object,
    portal_flow_param_rows: object | None,
    leak_hazard_rows: object | None,
    leak_hazard_models: object | None,
    portal_flow_template_registry: Mapping[str, object] | None,
    compartment_flow_policy_row: Mapping[str, object] | None,
    flow_solver_policy_registry: Mapping[str, object] | None,
    current_tick: int,
    dt_ticks: int,
    fixed_point_scale: int = 1000,
    numeric_policy: Mapping[str, object] | None = None,
    channel_runtime: Mapping[str, object] | None = None,
    outside_reservoir: Mapping[str, object] | None = None,
    include_smoke: bool = True,
    conserved_quantity_ids: object | None = None,
    graph_partition_row: Mapping[str, object] | None = None,
    cost_units_per_channel: int = 1,
    cost_units_per_hazard: int = 1,
) -> dict:
    """Advance compartment flows deterministically across dt using FlowSystem channels."""

    del numeric_policy

    try:
        volume_index = volume_rows_by_id(volume_rows)
    except Exception as exc:  # pragma: no cover - defensive conversion
        raise CompartmentFlowEngineError(
            REFUSAL_COMPARTMENT_FLOW_INVALID,
            "invalid interior volume rows",
            {"error": str(exc)},
        ) from exc

    states_by_volume_id = compartment_state_rows_by_volume_id(compartment_state_rows)
    for volume_id in sorted(volume_index.keys()):
        if volume_id in states_by_volume_id:
            continue
        states_by_volume_id[volume_id] = {
            "schema_version": "1.0.0",
            "volume_id": volume_id,
            "air_mass": 0,
            "water_volume": 0,
            "temperature": None,
            "oxygen_fraction": 210,
            "smoke_density": 0,
            "derived_pressure": 0,
            "extensions": {},
        }

    leak_rows_by_id = leak_hazard_rows_by_id(leak_hazard_rows)
    hazard_rows = sorted(
        (dict(row) for row in list(leak_hazard_models or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("hazard_id", "")),
    )

    policy_row = normalize_compartment_flow_policy_row(compartment_flow_policy_row)
    solver_policy_rows = flow_solver_policy_rows_by_id(flow_solver_policy_registry)
    if not solver_policy_rows:
        solver_policy_rows = {
            "flow.coarse_default": {
                "schema_version": "1.0.0",
                "solver_policy_id": "flow.coarse_default",
                "mode": "bulk",
                "allow_partial_transfer": True,
                "overflow_policy": "queue",
                "extensions": {},
            }
        }

    runtime_by_channel = dict(
        (str(key), dict(value))
        for key, value in sorted((dict(channel_runtime or {})).items(), key=lambda item: str(item[0]))
        if str(key).strip() and isinstance(value, dict)
    )
    outside_index = dict(_default_outside_reservoir(include_smoke=include_smoke))
    for medium_id, value in sorted((dict(outside_reservoir or {})).items(), key=lambda item: str(item[0])):
        token = str(medium_id).strip()
        if token in outside_index:
            outside_index[token] = max(0, _as_int(value, 0))

    processed_channel_count = 0
    remaining_channel_count = 0
    flow_cost_units = 0
    processed_hazard_count = 0
    deferred_hazard_count = 0
    hazard_cost_units = 0
    budget_outcome = "complete"
    flow_transfer_events: List[dict] = []
    flow_loss_entries: List[dict] = []
    hazard_consequence_events: List[dict] = []
    last_flow_build = {
        "graph_id": "",
        "volume_ids": [],
        "channels": [],
        "medium_channel_ids": {},
        "outside_node_id": None,
        "deterministic_fingerprint": canonical_sha256({"empty": True}),
    }

    scale = max(1, _as_int(fixed_point_scale, 1000))
    substeps = _substeps_for_dt(
        dt_ticks=max(1, _as_int(dt_ticks, 1)),
        max_substep_ticks=max(1, _as_int(policy_row.get("max_substep_ticks", 16), 16)),
    )
    update_interval = max(0, _as_int(policy_row.get("update_interval_ticks", 1), 1))
    strict_budget = bool(policy_row.get("strict_budget", False))
    max_channels_per_tick = max(0, _as_int(policy_row.get("max_channels_per_tick", 1024), 1024))
    max_hazards_per_tick = max(0, _as_int(policy_row.get("max_hazards_per_tick", 1024), 1024))

    tick_cursor = int(max(0, _as_int(current_tick, 0)))
    for bucket_ticks in substeps:
        for _ in range(int(max(1, _as_int(bucket_ticks, 1)))):
            due = update_interval <= 1 or (int(tick_cursor) % int(update_interval) == 0)
            if not due:
                tick_cursor += 1
                continue
            try:
                flow_build = build_compartment_flow_channels(
                    interior_graph_row=interior_graph_row,
                    volume_rows=list(volume_index.values()),
                    portal_rows=portal_rows,
                    portal_state_rows=portal_state_rows,
                    portal_flow_param_rows=portal_flow_param_rows,
                    leak_hazard_rows=list(leak_rows_by_id.values()),
                    portal_flow_template_registry=portal_flow_template_registry,
                    flow_solver_policy_id=str(policy_row.get("flow_solver_policy_id", "flow.coarse_default")),
                    fixed_point_scale=scale,
                    include_smoke=bool(include_smoke),
                )
            except CompartmentFlowBuilderError as exc:
                raise CompartmentFlowEngineError(
                    str(exc.reason_code),
                    str(exc),
                    dict(exc.details),
                ) from exc
            except Exception as exc:  # pragma: no cover - defensive conversion
                raise CompartmentFlowEngineError(
                    REFUSAL_COMPARTMENT_FLOW_INVALID,
                    "failed to build compartment flow channels",
                    {"error": str(exc)},
                ) from exc

            last_flow_build = dict(flow_build)
            outside_node_id = str(flow_build.get("outside_node_id") or "").strip()
            channels_by_medium = _channel_rows_by_medium(flow_build)
            for medium_id in sorted(channels_by_medium.keys()):
                channel_rows = list(channels_by_medium.get(medium_id) or [])
                if not channel_rows:
                    continue
                medium_balances = _flow_balance_for_medium(
                    medium_id=medium_id,
                    states_by_volume_id=states_by_volume_id,
                    volume_ids=list(flow_build.get("volume_ids") or []),
                    outside_node_id=outside_node_id,
                    outside_reservoir=outside_index,
                )
                medium_runtime = dict(
                    (str(row.get("channel_id", "")), dict(runtime_by_channel.get(str(row.get("channel_id", "")), {})))
                    for row in channel_rows
                    if str(row.get("channel_id", "")).strip()
                )
                gradient_channels = _gradient_limited_channels(
                    medium_balances=medium_balances,
                    channel_rows=channel_rows,
                )
                try:
                    ticked = tick_flow_channels(
                        channels=gradient_channels,
                        node_balances=medium_balances,
                        current_tick=int(tick_cursor),
                        fixed_point_scale=scale,
                        solver_policies=solver_policy_rows,
                        conserved_quantity_ids=list(conserved_quantity_ids or ["quantity.mass"]),
                        max_channels=int(max_channels_per_tick),
                        strict_budget=bool(strict_budget),
                        sink_capacities={},
                        channel_runtime=medium_runtime,
                        graph_row={
                            "schema_version": "1.0.0",
                            "graph_id": str(flow_build.get("graph_id", "")).strip(),
                            "node_type_schema_id": "interior.volume",
                            "edge_type_schema_id": "interior.portal",
                            "nodes": [
                                {
                                    "schema_version": "1.0.0",
                                    "node_id": token,
                                    "node_type_id": "interior.volume",
                                    "payload_ref": {},
                                    "tags": [],
                                    "extensions": {},
                                }
                                for token in sorted(_sorted_unique_strings(list(flow_build.get("node_ids") or [])))
                            ],
                            "edges": [
                                {
                                    "schema_version": "1.0.0",
                                    "edge_id": str(row.get("edge_id", "")).strip(),
                                    "from_node_id": str(row.get("from_node_id", "")).strip(),
                                    "to_node_id": str(row.get("to_node_id", "")).strip(),
                                    "edge_type_id": "interior.portal",
                                    "payload_ref": {},
                                    "capacity": None,
                                    "delay_ticks": 0,
                                    "loss_fraction": 0,
                                    "cost_units": 0,
                                    "extensions": {},
                                }
                                for row in list(flow_build.get("route_edges") or [])
                                if isinstance(row, dict)
                            ],
                            "deterministic_routing_policy_id": "route.direct",
                            "extensions": {},
                        },
                        partition_row=graph_partition_row,
                        cost_units_per_channel=max(1, _as_int(cost_units_per_channel, 1)),
                    )
                except FlowEngineError as exc:
                    refusal_code = REFUSAL_COMPARTMENT_FLOW_BUDGET_EXCEEDED if str(exc.reason_code) == "refusal.core.flow.capacity_insufficient" else REFUSAL_COMPARTMENT_FLOW_INVALID
                    raise CompartmentFlowEngineError(
                        refusal_code,
                        str(exc),
                        dict(exc.details),
                    ) from exc

                for channel_id, row in sorted((dict(ticked.get("channel_runtime") or {})).items(), key=lambda item: str(item[0])):
                    if str(channel_id).strip():
                        runtime_by_channel[str(channel_id)] = dict(row) if isinstance(row, dict) else {}
                _apply_medium_balance(
                    medium_id=medium_id,
                    balances=dict(ticked.get("node_balances") or {}),
                    states_by_volume_id=states_by_volume_id,
                    volume_ids=list(flow_build.get("volume_ids") or []),
                    outside_node_id=outside_node_id,
                    outside_reservoir=outside_index,
                )
                for event_row in list(ticked.get("transfer_events") or []):
                    if not isinstance(event_row, dict):
                        continue
                    payload = dict(event_row)
                    ext = dict(payload.get("extensions") or {})
                    ext["medium_id"] = medium_id
                    payload["extensions"] = ext
                    flow_transfer_events.append(payload)
                for loss_row in list(ticked.get("loss_entries") or []):
                    if not isinstance(loss_row, dict):
                        continue
                    payload = dict(loss_row)
                    payload["medium_id"] = medium_id
                    flow_loss_entries.append(payload)
                processed_channel_count += max(0, _as_int(ticked.get("processed_count", 0), 0))
                remaining_channel_count += max(0, _as_int(ticked.get("remaining_count", 0), 0))
                flow_cost_units += max(0, _as_int(ticked.get("cost_units", 0), 0))
                if str(ticked.get("budget_outcome", "complete")).strip() != "complete":
                    budget_outcome = "degraded"

            if hazard_rows:
                delta_by_hazard_id: Dict[str, int] = {}
                for leak_row in list(leak_rows_by_id.values()):
                    if not isinstance(leak_row, dict):
                        continue
                    hazard_model_id = str(leak_row.get("hazard_model_id", "")).strip()
                    if not hazard_model_id:
                        continue
                    leak_delta = max(0, _as_int(leak_row.get("leak_rate_air", 0), 0)) + max(0, _as_int(leak_row.get("leak_rate_water", 0), 0))
                    if leak_delta <= 0:
                        leak_delta = 1
                    delta_by_hazard_id[hazard_model_id] = _as_int(delta_by_hazard_id.get(hazard_model_id, 0), 0) + int(leak_delta)
                hazard_tick = tick_hazard_models(
                    hazard_rows=hazard_rows,
                    current_tick=int(tick_cursor),
                    delta_by_hazard_id=delta_by_hazard_id,
                    max_hazards=int(max_hazards_per_tick),
                    cost_units_per_hazard=max(1, _as_int(cost_units_per_hazard, 1)),
                )
                hazard_rows = [dict(row) for row in list(hazard_tick.get("hazards") or []) if isinstance(row, dict)]
                hazard_consequence_events.extend(
                    dict(row)
                    for row in list(hazard_tick.get("consequence_events") or [])
                    if isinstance(row, dict)
                )
                processed_hazard_count += max(0, _as_int(hazard_tick.get("processed_count", 0), 0))
                deferred_hazard_count += max(0, _as_int(hazard_tick.get("deferred_count", 0), 0))
                hazard_cost_units += max(0, _as_int(hazard_tick.get("cost_units", 0), 0))
                if str(hazard_tick.get("budget_outcome", "complete")).strip() != "complete":
                    budget_outcome = "degraded"

            tick_cursor += 1

    volume_capacity_liters_by_id: Dict[str, int] = {}
    for volume_id in sorted(states_by_volume_id.keys()):
        volume_row = dict(volume_index.get(volume_id) or {})
        volume_capacity_liters_by_id[volume_id] = _volume_capacity_liters(volume_row) if volume_row else 1

    for volume_id in sorted(states_by_volume_id.keys()):
        row = dict(states_by_volume_id.get(volume_id) or {})
        if row.get("oxygen_fraction") is None:
            row["oxygen_fraction"] = 210
        if row.get("smoke_density") is None:
            row["smoke_density"] = 0
        air_mass = max(0, _as_int(row.get("air_mass", 0), 0))
        liters = int(max(1, _as_int(volume_capacity_liters_by_id.get(volume_id, 1), 1)))
        row["derived_pressure"] = _pressure_from_air_mass(
            air_mass=air_mass,
            volume_liters=liters,
            fixed_point_scale=scale,
        )
        states_by_volume_id[volume_id] = row

    alarms = [
        _compose_alarm_row(volume_id=volume_id, state_row=states_by_volume_id[volume_id], policy_row=policy_row)
        for volume_id in sorted(states_by_volume_id.keys())
    ]
    movement_constraints = _movement_constraint_rows(states_by_volume_id=states_by_volume_id, policy_row=policy_row)

    states_out = [
        dict(states_by_volume_id[volume_id])
        for volume_id in sorted(states_by_volume_id.keys())
    ]
    for row in states_out:
        row.setdefault("schema_version", "1.0.0")
        row.setdefault("extensions", {})
        row["extensions"] = dict(row.get("extensions") or {})

    flow_transfer_events = sorted(
        (dict(row) for row in flow_transfer_events if isinstance(row, dict)),
        key=lambda row: (_as_int(row.get("tick", 0), 0), str(row.get("event_id", ""))),
    )
    flow_loss_entries = sorted(
        (dict(row) for row in flow_loss_entries if isinstance(row, dict)),
        key=lambda row: (str(row.get("medium_id", "")), str(row.get("channel_id", ""))),
    )
    hazard_consequence_events = sorted(
        (dict(row) for row in hazard_consequence_events if isinstance(row, dict)),
        key=lambda row: (_as_int(row.get("tick", 0), 0), str(row.get("hazard_id", ""))),
    )

    fingerprint_seed = {
        "current_tick": int(max(0, _as_int(current_tick, 0))),
        "dt_ticks": int(max(1, _as_int(dt_ticks, 1))),
        "policy_id": str(policy_row.get("policy_id", "")),
        "state_rows": states_out,
        "outside_reservoir": dict((key, int(outside_index[key])) for key in sorted(outside_index.keys())),
        "transfer_event_ids": [str(row.get("event_id", "")) for row in flow_transfer_events],
        "hazard_event_ids": [str(row.get("hazard_id", "")) for row in hazard_consequence_events],
    }

    return {
        "states": states_out,
        "outside_reservoir": dict((key, int(outside_index[key])) for key in sorted(outside_index.keys())),
        "channel_runtime": dict((key, dict(runtime_by_channel[key])) for key in sorted(runtime_by_channel.keys())),
        "flow_transfer_events": flow_transfer_events,
        "flow_loss_entries": flow_loss_entries,
        "hazards": sorted(hazard_rows, key=lambda row: str(row.get("hazard_id", ""))),
        "hazard_consequence_events": hazard_consequence_events,
        "flow_build": dict(last_flow_build),
        "alarm_summary": sorted(alarms, key=lambda row: str(row.get("volume_id", ""))),
        "movement_constraints": movement_constraints,
        "processed_channel_count": int(processed_channel_count),
        "remaining_channel_count": int(remaining_channel_count),
        "processed_hazard_count": int(processed_hazard_count),
        "deferred_hazard_count": int(deferred_hazard_count),
        "cost_units": int(max(0, flow_cost_units + hazard_cost_units)),
        "budget_outcome": "degraded" if (budget_outcome != "complete" or remaining_channel_count > 0 or deferred_hazard_count > 0) else "complete",
        "deterministic_fingerprint": canonical_sha256(fingerprint_seed),
    }


__all__ = [
    "CompartmentFlowEngineError",
    "REFUSAL_COMPARTMENT_FLOW_BUDGET_EXCEEDED",
    "REFUSAL_COMPARTMENT_FLOW_INVALID",
    "normalize_compartment_flow_policy_row",
    "resolve_compartment_flow_policy_row",
    "tick_compartment_flows",
]
