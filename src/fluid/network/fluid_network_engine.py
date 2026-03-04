"""Deterministic FLUID F0/F1 network + FLUID-2 containment helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from src.control.effects import get_effective_modifier
from src.core.flow import flow_transfer, normalize_flow_channel, normalize_flow_transfer_event
from src.core.graph.network_graph_engine import normalize_network_graph
from src.meta.explain import generate_explain_artifact
from src.models.model_engine import (
    cache_policy_rows_by_id,
    evaluate_model_bindings,
    model_type_rows_by_id,
    normalize_constitutive_model_rows,
)
from src.safety.safety_engine import build_safety_event
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_FLUID_NETWORK_INVALID = "refusal.fluid.network_invalid"

_VALID_NODE_KINDS = {"tank", "junction", "pump", "valve", "pressure_vessel"}
_VALID_EDGE_KINDS = {"pipe", "hose", "channel"}

_Q_MASS_FLOW = "quantity.mass_flow"
_Q_PRESSURE_HEAD = "quantity.pressure_head"

_MODEL_PUMP = "model_type.fluid_pump_curve_stub"
_MODEL_VALVE = "model_type.fluid_valve_curve_stub"
_MODEL_PIPE = "model_type.fluid_pipe_loss_stub"
_MODEL_CAVITATION = "model_type.fluid_cavitation_stub"
_MODEL_LEAK = "model_type.fluid_leak_rate_stub"

_PATTERN_RELIEF = "safety.relief_pressure"
_PATTERN_BURST = "safety.burst_disk"

_HAZARD_CAVITATION = "hazard.cavitation"
_HAZARD_BURST = "hazard.fluid.burst"
_HAZARD_LEAK = "hazard.fluid.leak"


class FluidError(ValueError):
    """Deterministic fluid-domain refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code or REFUSAL_FLUID_NETWORK_INVALID)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda token: str(token)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _token_set(values: object) -> set:
    return set(_sorted_tokens(values))


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return int(max(int(minimum), min(int(maximum), int(value))))


def normalize_fluid_node_payload(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    node_kind = str(payload.get("node_kind", "")).strip()
    fluid_profile_id = str(payload.get("fluid_profile_id", "")).strip()
    if node_kind not in _VALID_NODE_KINDS:
        raise FluidError(
            REFUSAL_FLUID_NETWORK_INVALID,
            "fluid node payload requires valid node_kind",
            {"node_kind": node_kind},
        )
    if not fluid_profile_id:
        raise FluidError(
            REFUSAL_FLUID_NETWORK_INVALID,
            "fluid node payload requires fluid_profile_id",
            {"node_kind": node_kind},
        )
    result = {
        "schema_version": "1.0.0",
        "node_kind": node_kind,
        "fluid_profile_id": fluid_profile_id,
        "spec_id": None if payload.get("spec_id") is None else str(payload.get("spec_id", "")).strip() or None,
        "model_bindings": _sorted_tokens(payload.get("model_bindings")),
        "safety_instances": _sorted_tokens(payload.get("safety_instances")),
        "state_ref": _canon(_as_map(payload.get("state_ref"))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(payload.get("extensions"))),
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def normalize_fluid_edge_payload(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    edge_kind = str(payload.get("edge_kind", "")).strip()
    if edge_kind not in _VALID_EDGE_KINDS:
        raise FluidError(
            REFUSAL_FLUID_NETWORK_INVALID,
            "fluid edge payload requires valid edge_kind",
            {"edge_kind": edge_kind},
        )
    result = {
        "schema_version": "1.0.0",
        "edge_kind": edge_kind,
        "length": int(max(0, _as_int(payload.get("length", 0), 0))),
        "diameter_proxy": int(max(0, _as_int(payload.get("diameter_proxy", 0), 0))),
        "roughness_proxy": int(max(0, _as_int(payload.get("roughness_proxy", 0), 0))),
        "capacity_rating": int(max(0, _as_int(payload.get("capacity_rating", 0), 0))),
        "spec_id": None if payload.get("spec_id") is None else str(payload.get("spec_id", "")).strip() or None,
        "model_bindings": _sorted_tokens(payload.get("model_bindings")),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(payload.get("extensions"))),
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def build_tank_state(
    *,
    node_id: str,
    stored_mass: int,
    max_mass: int,
    last_update_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    normalized_node_id = str(node_id or "").strip()
    if not normalized_node_id:
        raise FluidError(
            REFUSAL_FLUID_NETWORK_INVALID,
            "tank_state requires node_id",
            {"node_id": normalized_node_id},
        )
    normalized_max = int(max(0, _as_int(max_mass, 0)))
    normalized_stored = int(max(0, _as_int(stored_mass, 0)))
    if normalized_max > 0:
        normalized_stored = int(min(normalized_stored, normalized_max))
    payload = {
        "schema_version": "1.0.0",
        "node_id": normalized_node_id,
        "stored_mass": int(normalized_stored),
        "max_mass": int(normalized_max),
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_tank_state_rows(
    *,
    rows: object,
    current_tick: int,
    node_rows: object = None,
) -> List[dict]:
    out: Dict[str, dict] = {}
    if isinstance(rows, list):
        for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("node_id", ""))):
            node_id = str(row.get("node_id", "")).strip()
            if not node_id:
                continue
            try:
                out[node_id] = build_tank_state(
                    node_id=node_id,
                    stored_mass=int(max(0, _as_int(row.get("stored_mass", 0), 0))),
                    max_mass=int(max(0, _as_int(row.get("max_mass", 0), 0))),
                    last_update_tick=int(max(0, _as_int(row.get("last_update_tick", current_tick), current_tick))),
                    extensions=_as_map(row.get("extensions")),
                )
            except FluidError:
                continue
    if isinstance(node_rows, list):
        for node_row in sorted((dict(item) for item in node_rows if isinstance(item, Mapping)), key=lambda item: str(item.get("node_id", ""))):
            node_id = str(node_row.get("node_id", "")).strip()
            if not node_id or node_id in out:
                continue
            try:
                payload = normalize_fluid_node_payload(_as_map(node_row.get("payload")))
            except FluidError:
                continue
            node_kind = str(payload.get("node_kind", "")).strip()
            if node_kind not in {"tank", "pressure_vessel"}:
                continue
            state_ref = _as_map(payload.get("state_ref"))
            stored_mass = int(
                max(
                    0,
                    _as_int(
                        state_ref.get(
                            "stored_mass",
                            state_ref.get("tank_level_mass", state_ref.get("initial_stored_mass", 0)),
                        ),
                        0,
                    ),
                )
            )
            max_mass = int(
                max(
                    stored_mass,
                    _as_int(
                        state_ref.get(
                            "max_mass",
                            state_ref.get("tank_max_mass", state_ref.get("capacity_mass", stored_mass)),
                        ),
                        stored_mass,
                    ),
                )
            )
            out[node_id] = build_tank_state(
                node_id=node_id,
                stored_mass=stored_mass,
                max_mass=max_mass,
                last_update_tick=int(max(0, _as_int(current_tick, 0))),
                extensions={"auto_seeded_from_node_payload": True},
            )
    return [dict(out[key]) for key in sorted(out.keys())]


def _event_id(prefix: str, payload: Mapping[str, object]) -> str:
    token = str(prefix or "").strip() or "event"
    return "{}.{}".format(token, canonical_sha256(dict(payload or {}))[:16])


def build_pressure_vessel_state(
    *,
    node_id: str,
    current_head: int,
    last_update_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    node_token = str(node_id or "").strip()
    if not node_token:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "node_id": node_token,
        "current_head": int(max(0, _as_int(current_head, 0))),
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_pressure_vessel_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("node_id", ""))):
        normalized = build_pressure_vessel_state(
            node_id=str(row.get("node_id", "")).strip(),
            current_head=_as_int(row.get("current_head", 0), 0),
            last_update_tick=_as_int(row.get("last_update_tick", 0), 0),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("node_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_leak_state(
    *,
    target_id: str,
    leak_rate: int,
    active: bool,
    last_update_tick: int,
    source_node_id: str = "",
    sink_kind: str = "external",
    sink_id: str = "",
    originating_process_id: str = "process.start_leak",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    target_token = str(target_id or "").strip()
    if not target_token:
        return {}
    ext = _as_map(extensions)
    ext["source_node_id"] = str(source_node_id or ext.get("source_node_id", "")).strip()
    ext["sink_kind"] = str(sink_kind or ext.get("sink_kind", "external")).strip() or "external"
    ext["sink_id"] = str(sink_id or ext.get("sink_id", "")).strip()
    ext["originating_process_id"] = str(originating_process_id or ext.get("originating_process_id", "")).strip()
    payload = {
        "schema_version": "1.0.0",
        "target_id": target_token,
        "leak_rate": int(max(0, _as_int(leak_rate, 0))),
        "active": bool(active),
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(ext),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_leak_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("target_id", ""))):
        normalized = build_leak_state(
            target_id=str(row.get("target_id", "")).strip(),
            leak_rate=_as_int(row.get("leak_rate", 0), 0),
            active=bool(row.get("active", False)),
            last_update_tick=_as_int(row.get("last_update_tick", 0), 0),
            source_node_id=str(_as_map(row.get("extensions")).get("source_node_id", "")),
            sink_kind=str(_as_map(row.get("extensions")).get("sink_kind", "external")),
            sink_id=str(_as_map(row.get("extensions")).get("sink_id", "")),
            originating_process_id=str(_as_map(row.get("extensions")).get("originating_process_id", "process.start_leak")),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("target_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_burst_event(
    *,
    event_id: str,
    target_id: str,
    overpressure_value: int,
    current_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    target_token = str(target_id or "").strip()
    if not target_token:
        return {}
    token = str(event_id or "").strip()
    if not token:
        token = _event_id(
            "event.fluid.burst",
            {
                "target_id": target_token,
                "overpressure_value": int(_as_int(overpressure_value, 0)),
                "tick": int(_as_int(current_tick, 0)),
            },
        )
    ext = _as_map(extensions)
    ext["tick"] = int(max(0, _as_int(current_tick, 0)))
    payload = {
        "schema_version": "1.0.0",
        "event_id": token,
        "target_id": target_token,
        "overpressure_value": int(_as_int(overpressure_value, 0)),
        "deterministic_fingerprint": "",
        "extensions": _canon(ext),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_burst_event_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("event_id", ""))):
        ext = _as_map(row.get("extensions"))
        normalized = build_burst_event(
            event_id=str(row.get("event_id", "")).strip(),
            target_id=str(row.get("target_id", "")).strip(),
            overpressure_value=_as_int(row.get("overpressure_value", 0), 0),
            current_tick=_as_int(ext.get("tick", 0), 0),
            extensions=ext,
        )
        if not normalized:
            continue
        out[str(normalized.get("event_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def process_start_leak(
    *,
    leak_state_rows: object,
    target_id: str,
    leak_rate: int,
    current_tick: int,
    source_node_id: str = "",
    sink_kind: str = "external",
    sink_id: str = "",
    originating_process_id: str = "process.start_leak",
) -> dict:
    leak_rows = normalize_leak_state_rows(leak_state_rows)
    leak_by_target = dict((str(row.get("target_id", "")).strip(), dict(row)) for row in leak_rows if str(row.get("target_id", "")).strip())
    normalized = build_leak_state(
        target_id=str(target_id),
        leak_rate=int(max(0, _as_int(leak_rate, 0))),
        active=bool(int(max(0, _as_int(leak_rate, 0))) > 0),
        last_update_tick=int(max(0, _as_int(current_tick, 0))),
        source_node_id=str(source_node_id),
        sink_kind=str(sink_kind),
        sink_id=str(sink_id),
        originating_process_id=str(originating_process_id),
        extensions={},
    )
    if normalized:
        leak_by_target[str(normalized.get("target_id", ""))] = normalized
    leak_out = [dict(leak_by_target[key]) for key in sorted(leak_by_target.keys())]
    leak_event = {
        "event_id": _event_id(
            "event.fluid.leak_start",
            {
                "target_id": str(target_id),
                "tick": int(max(0, _as_int(current_tick, 0))),
                "leak_rate": int(max(0, _as_int(leak_rate, 0))),
            },
        ),
        "event_kind_id": "fluid.leak",
        "tick": int(max(0, _as_int(current_tick, 0))),
        "target_id": str(target_id or "").strip(),
        "leak_rate": int(max(0, _as_int(leak_rate, 0))),
        "source_node_id": str(source_node_id or "").strip(),
        "sink_kind": str(sink_kind or "external").strip() or "external",
        "sink_id": str(sink_id or "").strip(),
    }
    return {
        "leak_state_rows": leak_out,
        "leak_state": dict(normalized),
        "leak_event_rows": [leak_event] if normalized else [],
    }


def process_burst_event(
    *,
    burst_event_rows: object,
    leak_state_rows: object,
    target_id: str,
    overpressure_value: int,
    current_tick: int,
    source_node_id: str = "",
    sink_kind: str = "external",
    sink_id: str = "",
    leak_rate: int = 0,
) -> dict:
    burst_rows = normalize_burst_event_rows(burst_event_rows)
    burst_event = build_burst_event(
        event_id="",
        target_id=str(target_id),
        overpressure_value=int(max(0, _as_int(overpressure_value, 0))),
        current_tick=int(max(0, _as_int(current_tick, 0))),
        extensions={"originating_process_id": "process.burst_event"},
    )
    burst_by_id = dict((str(row.get("event_id", "")).strip(), dict(row)) for row in burst_rows if str(row.get("event_id", "")).strip())
    if burst_event:
        burst_by_id[str(burst_event.get("event_id", ""))] = burst_event
    normalized_leak_rate = int(max(1, _as_int(leak_rate, 0)))
    leak_start = process_start_leak(
        leak_state_rows=leak_state_rows,
        target_id=str(target_id),
        leak_rate=int(normalized_leak_rate),
        current_tick=int(current_tick),
        source_node_id=str(source_node_id),
        sink_kind=str(sink_kind),
        sink_id=str(sink_id),
        originating_process_id="process.burst_event",
    )
    burst_hazard = {
        "schema_version": "1.0.0",
        "target_id": str(target_id or "").strip(),
        "hazard_type_id": _HAZARD_BURST,
        "accumulated_value": int(max(1, _as_int(overpressure_value, 0))),
        "last_update_tick": int(max(0, _as_int(current_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": {"source": "process.burst_event"},
    }
    burst_hazard["deterministic_fingerprint"] = canonical_sha256(dict(burst_hazard, deterministic_fingerprint=""))
    return {
        "burst_event_rows": [dict(burst_by_id[key]) for key in sorted(burst_by_id.keys())],
        "burst_event": dict(burst_event),
        "leak_state_rows": [dict(row) for row in list(leak_start.get("leak_state_rows") or []) if isinstance(row, Mapping)],
        "leak_event_rows": [dict(row) for row in list(leak_start.get("leak_event_rows") or []) if isinstance(row, Mapping)],
        "hazard_rows": [burst_hazard],
    }


def process_leak_tick(
    *,
    current_tick: int,
    leak_state_rows: object,
    tank_state_by_node_id: Mapping[str, object],
    max_processed_targets: int = 64,
) -> dict:
    leak_rows = normalize_leak_state_rows(leak_state_rows)
    tank_rows = dict((str(key).strip(), dict(value)) for key, value in dict(tank_state_by_node_id or {}).items() if str(key).strip())
    flow_transfer_events: List[dict] = []
    leak_event_rows: List[dict] = []
    interior_coupling_rows: List[dict] = []
    hazard_rows: List[dict] = []
    out_rows: List[dict] = []
    processed_count = 0
    deferred_count = 0
    decision_log_rows: List[dict] = []
    max_targets = int(max(1, _as_int(max_processed_targets, 64)))
    for row in sorted((dict(item) for item in leak_rows if isinstance(item, Mapping)), key=lambda item: str(item.get("target_id", ""))):
        target_id = str(row.get("target_id", "")).strip()
        if not target_id:
            continue
        if processed_count >= max_targets:
            deferred_count += 1
            out_rows.append(dict(row))
            continue
        processed_count += 1
        ext = _as_map(row.get("extensions"))
        source_node_id = str(ext.get("source_node_id", "")).strip()
        sink_kind = str(ext.get("sink_kind", "external")).strip() or "external"
        sink_id = str(ext.get("sink_id", "")).strip()
        active = bool(row.get("active", False))
        leak_rate = int(max(0, _as_int(row.get("leak_rate", 0), 0)))
        if (not active) or leak_rate <= 0 or (not source_node_id):
            out_rows.append(
                build_leak_state(
                    target_id=target_id,
                    leak_rate=leak_rate,
                    active=False,
                    last_update_tick=int(max(0, _as_int(current_tick, 0))),
                    source_node_id=source_node_id,
                    sink_kind=sink_kind,
                    sink_id=sink_id,
                    originating_process_id=str(ext.get("originating_process_id", "process.leak_tick")),
                    extensions=ext,
                )
            )
            continue
        source_tank = dict(tank_rows.get(source_node_id) or {})
        source_mass = int(max(0, _as_int(source_tank.get("stored_mass", 0), 0)))
        request = int(max(0, min(leak_rate, source_mass)))
        transfer = flow_transfer(
            quantity=int(request),
            loss_fraction=0,
            scale=1000,
            capacity_per_tick=max(1, leak_rate),
            delay_ticks=0,
        )
        processed_mass = int(max(0, _as_int(transfer.get("processed_mass", 0), 0)))
        delivered_mass = int(max(0, _as_int(transfer.get("delivered_mass", 0), 0)))
        source_tank["stored_mass"] = int(max(0, source_mass - processed_mass))
        if source_tank:
            tank_rows[source_node_id] = dict(source_tank)
        channel_id = "channel.fluid.leak.{}".format(canonical_sha256({"target_id": target_id})[:16])
        flow_transfer_events.append(
            _flow_transfer_event(
                current_tick=int(current_tick),
                channel_id=channel_id,
                edge_id=target_id,
                transferred_amount=int(delivered_mass),
                lost_amount=0,
            )
        )
        event_row = {
            "event_id": _event_id(
                "event.fluid.leak_tick",
                {
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "target_id": target_id,
                    "delivered_mass": int(delivered_mass),
                },
            ),
            "event_kind_id": "fluid.leak",
            "tick": int(max(0, _as_int(current_tick, 0))),
            "target_id": target_id,
            "source_node_id": source_node_id,
            "sink_kind": sink_kind,
            "sink_id": sink_id,
            "transferred_mass": int(delivered_mass),
        }
        leak_event_rows.append(event_row)
        hazard_value = int(max(1, delivered_mass // 25)) if delivered_mass > 0 else 0
        if hazard_value > 0:
            hazard_row = {
                "schema_version": "1.0.0",
                "target_id": target_id,
                "hazard_type_id": _HAZARD_LEAK,
                "accumulated_value": int(hazard_value),
                "last_update_tick": int(max(0, _as_int(current_tick, 0))),
                "deterministic_fingerprint": "",
                "extensions": {"sink_kind": sink_kind, "sink_id": sink_id},
            }
            hazard_row["deterministic_fingerprint"] = canonical_sha256(dict(hazard_row, deterministic_fingerprint=""))
            hazard_rows.append(hazard_row)
        if sink_kind == "interior":
            interior_coupling_rows.append(
                {
                    "compartment_id": str(sink_id).strip(),
                    "source_target_id": target_id,
                    "transferred_mass": int(delivered_mass),
                    "hazard_flood_increment": int(max(0, delivered_mass // 10)),
                    "tick": int(max(0, _as_int(current_tick, 0))),
                }
            )
        next_active = bool(leak_rate > 0 and int(source_tank.get("stored_mass", 0)) > 0)
        out_rows.append(
            build_leak_state(
                target_id=target_id,
                leak_rate=leak_rate,
                active=next_active,
                last_update_tick=int(max(0, _as_int(current_tick, 0))),
                source_node_id=source_node_id,
                sink_kind=sink_kind,
                sink_id=sink_id,
                originating_process_id=str(ext.get("originating_process_id", "process.leak_tick")),
                extensions=ext,
            )
        )
    budget_outcome = "degraded" if deferred_count > 0 else "complete"
    if deferred_count > 0:
        decision_log_rows.append(
            {
                "process_id": "process.leak_tick",
                "tick": int(max(0, _as_int(current_tick, 0))),
                "target_id": "fluid.leak_runtime",
                "reason_code": "degrade.fluid.leak_eval_cap",
                "details": {
                    "processed_count": int(processed_count),
                    "deferred_count": int(deferred_count),
                    "max_processed_targets": int(max_targets),
                },
            }
        )
    return {
        "leak_state_rows": [dict(row) for row in out_rows if isinstance(row, Mapping)],
        "tank_state_by_node_id": dict((key, dict(tank_rows[key])) for key in sorted(tank_rows.keys())),
        "flow_transfer_events": sorted(
            (dict(row) for row in flow_transfer_events if isinstance(row, Mapping)),
            key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))),
        ),
        "leak_event_rows": sorted(
            (dict(row) for row in leak_event_rows if isinstance(row, Mapping)),
            key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))),
        ),
        "interior_coupling_rows": sorted(
            (dict(row) for row in interior_coupling_rows if isinstance(row, Mapping)),
            key=lambda row: (str(row.get("compartment_id", "")), str(row.get("source_target_id", ""))),
        ),
        "hazard_rows": sorted(
            (dict(row) for row in hazard_rows if isinstance(row, Mapping)),
            key=lambda row: (str(row.get("target_id", "")), str(row.get("hazard_type_id", ""))),
        ),
        "processed_count": int(processed_count),
        "deferred_count": int(deferred_count),
        "budget_outcome": budget_outcome,
        "decision_log_rows": decision_log_rows,
    }


def deterministic_fluid_channel_id(*, graph_id: str, edge_id: str) -> str:
    digest = canonical_sha256(
        {
            "graph_id": str(graph_id or "").strip(),
            "edge_id": str(edge_id or "").strip(),
            "kind": "fluid_flow_channel",
        }
    )
    return "channel.fluid.{}".format(digest[:16])


def build_fluid_flow_channel(
    *,
    graph_id: str,
    edge_id: str,
    source_node_id: str,
    sink_node_id: str,
    capacity_per_tick: int,
    solver_policy_id: str = "flow.solver.default",
    component_capacity_policy_id: str = "comp_capacity.default_bundle",
    component_loss_policy_id: str = "comp_loss.default_bundle",
) -> dict:
    return normalize_flow_channel(
        {
            "schema_version": "1.1.0",
            "channel_id": deterministic_fluid_channel_id(graph_id=graph_id, edge_id=edge_id),
            "graph_id": str(graph_id or "").strip(),
            "quantity_bundle_id": "bundle.fluid_basic",
            "component_capacity_policy_id": str(component_capacity_policy_id or "").strip() or None,
            "component_loss_policy_id": str(component_loss_policy_id or "").strip() or None,
            "source_node_id": str(source_node_id or "").strip(),
            "sink_node_id": str(sink_node_id or "").strip(),
            "capacity_per_tick": int(max(0, _as_int(capacity_per_tick, 0))),
            "delay_ticks": 0,
            "loss_fraction": 0,
            "solver_policy_id": str(solver_policy_id or "").strip() or "flow.solver.default",
            "priority": 0,
            "extensions": {
                "edge_id": str(edge_id or "").strip(),
                "component_weights": {
                    _Q_MASS_FLOW: 1000,
                    _Q_PRESSURE_HEAD: 100,
                },
            },
        }
    )


def _default_constitutive_model_rows() -> List[dict]:
    return [
        {
            "schema_version": "1.0.0",
            "model_id": "model.fluid_pump_curve_stub",
            "model_type_id": _MODEL_PUMP,
            "description": "deterministic fluid pump head-gain model",
            "supported_tiers": ["macro", "meso"],
            "input_signature": [],
            "output_signature": [
                {
                    "schema_version": "1.0.0",
                    "output_kind": "flow_adjustment",
                    "output_id": _Q_PRESSURE_HEAD,
                    "extensions": {
                        "quantity_bundle_id": "bundle.fluid_basic",
                        "component_quantity_id": _Q_PRESSURE_HEAD,
                    },
                },
                {
                    "schema_version": "1.0.0",
                    "output_kind": "derived_quantity",
                    "output_id": "derived.fluid.pump_head_gain",
                    "extensions": {},
                },
            ],
            "cost_units": 1,
            "cache_policy_id": "cache.by_inputs_hash",
            "uses_rng_stream": False,
            "rng_stream_name": None,
            "version_introduced": "1.0.0",
            "deprecated": False,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "model_id": "model.fluid_valve_curve_stub",
            "model_type_id": _MODEL_VALVE,
            "description": "deterministic fluid valve restriction model",
            "supported_tiers": ["macro", "meso"],
            "input_signature": [],
            "output_signature": [
                {
                    "schema_version": "1.0.0",
                    "output_kind": "flow_adjustment",
                    "output_id": _Q_MASS_FLOW,
                    "extensions": {
                        "quantity_bundle_id": "bundle.fluid_basic",
                        "component_quantity_id": _Q_MASS_FLOW,
                    },
                },
                {
                    "schema_version": "1.0.0",
                    "output_kind": "derived_quantity",
                    "output_id": "derived.fluid.valve_head_loss",
                    "extensions": {},
                },
            ],
            "cost_units": 1,
            "cache_policy_id": "cache.by_inputs_hash",
            "uses_rng_stream": False,
            "rng_stream_name": None,
            "version_introduced": "1.0.0",
            "deprecated": False,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "model_id": "model.fluid_pipe_loss_stub",
            "model_type_id": _MODEL_PIPE,
            "description": "deterministic fluid pipe friction head-loss model",
            "supported_tiers": ["macro", "meso"],
            "input_signature": [],
            "output_signature": [
                {
                    "schema_version": "1.0.0",
                    "output_kind": "flow_adjustment",
                    "output_id": _Q_PRESSURE_HEAD,
                    "extensions": {
                        "quantity_bundle_id": "bundle.fluid_basic",
                        "component_quantity_id": _Q_PRESSURE_HEAD,
                    },
                },
                {
                    "schema_version": "1.0.0",
                    "output_kind": "derived_quantity",
                    "output_id": "derived.fluid.pipe_head_loss",
                    "extensions": {},
                },
            ],
            "cost_units": 1,
            "cache_policy_id": "cache.by_inputs_hash",
            "uses_rng_stream": False,
            "rng_stream_name": None,
            "version_introduced": "1.0.0",
            "deprecated": False,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "model_id": "model.fluid_cavitation_stub",
            "model_type_id": _MODEL_CAVITATION,
            "description": "deterministic fluid cavitation hazard model",
            "supported_tiers": ["macro", "meso"],
            "input_signature": [],
            "output_signature": [
                {
                    "schema_version": "1.0.0",
                    "output_kind": "hazard_increment",
                    "output_id": "hazard.cavitation",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "output_kind": "derived_quantity",
                    "output_id": "derived.fluid.cavitation_risk",
                    "extensions": {},
                },
            ],
            "cost_units": 1,
            "cache_policy_id": "cache.by_inputs_hash",
            "uses_rng_stream": False,
            "rng_stream_name": None,
            "version_introduced": "1.0.0",
            "deprecated": False,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "model_id": "model.fluid_leak_rate_stub",
            "model_type_id": _MODEL_LEAK,
            "description": "deterministic fluid leak-rate model",
            "supported_tiers": ["macro", "meso"],
            "input_signature": [],
            "output_signature": [
                {
                    "schema_version": "1.0.0",
                    "output_kind": "derived_quantity",
                    "output_id": "derived.fluid.leak_rate",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "output_kind": "hazard_increment",
                    "output_id": _HAZARD_LEAK,
                    "extensions": {},
                },
            ],
            "cost_units": 1,
            "cache_policy_id": "cache.by_inputs_hash",
            "uses_rng_stream": False,
            "rng_stream_name": None,
            "version_introduced": "1.0.0",
            "deprecated": False,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
    ]


def _default_model_type_registry_payload() -> dict:
    return {
        "record": {
            "model_types": [
                {
                    "schema_version": "1.0.0",
                    "model_type_id": _MODEL_PUMP,
                    "description": "fluid pump curve",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "model_type_id": _MODEL_VALVE,
                    "description": "fluid valve curve",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "model_type_id": _MODEL_PIPE,
                    "description": "fluid pipe loss",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "model_type_id": _MODEL_CAVITATION,
                    "description": "fluid cavitation hazard",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "model_type_id": _MODEL_LEAK,
                    "description": "fluid leak rate",
                    "parameter_schema_id": "dominium.schema.models.model_binding.v1",
                    "extensions": {},
                },
            ]
        }
    }


def _default_cache_policy_registry_payload() -> dict:
    return {
        "record": {
            "cache_policies": [
                {
                    "schema_version": "1.0.0",
                    "cache_policy_id": "cache.none",
                    "mode": "none",
                    "ttl_ticks": None,
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "cache_policy_id": "cache.by_inputs_hash",
                    "mode": "by_inputs_hash",
                    "ttl_ticks": 8,
                    "extensions": {},
                },
            ]
        }
    }

def _merge_model_rows(rows: object) -> Dict[str, dict]:
    merged: Dict[str, dict] = {}
    for row in normalize_constitutive_model_rows(_default_constitutive_model_rows()):
        model_id = str(row.get("model_id", "")).strip()
        if model_id:
            merged[model_id] = dict(row)
    for row in normalize_constitutive_model_rows(rows):
        model_id = str(row.get("model_id", "")).strip()
        if model_id:
            merged[model_id] = dict(row)
    return dict((key, dict(merged[key])) for key in sorted(merged.keys()))


def _merge_model_type_rows(rows: Mapping[str, dict] | None) -> Dict[str, dict]:
    defaults = model_type_rows_by_id(_default_model_type_registry_payload())
    provided = model_type_rows_by_id(rows) if isinstance(rows, Mapping) else {}
    merged = dict(defaults)
    for key in sorted(provided.keys()):
        merged[key] = dict(provided[key])
    return dict((key, dict(merged[key])) for key in sorted(merged.keys()))


def _merge_cache_policy_rows(rows: Mapping[str, dict] | None) -> Dict[str, dict]:
    defaults = cache_policy_rows_by_id(_default_cache_policy_registry_payload())
    provided = cache_policy_rows_by_id(rows) if isinstance(rows, Mapping) else {}
    merged = dict(defaults)
    for key in sorted(provided.keys()):
        merged[key] = dict(provided[key])
    return dict((key, dict(merged[key])) for key in sorted(merged.keys()))


def _fluid_profile_rows_by_id(rows: object) -> Dict[str, dict]:
    raw = rows
    if isinstance(rows, Mapping):
        raw = (dict(rows.get("record") or {})).get("fluid_profiles")
    if not isinstance(raw, list):
        raw = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in raw if isinstance(item, Mapping)), key=lambda item: str(item.get("fluid_profile_id", ""))):
        fluid_profile_id = str(row.get("fluid_profile_id", "")).strip()
        if not fluid_profile_id:
            continue
        out[fluid_profile_id] = {
            "fluid_profile_id": fluid_profile_id,
            "compressible": bool(row.get("compressible", False)),
            "density": int(max(0, _as_int(row.get("density", 0), 0))),
            "viscosity_proxy": int(max(0, _as_int(row.get("viscosity_proxy", 0), 0))),
            "vapor_pressure_proxy": int(max(0, _as_int(row.get("vapor_pressure_proxy", 0), 0))),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _base_head_for_node(*, payload: Mapping[str, object], tank_row: Mapping[str, object] | None) -> int:
    state_ref = _as_map(payload.get("state_ref"))
    base_head = int(max(0, _as_int(state_ref.get("pressure_head", state_ref.get("pressure_head_base", 0)), 0)))
    node_kind = str(payload.get("node_kind", "")).strip()
    if node_kind in {"tank", "pressure_vessel"} and isinstance(tank_row, Mapping):
        stored = int(max(0, _as_int(tank_row.get("stored_mass", 0), 0)))
        max_mass = int(max(0, _as_int(tank_row.get("max_mass", 0), 0)))
        if max_mass > 0:
            fill_permille = int((stored * 1000) // max(1, max_mass))
            head_scale = int(max(0, _as_int(state_ref.get("head_scale", state_ref.get("tank_head_scale", 80)), 80)))
            base_head += int((fill_permille * head_scale) // 1000)
    return int(max(0, base_head))


def _model_binding_rows_for_edge(
    *,
    edge_id: str,
    edge_payload: Mapping[str, object],
    from_node_payload: Mapping[str, object],
    to_node_payload: Mapping[str, object],
    upstream_head: int,
    downstream_head: int,
    available_mass: int,
    capacity_rating: int,
    fluid_profile_rows_by_id: Mapping[str, dict],
) -> List[dict]:
    model_ids = _sorted_tokens(
        list(edge_payload.get("model_bindings") or [])
        + list(from_node_payload.get("model_bindings") or [])
        + list(to_node_payload.get("model_bindings") or [])
    )
    if not model_ids:
        return []
    pump_state = _as_map(from_node_payload.get("state_ref")) if str(from_node_payload.get("node_kind", "")).strip() == "pump" else {}
    if not pump_state and str(to_node_payload.get("node_kind", "")).strip() == "pump":
        pump_state = _as_map(to_node_payload.get("state_ref"))
    valve_state = _as_map(from_node_payload.get("state_ref")) if str(from_node_payload.get("node_kind", "")).strip() == "valve" else {}
    if not valve_state and str(to_node_payload.get("node_kind", "")).strip() == "valve":
        valve_state = _as_map(to_node_payload.get("state_ref"))
    fluid_profile_id = str(from_node_payload.get("fluid_profile_id", "")).strip() or str(to_node_payload.get("fluid_profile_id", "")).strip()
    fluid_profile_row = dict(fluid_profile_rows_by_id.get(fluid_profile_id) or {})
    model_rows: List[dict] = []
    for idx, model_id in enumerate(model_ids):
        model_rows.append(
            {
                "schema_version": "1.0.0",
                "binding_id": "binding.fluid.{}.{}.{}".format(edge_id.replace(".", "_"), model_id.replace(".", "_"), str(idx)),
                "model_id": str(model_id),
                "target_kind": "edge",
                "target_id": str(edge_id),
                "tier": "meso",
                "parameters": {
                    "quantity_bundle_id": "bundle.fluid_basic",
                    "edge_id": str(edge_id),
                    "upstream_head": int(max(0, _as_int(upstream_head, 0))),
                    "downstream_head": int(max(0, _as_int(downstream_head, 0))),
                    "demand_head": int(max(0, _as_int(downstream_head, 0) - _as_int(upstream_head, 0))),
                    "mass_flow_estimate": int(max(0, min(_as_int(available_mass, 0), _as_int(capacity_rating, 0)))),
                    "capacity_rating": int(max(0, _as_int(capacity_rating, 0))),
                    "length": int(max(0, _as_int(edge_payload.get("length", 0), 0))),
                    "diameter_proxy": int(max(0, _as_int(edge_payload.get("diameter_proxy", 0), 0))),
                    "roughness_proxy": int(max(0, _as_int(edge_payload.get("roughness_proxy", 0), 0))),
                    "pump_speed_permille": int(max(0, _as_int(pump_state.get("pump_speed_permille", 1000), 1000))),
                    "base_head_gain": int(max(0, _as_int(pump_state.get("base_head_gain", 50), 50))),
                    "valve_open_permille": int(_clamp(_as_int(valve_state.get("valve_open_permille", 1000), 1000), 0, 1000)),
                    "valve_cv_permille": int(_clamp(_as_int(valve_state.get("valve_cv_permille", 1000), 1000), 0, 1000)),
                    "vapor_pressure_proxy": int(max(0, _as_int(fluid_profile_row.get("vapor_pressure_proxy", 0), 0))),
                    "local_head": int(max(0, min(_as_int(upstream_head, 0), _as_int(downstream_head, 0)))),
                    "leak_coefficient_permille": int(
                        _clamp(
                            _as_int(
                                _as_map(edge_payload.get("extensions")).get("leak_coefficient_permille", 0),
                                0,
                            ),
                            0,
                            1000,
                        )
                    ),
                },
                "enabled": True,
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        )
    return sorted(model_rows, key=lambda row: str(row.get("binding_id", "")))


def _resolve_model_input(binding_row: Mapping[str, object], input_ref: Mapping[str, object]):
    params = _as_map(binding_row.get("parameters"))
    input_id = str(input_ref.get("input_id", "")).strip()
    if input_id and input_id in params:
        return params.get(input_id)
    return 0


def _parse_fluid_model_outputs(
    *,
    current_tick: int,
    model_rows_by_id: Mapping[str, dict],
    output_actions: object,
) -> dict:
    pump_gain_by_edge: Dict[str, int] = {}
    head_loss_by_edge: Dict[str, int] = {}
    heat_loss_by_edge: Dict[str, int] = {}
    valve_limit_by_edge: Dict[str, int] = {}
    flow_delta_by_edge: Dict[str, int] = {}
    cavitation_risk_by_edge: Dict[str, int] = {}
    cavitation_delta_by_edge: Dict[str, int] = {}
    leak_rate_by_edge: Dict[str, int] = {}
    leak_delta_by_edge: Dict[str, int] = {}
    for action in sorted(
        (dict(item) for item in list(output_actions or []) if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("target_id", "")),
            str(item.get("model_id", "")),
            str(item.get("output_kind", "")),
            str(item.get("output_id", "")),
        ),
    ):
        edge_id = str(action.get("target_id", "")).strip()
        model_id = str(action.get("model_id", "")).strip()
        output_kind = str(action.get("output_kind", "")).strip()
        output_id = str(action.get("output_id", "")).strip()
        payload = _as_map(action.get("payload"))
        model_type_id = str((dict(model_rows_by_id.get(model_id) or {})).get("model_type_id", "")).strip()
        if not edge_id:
            continue
        if model_type_id == _MODEL_PUMP:
            delta = int(_as_int(payload.get("delta", payload.get("head_gain", payload.get("value", 0))), 0))
            if output_kind == "flow_adjustment":
                pump_gain_by_edge[edge_id] = int(max(0, _as_int(pump_gain_by_edge.get(edge_id, 0), 0) + max(0, delta)))
                continue
            if output_kind == "derived_quantity":
                pump_gain_by_edge[edge_id] = int(
                    max(0, _as_int(pump_gain_by_edge.get(edge_id, 0), 0) + max(0, _as_int(payload.get("head_gain", delta), delta)))
                )
                continue
        if model_type_id == _MODEL_VALVE:
            limit_permille = int(
                _clamp(
                    _as_int(
                        payload.get(
                            "flow_limit_permille",
                            payload.get("valve_open_permille", payload.get("value", 1000)),
                        ),
                        1000,
                    ),
                    0,
                    1000,
                )
            )
            prior_limit = int(_as_int(valve_limit_by_edge.get(edge_id, 1000), 1000))
            valve_limit_by_edge[edge_id] = int(min(prior_limit, limit_permille))
            if output_kind == "flow_adjustment":
                flow_delta_by_edge[edge_id] = int(_as_int(flow_delta_by_edge.get(edge_id, 0), 0) + _as_int(payload.get("delta", 0), 0))
            head_loss = int(max(0, _as_int(payload.get("head_loss", payload.get("value", 0)), 0)))
            if head_loss > 0:
                head_loss_by_edge[edge_id] = int(_as_int(head_loss_by_edge.get(edge_id, 0), 0) + head_loss)
                heat_loss_by_edge[edge_id] = int(_as_int(heat_loss_by_edge.get(edge_id, 0), 0) + head_loss)
            continue
        if model_type_id == _MODEL_PIPE:
            if output_kind == "flow_adjustment":
                delta = int(_as_int(payload.get("delta", 0), 0))
                if output_id == _Q_PRESSURE_HEAD and delta < 0:
                    loss_delta = int(abs(delta))
                    head_loss_by_edge[edge_id] = int(_as_int(head_loss_by_edge.get(edge_id, 0), 0) + loss_delta)
                    heat_loss_by_edge[edge_id] = int(_as_int(heat_loss_by_edge.get(edge_id, 0), 0) + loss_delta)
            derived_loss = int(max(0, _as_int(payload.get("head_drop", payload.get("value", 0)), 0)))
            if derived_loss > 0:
                head_loss_by_edge[edge_id] = int(_as_int(head_loss_by_edge.get(edge_id, 0), 0) + derived_loss)
                heat_loss_by_edge[edge_id] = int(_as_int(heat_loss_by_edge.get(edge_id, 0), 0) + derived_loss)
            continue
        if model_type_id == _MODEL_CAVITATION:
            risk_permille = int(_clamp(_as_int(payload.get("risk_permille", payload.get("value", 0)), 0), 0, 1000))
            cavitation_risk_by_edge[edge_id] = int(max(_as_int(cavitation_risk_by_edge.get(edge_id, 0), 0), risk_permille))
            if output_kind == "hazard_increment":
                cavitation_delta_by_edge[edge_id] = int(
                    _as_int(cavitation_delta_by_edge.get(edge_id, 0), 0) + max(0, _as_int(payload.get("delta", 0), 0))
                )
            continue
        if model_type_id == _MODEL_LEAK:
            leak_rate = int(max(0, _as_int(payload.get("leak_rate", payload.get("value", 0)), 0)))
            if leak_rate > 0:
                leak_rate_by_edge[edge_id] = int(max(_as_int(leak_rate_by_edge.get(edge_id, 0), 0), leak_rate))
            if output_kind == "hazard_increment":
                leak_delta_by_edge[edge_id] = int(
                    _as_int(leak_delta_by_edge.get(edge_id, 0), 0) + max(0, _as_int(payload.get("delta", leak_rate), leak_rate))
                )
            continue
    hazard_rows: List[dict] = []
    for edge_id in sorted(cavitation_delta_by_edge.keys()):
        delta = int(max(0, _as_int(cavitation_delta_by_edge.get(edge_id, 0), 0)))
        if delta <= 0:
            continue
        hazard_row = {
            "schema_version": "1.0.0",
            "target_id": str(edge_id),
            "hazard_type_id": _HAZARD_CAVITATION,
            "accumulated_value": int(delta),
            "last_update_tick": int(max(0, _as_int(current_tick, 0))),
            "deterministic_fingerprint": "",
            "extensions": {
                "cavitation_risk_permille": int(_as_int(cavitation_risk_by_edge.get(edge_id, 0), 0)),
            },
        }
        hazard_row["deterministic_fingerprint"] = canonical_sha256(dict(hazard_row, deterministic_fingerprint=""))
        hazard_rows.append(hazard_row)
    for edge_id in sorted(leak_delta_by_edge.keys()):
        delta = int(max(0, _as_int(leak_delta_by_edge.get(edge_id, 0), 0)))
        if delta <= 0:
            continue
        leak_hazard = {
            "schema_version": "1.0.0",
            "target_id": str(edge_id),
            "hazard_type_id": _HAZARD_LEAK,
            "accumulated_value": int(delta),
            "last_update_tick": int(max(0, _as_int(current_tick, 0))),
            "deterministic_fingerprint": "",
            "extensions": {
                "leak_rate": int(_as_int(leak_rate_by_edge.get(edge_id, 0), 0)),
            },
        }
        leak_hazard["deterministic_fingerprint"] = canonical_sha256(dict(leak_hazard, deterministic_fingerprint=""))
        hazard_rows.append(leak_hazard)
    return {
        "pump_gain_by_edge": dict((key, int(pump_gain_by_edge[key])) for key in sorted(pump_gain_by_edge.keys())),
        "head_loss_by_edge": dict((key, int(head_loss_by_edge[key])) for key in sorted(head_loss_by_edge.keys())),
        "heat_loss_by_edge": dict((key, int(heat_loss_by_edge[key])) for key in sorted(heat_loss_by_edge.keys())),
        "valve_limit_by_edge": dict((key, int(valve_limit_by_edge[key])) for key in sorted(valve_limit_by_edge.keys())),
        "flow_delta_by_edge": dict((key, int(flow_delta_by_edge[key])) for key in sorted(flow_delta_by_edge.keys())),
        "cavitation_risk_by_edge": dict((key, int(cavitation_risk_by_edge[key])) for key in sorted(cavitation_risk_by_edge.keys())),
        "leak_rate_by_edge": dict((key, int(leak_rate_by_edge[key])) for key in sorted(leak_rate_by_edge.keys())),
        "hazard_rows": sorted(hazard_rows, key=lambda row: (str(row.get("target_id", "")), str(row.get("hazard_type_id", "")))),
    }


def _energy_ledger_row_from_heat_loss(
    *,
    current_tick: int,
    graph_id: str,
    edge_id: str,
    heat_loss: int,
) -> dict:
    tick_value = int(max(0, _as_int(current_tick, 0)))
    loss_value = int(max(0, _as_int(heat_loss, 0)))
    payload = {
        "schema_version": "1.0.0",
        "entry_id": "entry.energy.fluid.{}".format(
            canonical_sha256(
                {
                    "tick": int(tick_value),
                    "graph_id": str(graph_id),
                    "edge_id": str(edge_id),
                    "heat_loss": int(loss_value),
                    "transform": "transform.kinetic_to_thermal",
                }
            )[:16]
        ),
        "tick": int(tick_value),
        "transformation_id": "transform.kinetic_to_thermal",
        "source_id": "fluid.edge.{}".format(str(edge_id)),
        "input_values": {"quantity.energy_kinetic": int(loss_value)},
        "output_values": {
            "quantity.energy_thermal": int(loss_value),
            "quantity.heat_loss": int(loss_value),
        },
        "energy_total_delta": 0,
        "deterministic_fingerprint": "",
        "extensions": {
            "domain_id": "FLUID",
            "graph_id": str(graph_id),
            "edge_id": str(edge_id),
            "reason_code": "fluid.pipe_friction_head_loss",
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _flow_transfer_event(
    *,
    current_tick: int,
    channel_id: str,
    edge_id: str,
    transferred_amount: int,
    lost_amount: int = 0,
) -> dict:
    payload = {
        "schema_version": "1.1.0",
        "event_id": "event.flow.{}".format(
            canonical_sha256(
                {
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "channel_id": str(channel_id),
                    "edge_id": str(edge_id),
                    "transferred_amount": int(max(0, _as_int(transferred_amount, 0))),
                    "lost_amount": int(max(0, _as_int(lost_amount, 0))),
                }
            )[:16]
        ),
        "tick": int(max(0, _as_int(current_tick, 0))),
        "channel_id": str(channel_id),
        "transferred_amount": int(max(0, _as_int(transferred_amount, 0))),
        "lost_amount": int(max(0, _as_int(lost_amount, 0))),
        "transferred_components": {_Q_MASS_FLOW: int(max(0, _as_int(transferred_amount, 0)))},
        "lost_components": {_Q_MASS_FLOW: int(max(0, _as_int(lost_amount, 0)))},
        "ledger_delta_refs": [
            "ledger.delta.debit.{}".format(canonical_sha256({"channel_id": channel_id, "tick": int(current_tick), "kind": "debit"})[:24]),
            "ledger.delta.credit.{}".format(canonical_sha256({"channel_id": channel_id, "tick": int(current_tick), "kind": "credit"})[:24]),
        ],
        "extensions": {"edge_id": str(edge_id), "source": "fluid_network_engine"},
    }
    if int(max(0, _as_int(lost_amount, 0))) > 0:
        payload["ledger_delta_refs"].append(
            "ledger.delta.loss.{}".format(canonical_sha256({"channel_id": channel_id, "tick": int(current_tick), "kind": "loss"})[:24])
        )
    return normalize_flow_transfer_event(payload)


def _observation_rows_for_fluid_state(*, current_tick: int, graph_id: str, node_pressure_rows: List[dict], edge_flow_rows: List[dict]) -> List[dict]:
    out: List[dict] = []
    tick = int(max(0, _as_int(current_tick, 0)))
    for row in sorted(node_pressure_rows, key=lambda item: str(item.get("node_id", ""))):
        node_id = str(row.get("node_id", "")).strip()
        if not node_id:
            continue
        out.append(
            {
                "artifact_id": "artifact.observation.fluid.head.{}".format(
                    canonical_sha256({"graph_id": graph_id, "tick": tick, "node_id": node_id})[:16]
                ),
                "artifact_family_id": "OBSERVATION",
                "extensions": {
                    "section_id": "section.fluid.node_pressures",
                    "graph_id": str(graph_id),
                    "node_id": node_id,
                    "head_value": int(max(0, _as_int(row.get("head_value", 0), 0))),
                    "tick": int(tick),
                },
            }
        )
    for row in sorted(edge_flow_rows, key=lambda item: str(item.get("edge_id", ""))):
        edge_id = str(row.get("edge_id", "")).strip()
        if not edge_id:
            continue
        out.append(
            {
                "artifact_id": "artifact.observation.fluid.flow.{}".format(
                    canonical_sha256({"graph_id": graph_id, "tick": tick, "edge_id": edge_id})[:16]
                ),
                "artifact_family_id": "OBSERVATION",
                "extensions": {
                    "section_id": "section.fluid.edge_flows",
                    "graph_id": str(graph_id),
                    "edge_id": edge_id,
                    "mass_flow": int(max(0, _as_int(row.get("mass_flow", 0), 0))),
                    "head_loss": int(max(0, _as_int(row.get("head_loss", 0), 0))),
                    "heat_loss_stub": int(max(0, _as_int(row.get("heat_loss_stub", row.get("head_loss", 0)), 0))),
                    "tick": int(tick),
                },
            }
        )
    return sorted((dict(item) for item in out), key=lambda item: str(item.get("artifact_id", "")))


def _tank_state_rows_from_map(*, tank_state_by_node_id: Mapping[str, dict], current_tick: int) -> List[dict]:
    out: List[dict] = []
    for node_id in sorted(tank_state_by_node_id.keys()):
        row = dict(tank_state_by_node_id.get(node_id) or {})
        out.append(
            build_tank_state(
                node_id=node_id,
                stored_mass=int(max(0, _as_int(row.get("stored_mass", 0), 0))),
                max_mass=int(max(0, _as_int(row.get("max_mass", 0), 0))),
                last_update_tick=int(max(0, _as_int(current_tick, 0))),
                extensions=_as_map(row.get("extensions")),
            )
        )
    return sorted(out, key=lambda row: str(row.get("node_id", "")))


def _node_pressure_rows(*, node_payloads_by_id: Mapping[str, dict], tank_state_by_node_id: Mapping[str, dict]) -> List[dict]:
    rows: List[dict] = []
    for node_id in sorted(node_payloads_by_id.keys()):
        payload = dict(node_payloads_by_id.get(node_id) or {})
        rows.append(
            {
                "node_id": str(node_id),
                "node_kind": str(payload.get("node_kind", "")),
                "head_value": int(_base_head_for_node(payload=payload, tank_row=tank_state_by_node_id.get(node_id))),
                "fluid_profile_id": str(payload.get("fluid_profile_id", "")).strip(),
            }
        )
    return sorted(rows, key=lambda row: str(row.get("node_id", "")))

def solve_fluid_network_f0(
    *,
    graph_row: Mapping[str, object],
    current_tick: int,
    tank_state_rows: object = None,
    downgrade_reason: str = "degrade.fluid.f1_disabled",
) -> dict:
    graph = normalize_network_graph(graph_row)
    graph_id = str(graph.get("graph_id", "")).strip()
    node_rows = sorted((dict(item) for item in list(graph.get("nodes") or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("node_id", "")))
    edge_rows = sorted((dict(item) for item in list(graph.get("edges") or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("edge_id", "")))
    node_payloads_by_id: Dict[str, dict] = {}
    for node in node_rows:
        node_id = str(node.get("node_id", "")).strip()
        if not node_id:
            continue
        node_payloads_by_id[node_id] = normalize_fluid_node_payload(_as_map(node.get("payload")))
    edge_payloads_by_id: Dict[str, dict] = {}
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        if not edge_id:
            continue
        edge_payloads_by_id[edge_id] = normalize_fluid_edge_payload(_as_map(edge.get("payload")))
    normalized_tank_rows = normalize_tank_state_rows(
        rows=tank_state_rows,
        current_tick=int(max(0, _as_int(current_tick, 0))),
        node_rows=node_rows,
    )
    tank_state_by_node_id = dict((str(row.get("node_id", "")).strip(), dict(row)) for row in normalized_tank_rows if str(row.get("node_id", "")).strip())
    flow_channels: List[dict] = []
    edge_flow_rows: List[dict] = []
    flow_transfer_events: List[dict] = []
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        from_node_id = str(edge.get("from_node_id", "")).strip()
        to_node_id = str(edge.get("to_node_id", "")).strip()
        if (not edge_id) or (not from_node_id) or (not to_node_id):
            continue
        edge_payload = dict(edge_payloads_by_id.get(edge_id) or {})
        capacity = int(max(0, _as_int(edge_payload.get("capacity_rating", 0), 0)))
        channel = build_fluid_flow_channel(
            graph_id=graph_id,
            edge_id=edge_id,
            source_node_id=from_node_id,
            sink_node_id=to_node_id,
            capacity_per_tick=capacity,
        )
        flow_channels.append(channel)
        source_tank = dict(tank_state_by_node_id.get(from_node_id) or {})
        sink_tank = dict(tank_state_by_node_id.get(to_node_id) or {})
        source_available = int(max(0, _as_int(source_tank.get("stored_mass", capacity), capacity)))
        sink_room = int(max(0, _as_int(sink_tank.get("max_mass", capacity), capacity) - _as_int(sink_tank.get("stored_mass", 0), 0)))
        if not sink_tank:
            sink_room = int(capacity)
        transferable = int(max(0, min(capacity, source_available, sink_room)))
        transfer = flow_transfer(
            quantity=int(transferable),
            loss_fraction=0,
            scale=1000,
            capacity_per_tick=capacity,
            delay_ticks=0,
        )
        processed = int(max(0, _as_int(transfer.get("processed_mass", 0), 0)))
        delivered = int(max(0, _as_int(transfer.get("delivered_mass", 0), 0)))
        lost = int(max(0, _as_int(transfer.get("loss_mass", 0), 0)))
        if source_tank:
            source_tank["stored_mass"] = int(max(0, _as_int(source_tank.get("stored_mass", 0), 0) - processed))
            tank_state_by_node_id[from_node_id] = source_tank
        if sink_tank:
            sink_tank["stored_mass"] = int(
                min(
                    max(0, _as_int(sink_tank.get("max_mass", 0), 0)),
                    max(0, _as_int(sink_tank.get("stored_mass", 0), 0) + delivered),
                )
            )
            tank_state_by_node_id[to_node_id] = sink_tank
        flow_transfer_events.append(
            _flow_transfer_event(
                current_tick=int(current_tick),
                channel_id=str(channel.get("channel_id", "")),
                edge_id=edge_id,
                transferred_amount=delivered,
                lost_amount=lost,
            )
        )
        edge_flow_rows.append(
            {
                "edge_id": edge_id,
                "channel_id": str(channel.get("channel_id", "")).strip(),
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
                "mass_flow": int(delivered),
                "pump_gain": 0,
                "head_loss": 0,
                "heat_loss_stub": 0,
                "valve_limit_permille": 1000,
                "cavitation_risk_permille": 0,
                "feasible": bool(delivered > 0),
                "tier": "F0",
            }
        )
    node_pressure_rows = _node_pressure_rows(
        node_payloads_by_id=node_payloads_by_id,
        tank_state_by_node_id=tank_state_by_node_id,
    )
    observation_rows = _observation_rows_for_fluid_state(
        current_tick=int(current_tick),
        graph_id=graph_id,
        node_pressure_rows=node_pressure_rows,
        edge_flow_rows=edge_flow_rows,
    )
    decision_log_rows = [
        {
            "process_id": "process.fluid_budget_degrade",
            "tick": int(max(0, _as_int(current_tick, 0))),
            "target_id": graph_id,
            "reason_code": str(downgrade_reason or "degrade.fluid.f1_disabled"),
            "details": {"mode": "F0"},
        }
    ]
    return {
        "mode": "F0",
        "graph_id": graph_id,
        "flow_channels": sorted(flow_channels, key=lambda row: str(row.get("channel_id", ""))),
        "node_pressure_rows": list(node_pressure_rows),
        "node_head_rows": list(node_pressure_rows),
        "edge_flow_rows": sorted(edge_flow_rows, key=lambda row: str(row.get("edge_id", ""))),
        "energy_transform_rows": [],
        "heat_loss_total": 0,
        "tank_state_rows": _tank_state_rows_from_map(tank_state_by_node_id=tank_state_by_node_id, current_tick=int(current_tick)),
        "pressure_vessel_state_rows": [],
        "leak_state_rows": [],
        "burst_event_rows": [],
        "relief_event_rows": [],
        "leak_event_rows": [],
        "interior_coupling_rows": [],
        "mech_coupling_rows": [],
        "flow_transfer_events": sorted(
            (dict(row) for row in flow_transfer_events if isinstance(row, Mapping)),
            key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))),
        ),
        "model_evaluation_results": [],
        "model_output_actions": [],
        "model_observation_rows": [],
        "model_cache_rows": [],
        "model_cost_units": 0,
        "model_budget_outcome": "degraded",
        "hazard_rows": [],
        "safety_event_rows": [],
        "cavitation_rows": [],
        "explain_artifact_rows": [],
        "observation_artifact_rows": observation_rows,
        "fluid_flow_hash_chain": canonical_sha256(
            [
                {"edge_id": str(row.get("edge_id", "")), "mass_flow": int(max(0, _as_int(row.get("mass_flow", 0), 0)))}
                for row in sorted(edge_flow_rows, key=lambda item: str(item.get("edge_id", "")))
            ]
        ),
        "overpressure_event_hash_chain": canonical_sha256([]),
        "relief_event_hash_chain": canonical_sha256([]),
        "leak_hash_chain": canonical_sha256([]),
        "burst_hash_chain": canonical_sha256([]),
        "decision_log_rows": decision_log_rows,
        "budget_outcome": "degraded",
        "downgrade_reason": str(downgrade_reason or "degrade.fluid.f1_disabled"),
    }


def solve_fluid_network_f1(
    *,
    graph_row: Mapping[str, object],
    current_tick: int,
    tank_state_rows: object = None,
    leak_state_rows: object = None,
    burst_event_rows: object = None,
    model_rows: object = None,
    model_type_rows: Mapping[str, dict] | None = None,
    model_cache_policy_rows: Mapping[str, dict] | None = None,
    model_cache_rows: object = None,
    fluid_profile_rows: object = None,
    failure_policy_row: Mapping[str, object] | None = None,
    explain_contract_rows: object = None,
    truth_hash_anchor: str = "",
    epistemic_policy_id: str = "epistemic.public",
    max_processed_edges: int = 4096,
    max_cost_units: int = 0,
    max_model_cost_units: int = 0,
    max_failure_events: int = 64,
    overpressure_default_rating: int = 120,
    pressure_relief_pattern_id: str = "safety.relief_pressure",
    solve_tick_stride: int = 1,
    downgrade_subgraph_modulo: int = 0,
    downgrade_subgraph_remainder: int = 0,
    defer_noncritical_model_type_ids: object = None,
    max_leak_evaluations_per_tick: int = 0,
    effect_rows: object = None,
    effect_type_registry: Mapping[str, object] | None = None,
    stacking_policy_registry: Mapping[str, object] | None = None,
) -> dict:
    graph = normalize_network_graph(graph_row)
    graph_id = str(graph.get("graph_id", "")).strip()
    tick_value = int(max(0, _as_int(current_tick, 0)))
    stride = int(max(1, _as_int(solve_tick_stride, 1)))
    if stride > 1 and (tick_value % stride) != 0:
        return solve_fluid_network_f0(
            graph_row=graph,
            current_tick=int(tick_value),
            tank_state_rows=tank_state_rows,
            downgrade_reason="degrade.fluid.tick_bucket",
        )
    subgraph_modulo = int(max(0, _as_int(downgrade_subgraph_modulo, 0)))
    if subgraph_modulo > 0:
        remainder = int(max(0, _as_int(downgrade_subgraph_remainder, 0))) % int(subgraph_modulo)
        subgraph_slot = int(int(canonical_sha256({"graph_id": graph_id, "kind": "fluid.subgraph.slot"})[:12], 16) % int(subgraph_modulo))
        if subgraph_slot == remainder:
            return solve_fluid_network_f0(
                graph_row=graph,
                current_tick=int(tick_value),
                tank_state_rows=tank_state_rows,
                downgrade_reason="degrade.fluid.subgraph_f0_budget",
            )
    node_rows = sorted((dict(item) for item in list(graph.get("nodes") or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("node_id", "")))
    edge_rows = sorted((dict(item) for item in list(graph.get("edges") or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("edge_id", "")))
    if int(max_processed_edges) <= 0 or len(edge_rows) > int(max_processed_edges):
        return solve_fluid_network_f0(
            graph_row=graph,
            current_tick=int(current_tick),
            tank_state_rows=tank_state_rows,
            downgrade_reason="degrade.fluid.f1_budget",
        )
    estimated_cost = int(len(node_rows) + (len(edge_rows) * 4))
    if int(max_cost_units) > 0 and int(estimated_cost) > int(max_cost_units):
        return solve_fluid_network_f0(
            graph_row=graph,
            current_tick=int(current_tick),
            tank_state_rows=tank_state_rows,
            downgrade_reason="degrade.fluid.f1_budget",
        )

    node_payloads_by_id: Dict[str, dict] = {}
    for node in node_rows:
        node_id = str(node.get("node_id", "")).strip()
        if not node_id:
            continue
        node_payloads_by_id[node_id] = normalize_fluid_node_payload(_as_map(node.get("payload")))
    edge_payloads_by_id: Dict[str, dict] = {}
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        if not edge_id:
            continue
        edge_payloads_by_id[edge_id] = normalize_fluid_edge_payload(_as_map(edge.get("payload")))

    normalized_tank_rows = normalize_tank_state_rows(
        rows=tank_state_rows,
        current_tick=int(max(0, _as_int(current_tick, 0))),
        node_rows=node_rows,
    )
    tank_state_by_node_id = dict((str(row.get("node_id", "")).strip(), dict(row)) for row in normalized_tank_rows if str(row.get("node_id", "")).strip())
    node_head_by_id = dict(
        (
            str(node_id),
            int(_base_head_for_node(payload=node_payloads_by_id[node_id], tank_row=tank_state_by_node_id.get(node_id))),
        )
        for node_id in sorted(node_payloads_by_id.keys())
    )
    fluid_profiles = _fluid_profile_rows_by_id(fluid_profile_rows)

    flow_channels: List[dict] = []
    binding_rows: List[dict] = []
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        from_node_id = str(edge.get("from_node_id", "")).strip()
        to_node_id = str(edge.get("to_node_id", "")).strip()
        if (not edge_id) or (not from_node_id) or (not to_node_id):
            continue
        edge_payload = dict(edge_payloads_by_id.get(edge_id) or {})
        capacity = int(max(0, _as_int(edge_payload.get("capacity_rating", 0), 0)))
        flow_channels.append(
            build_fluid_flow_channel(
                graph_id=graph_id,
                edge_id=edge_id,
                source_node_id=from_node_id,
                sink_node_id=to_node_id,
                capacity_per_tick=capacity,
            )
        )
        source_tank = dict(tank_state_by_node_id.get(from_node_id) or {})
        source_available = int(max(0, _as_int(source_tank.get("stored_mass", capacity), capacity)))
        binding_rows.extend(
            _model_binding_rows_for_edge(
                edge_id=edge_id,
                edge_payload=edge_payload,
                from_node_payload=dict(node_payloads_by_id.get(from_node_id) or {}),
                to_node_payload=dict(node_payloads_by_id.get(to_node_id) or {}),
                upstream_head=int(_as_int(node_head_by_id.get(from_node_id, 0), 0)),
                downstream_head=int(_as_int(node_head_by_id.get(to_node_id, 0), 0)),
                available_mass=int(source_available),
                capacity_rating=int(capacity),
                fluid_profile_rows_by_id=fluid_profiles,
            )
        )
    merged_model_rows = _merge_model_rows(model_rows)
    merged_model_types = _merge_model_type_rows(model_type_rows)
    merged_cache_policies = _merge_cache_policy_rows(model_cache_policy_rows)
    deferred_noncritical_types = _token_set(defer_noncritical_model_type_ids)
    deferred_binding_count = 0
    if deferred_noncritical_types and binding_rows:
        filtered_rows: List[dict] = []
        for row in sorted((dict(item) for item in binding_rows if isinstance(item, Mapping)), key=lambda item: str(item.get("binding_id", ""))):
            model_id = str(row.get("model_id", "")).strip()
            model_type_id = str((dict(merged_model_rows.get(model_id) or {})).get("model_type_id", "")).strip()
            if model_type_id and model_type_id in deferred_noncritical_types:
                deferred_binding_count += 1
                continue
            filtered_rows.append(row)
        binding_rows = [dict(row) for row in filtered_rows]
    model_cache_rows_runtime = [dict(item) for item in list(model_cache_rows or []) if isinstance(item, Mapping)]
    model_eval = {
        "evaluation_results": [],
        "output_actions": [],
        "observation_rows": [],
        "cache_rows": model_cache_rows_runtime,
        "cost_units": 0,
        "budget_outcome": "complete",
    }
    if binding_rows:
        budget = int(max_model_cost_units) if int(max_model_cost_units) > 0 else int(max_cost_units)
        if budget <= 0:
            budget = 1_000_000
        model_eval = evaluate_model_bindings(
            current_tick=int(max(0, _as_int(current_tick, 0))),
            model_rows=[dict(row) for row in merged_model_rows.values()],
            binding_rows=sorted(binding_rows, key=lambda row: str(row.get("binding_id", ""))),
            cache_rows=model_cache_rows_runtime,
            model_type_rows=merged_model_types,
            cache_policy_rows=merged_cache_policies,
            input_resolver_fn=_resolve_model_input,
            max_cost_units=budget,
            far_target_ids=[],
            far_tick_stride=1,
        )
    parsed_outputs = _parse_fluid_model_outputs(
        current_tick=int(current_tick),
        model_rows_by_id=merged_model_rows,
        output_actions=model_eval.get("output_actions"),
    )

    pump_gain_by_edge = dict(parsed_outputs.get("pump_gain_by_edge") or {})
    head_loss_by_edge = dict(parsed_outputs.get("head_loss_by_edge") or {})
    heat_loss_by_edge = dict(parsed_outputs.get("heat_loss_by_edge") or {})
    valve_limit_by_edge = dict(parsed_outputs.get("valve_limit_by_edge") or {})
    flow_delta_by_edge = dict(parsed_outputs.get("flow_delta_by_edge") or {})
    cavitation_risk_by_edge = dict(parsed_outputs.get("cavitation_risk_by_edge") or {})
    leak_rate_by_edge = dict(parsed_outputs.get("leak_rate_by_edge") or {})
    hazard_rows = [dict(row) for row in list(parsed_outputs.get("hazard_rows") or []) if isinstance(row, Mapping)]
    leak_rows_runtime = normalize_leak_state_rows(leak_state_rows)
    burst_rows_runtime = normalize_burst_event_rows(burst_event_rows)

    edge_flow_rows: List[dict] = []
    flow_transfer_events: List[dict] = []
    cavitation_rows: List[dict] = []
    leak_event_rows: List[dict] = []
    relief_event_rows: List[dict] = []
    interior_coupling_rows: List[dict] = []
    decision_log_rows: List[dict] = []
    pressure_vessel_state_rows: List[dict] = []
    explain_artifact_rows: List[dict] = []
    mech_coupling_rows: List[dict] = []
    safety_event_rows: List[dict] = []
    burst_safety_event_rows: List[dict] = []
    failure_hazard_rows: List[dict] = []
    energy_transform_rows: List[dict] = []
    if deferred_binding_count > 0:
        decision_log_rows.append(
            {
                "process_id": "process.fluid_model_binding_filter",
                "tick": int(tick_value),
                "target_id": graph_id,
                "reason_code": "degrade.fluid.defer_noncritical_models",
                "details": {
                    "deferred_binding_count": int(deferred_binding_count),
                    "deferred_model_type_ids": sorted(deferred_noncritical_types),
                },
            }
        )
    for edge in edge_rows:
        edge_id = str(edge.get("edge_id", "")).strip()
        from_node_id = str(edge.get("from_node_id", "")).strip()
        to_node_id = str(edge.get("to_node_id", "")).strip()
        if (not edge_id) or (not from_node_id) or (not to_node_id):
            continue
        edge_payload = dict(edge_payloads_by_id.get(edge_id) or {})
        base_capacity = int(max(0, _as_int(edge_payload.get("capacity_rating", 0), 0)))
        capacity_reduction_row = {"present": False, "value": 0}
        pipe_loss_increase_row = {"present": False, "value": 0}
        if effect_type_registry is not None:
            capacity_reduction_row = get_effective_modifier(
                target_id=edge_id,
                key="pipe_capacity_reduction_permille",
                effect_rows=effect_rows,
                current_tick=int(tick_value),
                effect_type_registry=effect_type_registry,
                stacking_policy_registry=stacking_policy_registry,
            )
            if (not bool(capacity_reduction_row.get("present", False))) and graph_id:
                capacity_reduction_row = get_effective_modifier(
                    target_id=graph_id,
                    key="pipe_capacity_reduction_permille",
                    effect_rows=effect_rows,
                    current_tick=int(tick_value),
                    effect_type_registry=effect_type_registry,
                    stacking_policy_registry=stacking_policy_registry,
                )
            pipe_loss_increase_row = get_effective_modifier(
                target_id=edge_id,
                key="pipe_loss_increase_permille",
                effect_rows=effect_rows,
                current_tick=int(tick_value),
                effect_type_registry=effect_type_registry,
                stacking_policy_registry=stacking_policy_registry,
            )
            if (not bool(pipe_loss_increase_row.get("present", False))) and graph_id:
                pipe_loss_increase_row = get_effective_modifier(
                    target_id=graph_id,
                    key="pipe_loss_increase_permille",
                    effect_rows=effect_rows,
                    current_tick=int(tick_value),
                    effect_type_registry=effect_type_registry,
                    stacking_policy_registry=stacking_policy_registry,
                )
        capacity_reduction_permille = int(
            _clamp(_as_int(capacity_reduction_row.get("value", 0), 0), 0, 1000)
        )
        pipe_loss_increase_permille = int(
            _clamp(_as_int(pipe_loss_increase_row.get("value", 0), 0), 0, 1000)
        )
        capacity = int((int(base_capacity) * int(max(0, 1000 - capacity_reduction_permille))) // 1000)
        upstream_head = int(max(0, _as_int(node_head_by_id.get(from_node_id, 0), 0)))
        downstream_head = int(max(0, _as_int(node_head_by_id.get(to_node_id, 0), 0)))
        pump_gain = int(max(0, _as_int(pump_gain_by_edge.get(edge_id, 0), 0)))
        head_loss_base = int(max(0, _as_int(head_loss_by_edge.get(edge_id, 0), 0)))
        head_loss = int((int(head_loss_base) * int(1000 + pipe_loss_increase_permille)) // 1000)
        heat_loss_base = int(max(0, _as_int(heat_loss_by_edge.get(edge_id, head_loss_base), head_loss_base)))
        heat_loss = int((int(heat_loss_base) * int(1000 + pipe_loss_increase_permille)) // 1000)
        valve_limit = int(_clamp(_as_int(valve_limit_by_edge.get(edge_id, 1000), 1000), 0, 1000))
        flow_delta = int(_as_int(flow_delta_by_edge.get(edge_id, 0), 0))
        source_tank = dict(tank_state_by_node_id.get(from_node_id) or {})
        sink_tank = dict(tank_state_by_node_id.get(to_node_id) or {})
        source_available = int(max(0, _as_int(source_tank.get("stored_mass", capacity), capacity)))
        sink_room = int(max(0, _as_int(sink_tank.get("max_mass", capacity), capacity) - _as_int(sink_tank.get("stored_mass", 0), 0)))
        if not sink_tank:
            sink_room = int(capacity)
        can_flow = bool(int(upstream_head + pump_gain) > int(downstream_head + head_loss))
        candidate = int(max(0, min(capacity, source_available, sink_room)))
        candidate = int((candidate * valve_limit) // 1000)
        candidate = int(max(0, candidate + flow_delta))
        mass_flow = int(min(capacity, source_available, sink_room, candidate)) if can_flow else 0
        transfer = flow_transfer(
            quantity=int(max(0, mass_flow)),
            loss_fraction=0,
            scale=1000,
            capacity_per_tick=capacity,
            delay_ticks=0,
        )
        processed = int(max(0, _as_int(transfer.get("processed_mass", 0), 0)))
        delivered = int(max(0, _as_int(transfer.get("delivered_mass", 0), 0)))
        lost = int(max(0, _as_int(transfer.get("loss_mass", 0), 0)))
        if source_tank:
            source_tank["stored_mass"] = int(max(0, _as_int(source_tank.get("stored_mass", 0), 0) - processed))
            tank_state_by_node_id[from_node_id] = source_tank
        if sink_tank:
            sink_tank["stored_mass"] = int(
                min(
                    max(0, _as_int(sink_tank.get("max_mass", 0), 0)),
                    max(0, _as_int(sink_tank.get("stored_mass", 0), 0) + delivered),
                )
            )
            tank_state_by_node_id[to_node_id] = sink_tank
        channel_id = deterministic_fluid_channel_id(graph_id=graph_id, edge_id=edge_id)
        flow_transfer_events.append(
            _flow_transfer_event(
                current_tick=int(current_tick),
                channel_id=channel_id,
                edge_id=edge_id,
                transferred_amount=delivered,
                lost_amount=lost,
            )
        )
        cavitation_risk = int(max(0, _as_int(cavitation_risk_by_edge.get(edge_id, 0), 0)))
        if cavitation_risk > 0:
            cavitation_rows.append(
                {
                    "edge_id": edge_id,
                    "cavitation_risk_permille": int(cavitation_risk),
                }
            )
        leak_rate = int(max(0, _as_int(leak_rate_by_edge.get(edge_id, 0), 0)))
        if leak_rate > 0:
            has_existing_leak = any(str(row.get("target_id", "")).strip() == edge_id for row in leak_rows_runtime)
            if not has_existing_leak:
                edge_ext = _as_map(edge_payload.get("extensions"))
                leak_start = process_start_leak(
                    leak_state_rows=leak_rows_runtime,
                    target_id=edge_id,
                    leak_rate=leak_rate,
                    current_tick=int(current_tick),
                    source_node_id=from_node_id,
                    sink_kind=str(edge_ext.get("leak_sink_kind", "external")).strip() or "external",
                    sink_id=str(edge_ext.get("leak_sink_id", "")).strip(),
                    originating_process_id="process.start_leak",
                )
                leak_rows_runtime = [dict(row) for row in list(leak_start.get("leak_state_rows") or []) if isinstance(row, Mapping)]
                leak_event_rows.extend(dict(row) for row in list(leak_start.get("leak_event_rows") or []) if isinstance(row, Mapping))
        edge_flow_rows.append(
            {
                "edge_id": edge_id,
                "channel_id": channel_id,
                "from_node_id": from_node_id,
                "to_node_id": to_node_id,
                "mass_flow": int(delivered),
                "upstream_head": int(upstream_head),
                "downstream_head": int(downstream_head),
                "pump_gain": int(pump_gain),
                "capacity_rating_base": int(base_capacity),
                "capacity_effective": int(capacity),
                "pipe_capacity_reduction_permille": int(capacity_reduction_permille),
                "head_loss_base": int(head_loss_base),
                "head_loss": int(head_loss),
                "pipe_loss_increase_permille": int(pipe_loss_increase_permille),
                "heat_loss_stub": int(heat_loss),
                "valve_limit_permille": int(valve_limit),
                "cavitation_risk_permille": int(cavitation_risk),
                "feasible": bool(can_flow and delivered > 0),
                "tier": "F1",
            }
        )
        if int(heat_loss) > 0:
            energy_transform_rows.append(
                _energy_ledger_row_from_heat_loss(
                    current_tick=int(current_tick),
                    graph_id=graph_id,
                    edge_id=edge_id,
                    heat_loss=int(heat_loss),
                )
            )

    node_pressure_rows = _node_pressure_rows(
        node_payloads_by_id=node_payloads_by_id,
        tank_state_by_node_id=tank_state_by_node_id,
    )
    failure_policy = _as_map(failure_policy_row)
    relief_preferred = bool(failure_policy.get("relief_preferred", True))
    burst_requires_threshold = bool(failure_policy.get("burst_requires_threshold", True))
    max_failure_targets = int(
        max(
            1,
            _as_int(
                failure_policy.get("max_failure_events_per_tick", max_failure_events),
                max_failure_events,
            ),
        )
    )
    failure_processed = 0
    failure_deferred = 0
    for row in list(node_pressure_rows):
        node_id = str(row.get("node_id", "")).strip()
        if not node_id:
            continue
        node_payload = dict(node_payloads_by_id.get(node_id) or {})
        state_ref = _as_map(node_payload.get("state_ref"))
        if str(node_payload.get("node_kind", "")).strip() != "pressure_vessel":
            continue
        rating = int(
            max(
                1,
                _as_int(
                    state_ref.get("vessel_rating", state_ref.get("pressure_rating", overpressure_default_rating)),
                    overpressure_default_rating,
                ),
            )
        )
        relief_threshold = int(max(1, _as_int(state_ref.get("relief_threshold", rating), rating)))
        burst_threshold = int(
            max(
                relief_threshold + 1,
                _as_int(
                    state_ref.get("burst_threshold", max(relief_threshold + 1, rating + max(1, rating // 4))),
                    max(relief_threshold + 1, rating + max(1, rating // 4)),
                ),
            )
        )
        head_value = int(max(0, _as_int(row.get("head_value", 0), 0)))
        if head_value <= relief_threshold:
            continue
        if failure_processed >= max_failure_targets:
            failure_deferred += 1
            continue
        failure_processed += 1
        overpressure_value = int(max(0, head_value - relief_threshold))
        source_tank = dict(tank_state_by_node_id.get(node_id) or {})
        source_mass = int(max(0, _as_int(source_tank.get("stored_mass", 0), 0)))
        relief_mass = int(min(source_mass, max(0, overpressure_value)))
        if relief_preferred and relief_mass > 0:
            source_tank["stored_mass"] = int(max(0, source_mass - relief_mass))
            if source_tank:
                tank_state_by_node_id[node_id] = source_tank
            relief_channel_id = "channel.fluid.relief.{}".format(canonical_sha256({"node_id": node_id})[:16])
            flow_transfer_events.append(
                _flow_transfer_event(
                    current_tick=int(current_tick),
                    channel_id=relief_channel_id,
                    edge_id="relief.{}".format(node_id),
                    transferred_amount=int(relief_mass),
                    lost_amount=0,
                )
            )
            relief_safety = build_safety_event(
                event_id="",
                tick=int(max(0, _as_int(current_tick, 0))),
                instance_id="instance.safety.pressure_relief.{}".format(node_id),
                pattern_id=str(pressure_relief_pattern_id or _PATTERN_RELIEF),
                pattern_type="relief",
                status="triggered",
                target_ids=[node_id],
                action_count=1,
                details={
                    "node_id": node_id,
                    "head_value": int(head_value),
                    "relief_threshold": int(relief_threshold),
                    "burst_threshold": int(burst_threshold),
                    "vented_mass": int(relief_mass),
                    "recommended_action": "effect.pressure_relief",
                },
                extensions={},
            )
            safety_event_rows.append(relief_safety)
            relief_event_rows.append(
                {
                    "event_id": str(relief_safety.get("event_id", "")),
                    "event_kind_id": "fluid.overpressure",
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "target_id": node_id,
                    "head_value": int(head_value),
                    "relief_threshold": int(relief_threshold),
                    "vented_mass": int(relief_mass),
                }
            )
        burst_triggered = bool(int(head_value) > int(burst_threshold)) if burst_requires_threshold else bool(int(head_value) > int(relief_threshold))
        if burst_triggered:
            burst_rate = int(max(1, overpressure_value))
            burst = process_burst_event(
                burst_event_rows=burst_rows_runtime,
                leak_state_rows=leak_rows_runtime,
                target_id=node_id,
                overpressure_value=int(max(0, head_value - burst_threshold)),
                current_tick=int(current_tick),
                source_node_id=node_id,
                sink_kind=str(state_ref.get("burst_sink_kind", "external")).strip() or "external",
                sink_id=str(state_ref.get("burst_sink_id", "")).strip(),
                leak_rate=burst_rate,
            )
            burst_rows_runtime = [dict(row) for row in list(burst.get("burst_event_rows") or []) if isinstance(row, Mapping)]
            leak_rows_runtime = [dict(row) for row in list(burst.get("leak_state_rows") or []) if isinstance(row, Mapping)]
            leak_event_rows.extend(dict(row) for row in list(burst.get("leak_event_rows") or []) if isinstance(row, Mapping))
            failure_hazard_rows.extend(dict(row) for row in list(burst.get("hazard_rows") or []) if isinstance(row, Mapping))
            burst_safety = build_safety_event(
                event_id="",
                tick=int(max(0, _as_int(current_tick, 0))),
                instance_id="instance.safety.burst_disk.{}".format(node_id),
                pattern_id=_PATTERN_BURST,
                pattern_type="burst_disk",
                status="triggered",
                target_ids=[node_id],
                action_count=1,
                details={
                    "node_id": node_id,
                    "head_value": int(head_value),
                    "burst_threshold": int(burst_threshold),
                    "recommended_action": "process.burst_event",
                },
                extensions={},
            )
            burst_safety_event_rows.append(burst_safety)
            mech_coupling_rows.append(
                {
                    "target_id": node_id,
                    "coupling_kind": "fluid_to_mech_impulse",
                    "process_id": "process.apply_impulse",
                    "impulse_vector": {"x": 0, "y": int(max(1, overpressure_value)), "z": 0},
                    "hazard_type_id": "hazard.structural_overload",
                    "tick": int(max(0, _as_int(current_tick, 0))),
                }
            )
            overload_hazard = {
                "schema_version": "1.0.0",
                "target_id": node_id,
                "hazard_type_id": "hazard.structural_overload",
                "accumulated_value": int(max(1, overpressure_value)),
                "last_update_tick": int(max(0, _as_int(current_tick, 0))),
                "deterministic_fingerprint": "",
                "extensions": {"source": "fluid.burst"},
            }
            overload_hazard["deterministic_fingerprint"] = canonical_sha256(dict(overload_hazard, deterministic_fingerprint=""))
            failure_hazard_rows.append(overload_hazard)
    if failure_deferred > 0:
        decision_log_rows.append(
            {
                "process_id": "process.fluid.failure_tick",
                "tick": int(max(0, _as_int(current_tick, 0))),
                "target_id": graph_id,
                "reason_code": "degrade.fluid.failure_budget",
                "details": {
                    "processed_count": int(failure_processed),
                    "deferred_count": int(failure_deferred),
                    "max_failure_events_per_tick": int(max_failure_targets),
                },
            }
        )

    leak_eval_cap = int(max_failure_targets)
    if int(max_leak_evaluations_per_tick) > 0:
        leak_eval_cap = int(max(1, min(int(max_failure_targets), int(_as_int(max_leak_evaluations_per_tick, max_failure_targets)))))
    leak_tick = process_leak_tick(
        current_tick=int(current_tick),
        leak_state_rows=leak_rows_runtime,
        tank_state_by_node_id=tank_state_by_node_id,
        max_processed_targets=int(leak_eval_cap),
    )
    leak_rows_runtime = [dict(row) for row in list(leak_tick.get("leak_state_rows") or []) if isinstance(row, Mapping)]
    tank_state_by_node_id = dict(leak_tick.get("tank_state_by_node_id") or {})
    flow_transfer_events.extend(dict(row) for row in list(leak_tick.get("flow_transfer_events") or []) if isinstance(row, Mapping))
    leak_event_rows.extend(dict(row) for row in list(leak_tick.get("leak_event_rows") or []) if isinstance(row, Mapping))
    interior_coupling_rows.extend(dict(row) for row in list(leak_tick.get("interior_coupling_rows") or []) if isinstance(row, Mapping))
    failure_hazard_rows.extend(dict(row) for row in list(leak_tick.get("hazard_rows") or []) if isinstance(row, Mapping))
    decision_log_rows.extend(dict(row) for row in list(leak_tick.get("decision_log_rows") or []) if isinstance(row, Mapping))

    node_pressure_rows = _node_pressure_rows(
        node_payloads_by_id=node_payloads_by_id,
        tank_state_by_node_id=tank_state_by_node_id,
    )
    for row in list(node_pressure_rows):
        node_id = str(row.get("node_id", "")).strip()
        if not node_id:
            continue
        node_payload = dict(node_payloads_by_id.get(node_id) or {})
        if str(node_payload.get("node_kind", "")).strip() != "pressure_vessel":
            continue
        pressure_vessel_state = build_pressure_vessel_state(
            node_id=node_id,
            current_head=int(max(0, _as_int(row.get("head_value", 0), 0))),
            last_update_tick=int(max(0, _as_int(current_tick, 0))),
            extensions={"graph_id": graph_id},
        )
        if pressure_vessel_state:
            pressure_vessel_state_rows.append(pressure_vessel_state)

    safety_event_rows = sorted(
        [dict(row) for row in list(safety_event_rows + burst_safety_event_rows) if isinstance(row, Mapping)],
        key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))),
    )
    hazard_rows = sorted(
        [dict(row) for row in list(hazard_rows + failure_hazard_rows) if isinstance(row, Mapping)],
        key=lambda row: (str(row.get("target_id", "")), str(row.get("hazard_type_id", ""))),
    )

    explain_contract_map: Dict[str, dict] = {}
    explain_raw = explain_contract_rows
    if isinstance(explain_contract_rows, Mapping):
        explain_raw = list((dict(explain_contract_rows.get("record") or {})).get("explain_contracts") or [])
    if isinstance(explain_raw, list):
        for row in sorted((dict(item) for item in explain_raw if isinstance(item, Mapping)), key=lambda item: str(item.get("event_kind_id", ""))):
            event_kind_id = str(row.get("event_kind_id", "")).strip()
            if event_kind_id:
                explain_contract_map[event_kind_id] = row
    explain_seed_events: List[dict] = []
    explain_seed_events.extend(
        {
            "event_id": str(row.get("event_id", "")),
            "event_kind_id": "fluid.leak",
            "target_id": str(row.get("target_id", "")),
        }
        for row in leak_event_rows
        if isinstance(row, Mapping)
    )
    explain_seed_events.extend(
        {
            "event_id": str(row.get("event_id", "")),
            "event_kind_id": "fluid.overpressure",
            "target_id": str(row.get("target_id", "")),
        }
        for row in relief_event_rows
        if isinstance(row, Mapping)
    )
    explain_seed_events.extend(
        {
            "event_id": str(row.get("event_id", "")),
            "event_kind_id": "fluid.burst",
            "target_id": str(row.get("target_id", "")),
        }
        for row in burst_rows_runtime
        if isinstance(row, Mapping)
    )
    for row in cavitation_rows:
        if not isinstance(row, Mapping):
            continue
        edge_id = str(row.get("edge_id", "")).strip()
        if not edge_id:
            continue
        explain_seed_events.append(
            {
                "event_id": _event_id("event.fluid.cavitation", {"edge_id": edge_id, "tick": int(current_tick)}),
                "event_kind_id": "fluid.cavitation",
                "target_id": edge_id,
            }
        )
    truth_anchor_token = str(truth_hash_anchor or "").strip() or canonical_sha256(
        {"graph_id": graph_id, "tick": int(max(0, _as_int(current_tick, 0))), "mode": "fluid.f1"}
    )
    for event_row in sorted(explain_seed_events, key=lambda item: (str(item.get("event_kind_id", "")), str(item.get("event_id", "")))):
        event_id = str(event_row.get("event_id", "")).strip()
        target_id = str(event_row.get("target_id", "")).strip()
        event_kind_id = str(event_row.get("event_kind_id", "")).strip()
        if (not event_id) or (not target_id) or (not event_kind_id):
            continue
        artifact = generate_explain_artifact(
            event_id=event_id,
            target_id=target_id,
            event_kind_id=event_kind_id,
            truth_hash_anchor=truth_anchor_token,
            epistemic_policy_id=str(epistemic_policy_id or "epistemic.public").strip() or "epistemic.public",
            explain_contract_row=dict(explain_contract_map.get(event_kind_id) or {}),
            decision_log_rows=decision_log_rows,
            safety_event_rows=safety_event_rows,
            hazard_rows=hazard_rows,
            compliance_rows=[],
            model_result_rows=list(model_eval.get("evaluation_results") or []),
            remediation_hint_keys=["hint.fluid.inspect_and_isolate"],
            referenced_artifacts=[event_id],
            max_items=12,
        )
        if artifact:
            explain_artifact_rows.append(dict(artifact))

    observation_rows = _observation_rows_for_fluid_state(
        current_tick=int(current_tick),
        graph_id=graph_id,
        node_pressure_rows=node_pressure_rows,
        edge_flow_rows=edge_flow_rows,
    )
    model_budget_outcome = str(model_eval.get("budget_outcome", "complete")).strip() or "complete"
    if model_budget_outcome == "degraded":
        decision_log_rows.append(
            {
                "process_id": "process.fluid_model_budget_degrade",
                "tick": int(max(0, _as_int(current_tick, 0))),
                "target_id": graph_id,
                "reason_code": "degrade.fluid.model_budget",
                "details": {"mode": "F1", "binding_count": len(binding_rows)},
            }
        )
    if int(max_leak_evaluations_per_tick) > 0 and int(leak_eval_cap) < int(max_failure_targets):
        decision_log_rows.append(
            {
                "process_id": "process.fluid_leak_eval_budget",
                "tick": int(max(0, _as_int(current_tick, 0))),
                "target_id": graph_id,
                "reason_code": "degrade.fluid.leak_eval_cap",
                "details": {
                    "configured_max_leak_evaluations_per_tick": int(max(1, _as_int(max_leak_evaluations_per_tick, 1))),
                    "effective_cap": int(leak_eval_cap),
                    "max_failure_events_per_tick": int(max_failure_targets),
                },
            }
        )
    fluid_flow_hash_chain = canonical_sha256(
        [
            {
                "edge_id": str(row.get("edge_id", "")),
                "mass_flow": int(max(0, _as_int(row.get("mass_flow", 0), 0))),
                "head_loss": int(max(0, _as_int(row.get("head_loss", 0), 0))),
            }
            for row in sorted(edge_flow_rows, key=lambda item: str(item.get("edge_id", "")))
        ]
    )
    overpressure_event_hash_chain = canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")),
                "target_ids": _sorted_tokens(row.get("target_ids")),
                "pattern_id": str(row.get("pattern_id", "")),
            }
            for row in sorted(safety_event_rows, key=lambda item: str(item.get("event_id", "")))
        ]
    )
    relief_event_hash_chain = canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")),
                "target_id": str(row.get("target_id", "")),
                "head_value": int(max(0, _as_int(row.get("head_value", 0), 0))),
            }
            for row in sorted(relief_event_rows, key=lambda item: str(item.get("event_id", "")))
        ]
    )
    leak_hash_chain = canonical_sha256(
        [
            {
                "target_id": str(row.get("target_id", "")),
                "leak_rate": int(max(0, _as_int(row.get("leak_rate", 0), 0))),
                "active": bool(row.get("active", False)),
            }
            for row in sorted(leak_rows_runtime, key=lambda item: str(item.get("target_id", "")))
        ]
    )
    burst_hash_chain = canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")),
                "target_id": str(row.get("target_id", "")),
                "overpressure_value": int(_as_int(row.get("overpressure_value", 0), 0)),
            }
            for row in sorted(burst_rows_runtime, key=lambda item: str(item.get("event_id", "")))
        ]
    )
    budget_outcome = "degraded" if model_budget_outcome == "degraded" else "complete"
    if str(leak_tick.get("budget_outcome", "complete")).strip() == "degraded":
        budget_outcome = "degraded"
    return {
        "mode": "F1",
        "graph_id": graph_id,
        "flow_channels": sorted(flow_channels, key=lambda row: str(row.get("channel_id", ""))),
        "node_pressure_rows": list(node_pressure_rows),
        "node_head_rows": list(node_pressure_rows),
        "edge_flow_rows": sorted(edge_flow_rows, key=lambda row: str(row.get("edge_id", ""))),
        "energy_transform_rows": sorted(
            (dict(row) for row in energy_transform_rows if isinstance(row, Mapping)),
            key=lambda row: (
                int(_as_int(row.get("tick", 0), 0)),
                str(row.get("transformation_id", "")),
                str(row.get("source_id", "")),
                str(row.get("entry_id", "")),
            ),
        ),
        "heat_loss_total": int(
            sum(max(0, _as_int(row.get("heat_loss_stub", 0), 0)) for row in list(edge_flow_rows or []))
        ),
        "tank_state_rows": _tank_state_rows_from_map(tank_state_by_node_id=tank_state_by_node_id, current_tick=int(current_tick)),
        "pressure_vessel_state_rows": sorted(
            (dict(row) for row in pressure_vessel_state_rows if isinstance(row, Mapping)),
            key=lambda row: str(row.get("node_id", "")),
        ),
        "leak_state_rows": sorted(
            (dict(row) for row in leak_rows_runtime if isinstance(row, Mapping)),
            key=lambda row: str(row.get("target_id", "")),
        ),
        "burst_event_rows": sorted(
            (dict(row) for row in burst_rows_runtime if isinstance(row, Mapping)),
            key=lambda row: str(row.get("event_id", "")),
        ),
        "relief_event_rows": sorted(
            (dict(row) for row in relief_event_rows if isinstance(row, Mapping)),
            key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))),
        ),
        "leak_event_rows": sorted(
            (dict(row) for row in leak_event_rows if isinstance(row, Mapping)),
            key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))),
        ),
        "interior_coupling_rows": sorted(
            (dict(row) for row in interior_coupling_rows if isinstance(row, Mapping)),
            key=lambda row: (str(row.get("compartment_id", "")), str(row.get("source_target_id", ""))),
        ),
        "mech_coupling_rows": sorted(
            (dict(row) for row in mech_coupling_rows if isinstance(row, Mapping)),
            key=lambda row: (str(row.get("target_id", "")), str(row.get("coupling_kind", ""))),
        ),
        "flow_transfer_events": sorted(
            (dict(row) for row in flow_transfer_events if isinstance(row, Mapping)),
            key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))),
        ),
        "model_evaluation_results": sorted(
            (dict(row) for row in list(model_eval.get("evaluation_results") or []) if isinstance(row, Mapping)),
            key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("result_id", ""))),
        ),
        "model_output_actions": sorted(
            (dict(row) for row in list(model_eval.get("output_actions") or []) if isinstance(row, Mapping)),
            key=lambda row: (str(row.get("target_id", "")), str(row.get("model_id", "")), str(row.get("output_id", ""))),
        ),
        "model_observation_rows": sorted(
            (dict(row) for row in list(model_eval.get("observation_rows") or []) if isinstance(row, Mapping)),
            key=lambda row: str(row.get("artifact_id", "")),
        ),
        "model_cache_rows": [dict(row) for row in list(model_eval.get("cache_rows") or []) if isinstance(row, Mapping)],
        "model_cost_units": int(max(0, _as_int(model_eval.get("cost_units", 0), 0))),
        "model_budget_outcome": model_budget_outcome,
        "hazard_rows": sorted(hazard_rows, key=lambda row: (str(row.get("target_id", "")), str(row.get("hazard_type_id", "")))),
        "safety_event_rows": sorted(safety_event_rows, key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", "")))),
        "cavitation_rows": sorted(cavitation_rows, key=lambda row: str(row.get("edge_id", ""))),
        "explain_artifact_rows": sorted(
            (dict(row) for row in explain_artifact_rows if isinstance(row, Mapping)),
            key=lambda row: str(row.get("explain_id", "")),
        ),
        "observation_artifact_rows": observation_rows,
        "fluid_flow_hash_chain": str(fluid_flow_hash_chain),
        "overpressure_event_hash_chain": str(overpressure_event_hash_chain),
        "relief_event_hash_chain": str(relief_event_hash_chain),
        "leak_hash_chain": str(leak_hash_chain),
        "burst_hash_chain": str(burst_hash_chain),
        "decision_log_rows": decision_log_rows,
        "budget_outcome": budget_outcome,
    }


__all__ = [
    "FluidError",
    "REFUSAL_FLUID_NETWORK_INVALID",
    "build_burst_event",
    "build_fluid_flow_channel",
    "build_leak_state",
    "build_pressure_vessel_state",
    "build_tank_state",
    "deterministic_fluid_channel_id",
    "normalize_burst_event_rows",
    "normalize_fluid_edge_payload",
    "normalize_fluid_node_payload",
    "normalize_leak_state_rows",
    "normalize_pressure_vessel_state_rows",
    "normalize_tank_state_rows",
    "process_burst_event",
    "process_leak_tick",
    "process_start_leak",
    "solve_fluid_network_f0",
    "solve_fluid_network_f1",
]
