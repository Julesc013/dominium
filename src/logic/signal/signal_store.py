"""LOGIC-1 deterministic signal store and process APIs."""

from __future__ import annotations

import json
from typing import Dict, List, Mapping

from src.meta.compute import request_compute
from tools.xstack.compatx.canonical_json import canonical_sha256


PROCESS_SIGNAL_SET = "process.signal_set"
PROCESS_SIGNAL_EMIT_PULSE = "process.signal_emit_pulse"

REFUSAL_SIGNAL_INVALID = "refusal.logic.signal_invalid"
REFUSAL_SIGNAL_TYPE_UNREGISTERED = "refusal.logic.signal_type_unregistered"
REFUSAL_CARRIER_TYPE_UNREGISTERED = "refusal.logic.carrier_type_unregistered"
REFUSAL_SIGNAL_DELAY_POLICY_UNREGISTERED = "refusal.logic.signal_delay_policy_unregistered"
REFUSAL_NOISE_POLICY_UNREGISTERED = "refusal.logic.signal_noise_policy_unregistered"
REFUSAL_BUS_DEFINITION_INVALID = "refusal.logic.bus_definition_invalid"
REFUSAL_PROTOCOL_DEFINITION_INVALID = "refusal.logic.protocol_definition_invalid"

_PULSE_EDGE_KINDS = {"rising", "falling", "toggle"}


def _as_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _registry_rows_by_id(payload: Mapping[str, object] | None, list_key: str, id_key: str) -> Dict[str, dict]:
    src = _as_map(payload)
    rows = src.get(list_key)
    if not isinstance(rows, list):
        rows = _as_map(src.get("record")).get(list_key)
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: _token(item.get(id_key))):
        token = _token(row.get(id_key))
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def deterministic_signal_id(*, network_id: str, element_id: str, port_id: str, tick: int, sequence: int = 0) -> str:
    return "signal.logic.{}".format(
        canonical_sha256(
            {
                "network_id": _token(network_id),
                "element_id": _token(element_id),
                "port_id": _token(port_id),
                "tick": int(max(0, _as_int(tick, 0))),
                "sequence": int(max(0, _as_int(sequence, 0))),
            }
        )[:16]
    )


def build_bus_definition_row(
    *,
    bus_id: str,
    encoding_id: str,
    width: int | None = None,
    fields: object = None,
    extensions: Mapping[str, object] | None = None,
    deterministic_fingerprint: str = "",
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "bus_id": _token(bus_id),
        "encoding_id": _token(encoding_id),
        "width": (None if width is None else int(max(0, _as_int(width, 0))) or None),
        "fields": [
            _canon(dict(item))
            for item in sorted(
                (dict(item) for item in _as_list(fields) if isinstance(item, Mapping)),
                key=lambda item: _token(item.get("field_id")),
            )
        ],
        "extensions": _canon(_as_map(extensions)),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
    }
    if not payload["bus_id"] or not payload["encoding_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_bus_definition_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: _token(item.get("bus_id"))):
        normalized = build_bus_definition_row(
            bus_id=_token(row.get("bus_id")),
            encoding_id=_token(row.get("encoding_id")),
            width=(None if row.get("width") is None else _as_int(row.get("width"), 0)),
            fields=row.get("fields"),
            extensions=_as_map(row.get("extensions")),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
        )
        if normalized:
            out[_token(normalized.get("bus_id"))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_protocol_definition_row(
    *,
    protocol_id: str,
    bus_id: str,
    framing_rules_ref: str | None,
    arbitration_policy_id: str | None,
    addressing_mode: str | None,
    error_detection_policy_id: str | None,
    security_policy_id: str | None,
    extensions: Mapping[str, object] | None = None,
    deterministic_fingerprint: str = "",
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "protocol_id": _token(protocol_id),
        "bus_id": _token(bus_id),
        "framing_rules_ref": None if framing_rules_ref is None else _token(framing_rules_ref) or None,
        "arbitration_policy_id": None if arbitration_policy_id is None else _token(arbitration_policy_id) or None,
        "addressing_mode": _token(addressing_mode).lower() or "unicast",
        "error_detection_policy_id": None if error_detection_policy_id is None else _token(error_detection_policy_id) or None,
        "security_policy_id": None if security_policy_id is None else _token(security_policy_id) or None,
        "extensions": _canon(_as_map(extensions)),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
    }
    if not payload["protocol_id"] or not payload["bus_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_protocol_definition_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: _token(item.get("protocol_id"))):
        normalized = build_protocol_definition_row(
            protocol_id=_token(row.get("protocol_id")),
            bus_id=_token(row.get("bus_id")),
            framing_rules_ref=(None if row.get("framing_rules_ref") is None else _token(row.get("framing_rules_ref"))),
            arbitration_policy_id=(None if row.get("arbitration_policy_id") is None else _token(row.get("arbitration_policy_id"))),
            addressing_mode=(None if row.get("addressing_mode") is None else _token(row.get("addressing_mode"))),
            error_detection_policy_id=(None if row.get("error_detection_policy_id") is None else _token(row.get("error_detection_policy_id"))),
            security_policy_id=(None if row.get("security_policy_id") is None else _token(row.get("security_policy_id"))),
            extensions=_as_map(row.get("extensions")),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
        )
        if normalized:
            out[_token(normalized.get("protocol_id"))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def _slot_key(network_id: str, element_id: str, port_id: str) -> str:
    return "|".join((_token(network_id), _token(element_id), _token(port_id)))


def _slot_from_row(row: Mapping[str, object]) -> str:
    slot = _as_map(_as_map(row.get("extensions")).get("slot"))
    return _slot_key(_token(slot.get("network_id")), _token(slot.get("element_id")), _token(slot.get("port_id")))


def _build_value_ref(signal_type_id: str, value_payload: Mapping[str, object], bus_ids: set[str]) -> tuple[dict, str]:
    signal_token = _token(signal_type_id)
    kind = signal_token.split(".", 1)[1] if signal_token.startswith("signal.") else signal_token
    payload = _as_map(value_payload)
    if kind == "boolean":
        value = 1 if bool(_as_int(payload.get("value", payload.get("value_fixed", 0)), 0)) else 0
        out = {"value_kind": "boolean", "value": value, "deterministic_fingerprint": ""}
    elif kind == "scalar":
        out = {
            "value_kind": "scalar",
            "value_fixed": int(_as_int(payload.get("value_fixed", payload.get("value", 0)), 0)),
            "units_id": None if payload.get("units_id") is None else _token(payload.get("units_id")) or None,
            "deterministic_fingerprint": "",
        }
    elif kind == "pulse":
        edges = []
        raw_edges = payload.get("edges")
        if not isinstance(raw_edges, list):
            raw_edges = [{"tick_offset": int(max(0, _as_int(payload.get("tick_offset", 0), 0))), "edge_kind": _token(payload.get("edge_kind")).lower() or "rising"}]
        for edge in sorted((dict(item) for item in raw_edges if isinstance(item, Mapping)), key=lambda item: (_as_int(item.get("tick_offset", 0), 0), _token(item.get("edge_kind")))):
            edge_kind = _token(edge.get("edge_kind")).lower() or "rising"
            if edge_kind not in _PULSE_EDGE_KINDS:
                edge_kind = "rising"
            edges.append({"tick_offset": int(max(0, _as_int(edge.get("tick_offset", 0), 0))), "edge_kind": edge_kind})
        out = {"value_kind": "pulse", "edges": edges[:64], "deterministic_fingerprint": ""}
    elif kind == "message":
        artifact_id = _token(payload.get("artifact_id"))
        if not artifact_id:
            return {}, REFUSAL_SIGNAL_INVALID
        out = {
            "value_kind": "message",
            "artifact_id": artifact_id,
            "receipt_id": None if payload.get("receipt_id") is None else _token(payload.get("receipt_id")) or None,
            "receipt_metadata": _canon(_as_map(payload.get("receipt_metadata"))),
            "deterministic_fingerprint": "",
        }
    elif kind == "bus":
        bus_id = _token(payload.get("bus_id"))
        if bus_id not in bus_ids:
            return {}, REFUSAL_BUS_DEFINITION_INVALID
        out = {
            "value_kind": "bus",
            "bus_id": bus_id,
            "encoding_id": _token(payload.get("encoding_id")),
            "width": (None if payload.get("width") is None else int(max(0, _as_int(payload.get("width"), 0))) or None),
            "sub_signals": _canon(_as_list(payload.get("sub_signals"))),
            "packed_fixed": (None if payload.get("packed_fixed") is None else int(_as_int(payload.get("packed_fixed"), 0))),
            "deterministic_fingerprint": "",
        }
    else:
        return {}, REFUSAL_SIGNAL_INVALID
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out, ""


def _build_signal_row(
    *,
    signal_id: str,
    signal_type_id: str,
    carrier_type_id: str,
    value_ref: Mapping[str, object],
    valid_from_tick: int,
    valid_until_tick: int | None,
    network_id: str,
    element_id: str,
    port_id: str,
    delay_policy_id: str,
    noise_policy_id: str,
    bus_id: str | None,
    protocol_id: str | None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    ext = _as_map(extensions)
    ext["slot"] = {"network_id": _token(network_id), "element_id": _token(element_id), "port_id": _token(port_id)}
    ext["delay_policy_id"] = _token(delay_policy_id) or "delay.none"
    ext["noise_policy_id"] = _token(noise_policy_id) or "noise.none"
    ext["bus_id"] = None if bus_id is None else _token(bus_id) or None
    ext["protocol_id"] = None if protocol_id is None else _token(protocol_id) or None
    payload = {
        "schema_version": "1.0.0",
        "signal_id": _token(signal_id),
        "signal_type_id": _token(signal_type_id),
        "carrier_type_id": _token(carrier_type_id),
        "value_ref": _canon(_as_map(value_ref)),
        "valid_from_tick": int(max(0, _as_int(valid_from_tick, 0))),
        "valid_until_tick": (None if valid_until_tick is None else int(max(0, _as_int(valid_until_tick, 0)))),
        "extensions": _canon(ext),
        "deterministic_fingerprint": "",
    }
    if not payload["signal_id"] or not payload["signal_type_id"] or not payload["carrier_type_id"]:
        return {}
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_signal_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: (_as_int(item.get("valid_from_tick", 0), 0), _token(item.get("signal_id")))):
        ext = _as_map(row.get("extensions"))
        slot = _as_map(ext.get("slot"))
        normalized = _build_signal_row(
            signal_id=_token(row.get("signal_id")),
            signal_type_id=_token(row.get("signal_type_id")),
            carrier_type_id=_token(row.get("carrier_type_id")),
            value_ref=_as_map(row.get("value_ref")),
            valid_from_tick=_as_int(row.get("valid_from_tick", 0), 0),
            valid_until_tick=(None if row.get("valid_until_tick") is None else _as_int(row.get("valid_until_tick"), 0)),
            network_id=_token(slot.get("network_id")),
            element_id=_token(slot.get("element_id")),
            port_id=_token(slot.get("port_id")),
            delay_policy_id=_token(ext.get("delay_policy_id")) or "delay.none",
            noise_policy_id=_token(ext.get("noise_policy_id")) or "noise.none",
            bus_id=(None if ext.get("bus_id") is None else _token(ext.get("bus_id")) or None),
            protocol_id=(None if ext.get("protocol_id") is None else _token(ext.get("protocol_id")) or None),
            extensions=ext,
        )
        if normalized:
            out[_token(normalized.get("signal_id"))] = normalized
    return sorted(
        (dict(item) for item in out.values()),
        key=lambda item: (_as_int(item.get("valid_from_tick", 0), 0), _slot_from_row(item), _token(item.get("signal_id"))),
    )


def _tolerance_scale(tolerance_policy_registry_payload: Mapping[str, object] | None, tolerance_policy_id: str) -> int:
    rows = _registry_rows_by_id(tolerance_policy_registry_payload, "tolerance_policies", "tolerance_policy_id")
    row = dict(rows.get(_token(tolerance_policy_id)) or rows.get("tol.default") or {})
    scale = _as_int(_as_map(row.get("rounding_rules")).get("scale", 1), 1)
    return int(max(1, scale))


def signal_coupling_change_token(
    signal_row: Mapping[str, object],
    *,
    tolerance_policy_registry_payload: Mapping[str, object] | None = None,
    tolerance_policy_id: str = "tol.default",
) -> str:
    row = _as_map(signal_row)
    value_ref = _as_map(row.get("value_ref"))
    kind = _token(value_ref.get("value_kind"))
    if kind == "scalar":
        scale = _tolerance_scale(tolerance_policy_registry_payload, tolerance_policy_id)
        value_fixed = _as_int(value_ref.get("value_fixed", 0), 0)
        if value_fixed >= 0:
            quantized = int(((value_fixed + (scale // 2)) // scale) * scale)
        else:
            quantized = int(-(((-value_fixed) + (scale // 2)) // scale) * scale)
        payload = {"value_kind": kind, "value_fixed": quantized, "scale": scale}
    elif kind == "boolean":
        payload = {"value_kind": kind, "value": 1 if bool(_as_int(value_ref.get("value", 0), 0)) else 0}
    else:
        payload = {"value_kind": kind, "value_hash": canonical_sha256(value_ref)}
    payload["slot_key"] = _slot_from_row(row)
    return canonical_sha256(payload)


def _estimate_signal_compute_cost(request: Mapping[str, object], value_ref: Mapping[str, object]) -> tuple[int, int]:
    value_kind = _token(_as_map(value_ref).get("value_kind"))
    instruction_units = 8
    memory_units = 4
    if value_kind == "pulse":
        instruction_units += len(_as_list(_as_map(value_ref).get("edges"))) * 2
        memory_units += len(_as_list(_as_map(value_ref).get("edges")))
    elif value_kind == "bus":
        instruction_units += len(_as_list(_as_map(value_ref).get("sub_signals"))) * 3
        memory_units += len(_as_list(_as_map(value_ref).get("sub_signals"))) * 2
    elif value_kind == "message":
        instruction_units += 4
        memory_units += 4
    instruction_units += len(_as_list(request.get("bus_definition_rows"))) * 2
    instruction_units += len(_as_list(request.get("protocol_definition_rows"))) * 2
    return int(max(1, instruction_units)), int(max(1, memory_units))


def _coupling_change_row(
    *,
    signal_id: str,
    slot_key: str,
    tick: int,
    change_token: str,
    prior_change_token: str | None,
    tolerance_policy_id: str,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "coupling_change_id": "coupling.logic.signal.{}".format(
            canonical_sha256(
                {
                    "signal_id": signal_id,
                    "slot_key": slot_key,
                    "tick": tick,
                    "change_token": change_token,
                    "tolerance_policy_id": tolerance_policy_id,
                }
            )[:16]
        ),
        "signal_id": _token(signal_id),
        "slot_key": _token(slot_key),
        "tick": int(max(0, _as_int(tick, 0))),
        "change_token": _token(change_token),
        "prior_change_token": None if prior_change_token is None else _token(prior_change_token) or None,
        "tolerance_policy_id": _token(tolerance_policy_id) or "tol.default",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_signal_store_state(state: Mapping[str, object] | None) -> dict:
    src = _as_map(state)
    return {
        "schema_version": "1.0.0",
        "signal_rows": normalize_signal_rows(src.get("signal_rows")),
        "bus_definition_rows": normalize_bus_definition_rows(src.get("bus_definition_rows")),
        "protocol_definition_rows": normalize_protocol_definition_rows(src.get("protocol_definition_rows")),
        "signal_change_record_rows": [
            _canon(dict(item))
            for item in sorted((dict(row) for row in _as_list(src.get("signal_change_record_rows")) if isinstance(row, Mapping)), key=lambda row: (_as_int(row.get("tick", 0), 0), _token(row.get("change_id"))))
        ],
        "signal_trace_artifact_rows": [
            _canon(dict(item))
            for item in sorted((dict(row) for row in _as_list(src.get("signal_trace_artifact_rows")) if isinstance(row, Mapping)), key=lambda row: (_as_int(row.get("created_tick", 0), 0), _token(row.get("artifact_id"))))
        ],
        "coupling_change_rows": [
            _canon(dict(item))
            for item in sorted((dict(row) for row in _as_list(src.get("coupling_change_rows")) if isinstance(row, Mapping)), key=lambda row: (_as_int(row.get("tick", 0), 0), _token(row.get("coupling_change_id"))))
        ],
        "compute_runtime_state": _canon(_as_map(src.get("compute_runtime_state"))),
        "extensions": _canon(_as_map(src.get("extensions"))),
    }


def canonical_signal_snapshot(*, state: Mapping[str, object] | None, tick: int | None = None) -> dict:
    normalized = normalize_signal_store_state(state)
    active_by_slot: Dict[str, dict] = {}
    target_tick = None if tick is None else int(max(0, _as_int(tick, 0)))
    for row in normalized.get("signal_rows") or []:
        start_tick = _as_int(row.get("valid_from_tick", 0), 0)
        end_tick = row.get("valid_until_tick")
        end_value = None if end_tick is None else _as_int(end_tick, start_tick)
        if target_tick is not None and (start_tick > target_tick or (end_value is not None and target_tick >= end_value)):
            continue
        slot_key = _slot_from_row(row)
        current = dict(active_by_slot.get(slot_key) or {})
        if not current or (_as_int(current.get("valid_from_tick", 0), 0), _token(current.get("signal_id"))) <= (start_tick, _token(row.get("signal_id"))):
            active_by_slot[slot_key] = dict(row)
    return {
        "schema_version": "1.0.0",
        "tick": target_tick,
        "signals": [dict(active_by_slot[key]) for key in sorted(active_by_slot.keys())],
        "bus_definitions": normalize_bus_definition_rows(normalized.get("bus_definition_rows")),
        "protocol_definitions": normalize_protocol_definition_rows(normalized.get("protocol_definition_rows")),
    }


def canonical_signal_serialization(*, state: Mapping[str, object] | None, tick: int | None = None) -> str:
    return json.dumps(canonical_signal_snapshot(state=state, tick=tick), sort_keys=True, separators=(",", ":"))


def canonical_signal_hash(*, state: Mapping[str, object] | None, tick: int | None = None) -> str:
    return canonical_sha256(canonical_signal_snapshot(state=state, tick=tick))


def _active_signal_for_slot(signal_rows: List[dict], slot_key: str, tick: int) -> dict:
    selected = {}
    for row in signal_rows:
        if _slot_from_row(row) != slot_key:
            continue
        start_tick = _as_int(row.get("valid_from_tick", 0), 0)
        end_tick = row.get("valid_until_tick")
        end_value = None if end_tick is None else _as_int(end_tick, start_tick)
        if start_tick > tick or (end_value is not None and tick >= end_value):
            continue
        if not selected or (_as_int(selected.get("valid_from_tick", 0), 0), _token(selected.get("signal_id"))) <= (start_tick, _token(row.get("signal_id"))):
            selected = dict(row)
    return selected


def _close_prior_windows(rows: List[dict], slot_key: str, tick: int) -> List[dict]:
    updated = []
    for row in rows:
        current = dict(row)
        if _slot_from_row(current) == slot_key:
            end_tick = current.get("valid_until_tick")
            if end_tick is None or _as_int(end_tick, tick) > tick:
                current["valid_until_tick"] = int(max(_as_int(current.get("valid_from_tick", 0), 0), tick))
                current["deterministic_fingerprint"] = canonical_sha256(dict(current, deterministic_fingerprint=""))
        updated.append(current)
    return normalize_signal_rows(updated)


def _signal_change_row(signal_id: str, slot_key: str, tick: int, prior_hash: str | None, next_hash: str, process_id: str) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "change_id": "change.logic.signal.{}".format(canonical_sha256({"signal_id": signal_id, "slot_key": slot_key, "tick": tick, "process_id": process_id, "next_hash": next_hash})[:16]),
        "signal_id": signal_id,
        "slot_key": slot_key,
        "tick": int(max(0, _as_int(tick, 0))),
        "process_id": _token(process_id),
        "prior_signal_hash": None if prior_hash is None else _token(prior_hash) or None,
        "next_signal_hash": _token(next_hash),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _signal_trace_row(signal_id: str, tick: int, process_id: str, signal_hash: str, trace_kind: str, extensions: Mapping[str, object] | None = None) -> dict:
    ext = _as_map(extensions)
    ext["trace_compactable"] = True
    payload = {
        "schema_version": "1.0.0",
        "artifact_id": "artifact.logic.signal_trace.{}".format(canonical_sha256({"signal_id": signal_id, "tick": tick, "trace_kind": trace_kind, "process_id": process_id})[:16]),
        "signal_id": _token(signal_id),
        "created_tick": int(max(0, _as_int(tick, 0))),
        "trace_kind": _token(trace_kind),
        "source_process_id": _token(process_id),
        "signal_hash": _token(signal_hash),
        "extensions": _canon(ext),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def process_signal_set(
    *,
    current_tick: int,
    signal_store_state: Mapping[str, object] | None,
    signal_request: Mapping[str, object],
    signal_type_registry_payload: Mapping[str, object] | None,
    carrier_type_registry_payload: Mapping[str, object] | None,
    signal_delay_policy_registry_payload: Mapping[str, object] | None,
    signal_noise_policy_registry_payload: Mapping[str, object] | None,
    bus_encoding_registry_payload: Mapping[str, object] | None = None,
    protocol_registry_payload: Mapping[str, object] | None = None,
    compute_runtime_state: Mapping[str, object] | None = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None = None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_id: str = "compute.default",
    tolerance_policy_registry_payload: Mapping[str, object] | None = None,
    tolerance_policy_id: str = "tol.default",
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    request = _as_map(signal_request)
    state = normalize_signal_store_state(signal_store_state)
    signal_type_rows = _registry_rows_by_id(signal_type_registry_payload, "signal_types", "signal_type_id")
    carrier_type_rows = _registry_rows_by_id(carrier_type_registry_payload, "carrier_types", "carrier_type_id")
    delay_policy_rows = _registry_rows_by_id(signal_delay_policy_registry_payload, "signal_delay_policies", "delay_policy_id")
    noise_policy_rows = _registry_rows_by_id(signal_noise_policy_registry_payload, "signal_noise_policies", "noise_policy_id")
    bus_encoding_rows = _registry_rows_by_id(bus_encoding_registry_payload, "bus_encodings", "encoding_id")
    protocol_rows = _registry_rows_by_id(protocol_registry_payload, "protocols", "protocol_id")
    signal_type_id = _token(request.get("signal_type_id"))
    carrier_type_id = _token(request.get("carrier_type_id"))
    delay_policy_id = _token(request.get("delay_policy_id")) or "delay.none"
    noise_policy_id = _token(request.get("noise_policy_id")) or "noise.none"
    if signal_type_id not in signal_type_rows:
        return {"result": "refused", "reason_code": REFUSAL_SIGNAL_TYPE_UNREGISTERED, "signal_store_state": state}
    if carrier_type_id not in carrier_type_rows:
        return {"result": "refused", "reason_code": REFUSAL_CARRIER_TYPE_UNREGISTERED, "signal_store_state": state}
    if delay_policy_id not in delay_policy_rows:
        return {"result": "refused", "reason_code": REFUSAL_SIGNAL_DELAY_POLICY_UNREGISTERED, "signal_store_state": state}
    if noise_policy_id not in noise_policy_rows:
        return {"result": "refused", "reason_code": REFUSAL_NOISE_POLICY_UNREGISTERED, "signal_store_state": state}
    bus_rows = normalize_bus_definition_rows(list(state.get("bus_definition_rows") or []) + _as_list(request.get("bus_definition_rows")))
    protocol_rows_defined = normalize_protocol_definition_rows(list(state.get("protocol_definition_rows") or []) + _as_list(request.get("protocol_definition_rows")))
    bus_ids = set(_token(row.get("bus_id")) for row in bus_rows)
    protocol_ids = set(_token(row.get("protocol_id")) for row in protocol_rows_defined)
    bus_id = None if request.get("bus_id") is None else _token(request.get("bus_id")) or None
    protocol_id = None if request.get("protocol_id") is None else _token(request.get("protocol_id")) or None
    if bus_id is not None and bus_id not in bus_ids:
        return {"result": "refused", "reason_code": REFUSAL_BUS_DEFINITION_INVALID, "signal_store_state": state}
    if bus_id is not None:
        bus_row = dict(next((row for row in bus_rows if _token(row.get("bus_id")) == bus_id), {}))
        if _token(bus_row.get("encoding_id")) not in bus_encoding_rows:
            return {"result": "refused", "reason_code": REFUSAL_BUS_DEFINITION_INVALID, "signal_store_state": state}
    if protocol_id is not None and (protocol_id not in protocol_ids or protocol_id not in protocol_rows):
        return {"result": "refused", "reason_code": REFUSAL_PROTOCOL_DEFINITION_INVALID, "signal_store_state": state}
    network_id = _token(request.get("network_id"))
    element_id = _token(request.get("element_id"))
    port_id = _token(request.get("port_id"))
    if not network_id or not element_id or not port_id:
        return {"result": "refused", "reason_code": REFUSAL_SIGNAL_INVALID, "signal_store_state": state}
    value_ref, value_reason = _build_value_ref(signal_type_id, _as_map(request.get("value_payload")), bus_ids)
    if value_reason:
        return {"result": "refused", "reason_code": value_reason, "signal_store_state": state}
    compute_request = request_compute(
        current_tick=tick,
        owner_kind="process",
        owner_id=_token(request.get("compute_owner_id")) or PROCESS_SIGNAL_SET,
        instruction_units=_estimate_signal_compute_cost(request, value_ref)[0],
        memory_units=_estimate_signal_compute_cost(request, value_ref)[1],
        compute_runtime_state=(compute_runtime_state if isinstance(compute_runtime_state, Mapping) else _as_map(state.get("compute_runtime_state"))),
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_budget_profile_id=_token(request.get("compute_profile_id")) or _token(compute_budget_profile_id) or "compute.default",
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
    )
    if str(compute_request.get("result", "")) not in {"complete", "throttled"}:
        state["compute_runtime_state"] = _as_map(compute_request.get("runtime_state"))
        return {
            "result": str(compute_request.get("result", "")) or "refused",
            "reason_code": str(compute_request.get("reason_code", "")) or REFUSAL_SIGNAL_INVALID,
            "compute_request": dict(compute_request),
            "signal_store_state": normalize_signal_store_state(state),
        }
    slot_key = _slot_key(network_id, element_id, port_id)
    signal_rows = _close_prior_windows(list(state.get("signal_rows") or []), slot_key, tick)
    sequence = len([row for row in signal_rows if _slot_from_row(row) == slot_key and _as_int(row.get("valid_from_tick", 0), 0) == tick])
    signal_id = _token(request.get("signal_id")) or deterministic_signal_id(
        network_id=network_id,
        element_id=element_id,
        port_id=port_id,
        tick=tick,
        sequence=sequence,
    )
    prior_row = _active_signal_for_slot(signal_rows, slot_key, tick)
    new_row = _build_signal_row(
        signal_id=signal_id,
        signal_type_id=signal_type_id,
        carrier_type_id=carrier_type_id,
        value_ref=value_ref,
        valid_from_tick=tick,
        valid_until_tick=(None if request.get("valid_until_tick") is None else _as_int(request.get("valid_until_tick"), tick)),
        network_id=network_id,
        element_id=element_id,
        port_id=port_id,
        delay_policy_id=delay_policy_id,
        noise_policy_id=noise_policy_id,
        bus_id=bus_id,
        protocol_id=protocol_id,
        extensions=_as_map(request.get("extensions")),
    )
    signal_rows = normalize_signal_rows(signal_rows + [new_row])
    prior_hash = None if not prior_row else canonical_sha256(prior_row)
    next_hash = canonical_sha256(new_row)
    prior_change_token = None if not prior_row else signal_coupling_change_token(
        prior_row,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        tolerance_policy_id=_token(request.get("tolerance_policy_id")) or _token(tolerance_policy_id) or "tol.default",
    )
    next_change_token = signal_coupling_change_token(
        new_row,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        tolerance_policy_id=_token(request.get("tolerance_policy_id")) or _token(tolerance_policy_id) or "tol.default",
    )
    state["signal_rows"] = signal_rows
    state["bus_definition_rows"] = bus_rows
    state["protocol_definition_rows"] = protocol_rows_defined
    state["compute_runtime_state"] = _as_map(compute_request.get("runtime_state"))
    state["signal_change_record_rows"] = list(state.get("signal_change_record_rows") or []) + [
        _signal_change_row(signal_id, slot_key, tick, prior_hash, next_hash, PROCESS_SIGNAL_SET)
    ]
    state["signal_trace_artifact_rows"] = list(state.get("signal_trace_artifact_rows") or []) + [
        _signal_trace_row(signal_id, tick, PROCESS_SIGNAL_SET, next_hash, "trace.signal_snapshot", {"slot_key": slot_key})
    ]
    if prior_change_token != next_change_token:
        state["coupling_change_rows"] = list(state.get("coupling_change_rows") or []) + [
            _coupling_change_row(
                signal_id=signal_id,
                slot_key=slot_key,
                tick=tick,
                change_token=next_change_token,
                prior_change_token=prior_change_token,
                tolerance_policy_id=_token(request.get("tolerance_policy_id")) or _token(tolerance_policy_id) or "tol.default",
            )
        ]
    state = normalize_signal_store_state(state)
    return {
        "result": "complete",
        "reason_code": "",
        "signal_row": dict(new_row),
        "signal_rows": list(state.get("signal_rows") or []),
        "bus_definition_rows": list(state.get("bus_definition_rows") or []),
        "protocol_definition_rows": list(state.get("protocol_definition_rows") or []),
        "signal_change_record_rows": list(state.get("signal_change_record_rows") or []),
        "signal_trace_artifact_rows": list(state.get("signal_trace_artifact_rows") or []),
        "coupling_change_rows": list(state.get("coupling_change_rows") or []),
        "compute_request": dict(compute_request),
        "signal_store_state": state,
    }


def process_signal_emit_pulse(
    *,
    current_tick: int,
    signal_store_state: Mapping[str, object] | None,
    pulse_request: Mapping[str, object],
    signal_type_registry_payload: Mapping[str, object] | None,
    carrier_type_registry_payload: Mapping[str, object] | None,
    signal_delay_policy_registry_payload: Mapping[str, object] | None,
    signal_noise_policy_registry_payload: Mapping[str, object] | None,
    bus_encoding_registry_payload: Mapping[str, object] | None = None,
    protocol_registry_payload: Mapping[str, object] | None = None,
    compute_runtime_state: Mapping[str, object] | None = None,
    compute_budget_profile_registry_payload: Mapping[str, object] | None = None,
    compute_degrade_policy_registry_payload: Mapping[str, object] | None = None,
    compute_budget_profile_id: str = "compute.default",
    tolerance_policy_registry_payload: Mapping[str, object] | None = None,
    tolerance_policy_id: str = "tol.default",
) -> dict:
    request = dict(_as_map(pulse_request))
    request["signal_type_id"] = "signal.pulse"
    if not _as_map(request.get("value_payload")):
        request["value_payload"] = {
            "edges": [
                {
                    "tick_offset": int(max(0, _as_int(request.get("tick_offset", 0), 0))),
                    "edge_kind": _token(request.get("edge_kind")).lower() or "rising",
                }
            ]
        }
    result = process_signal_set(
        current_tick=current_tick,
        signal_store_state=signal_store_state,
        signal_request=request,
        signal_type_registry_payload=signal_type_registry_payload,
        carrier_type_registry_payload=carrier_type_registry_payload,
        signal_delay_policy_registry_payload=signal_delay_policy_registry_payload,
        signal_noise_policy_registry_payload=signal_noise_policy_registry_payload,
        bus_encoding_registry_payload=bus_encoding_registry_payload,
        protocol_registry_payload=protocol_registry_payload,
        compute_runtime_state=compute_runtime_state,
        compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
        compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
        compute_budget_profile_id=compute_budget_profile_id,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        tolerance_policy_id=tolerance_policy_id,
    )
    if str(result.get("result", "")) != "complete":
        return result
    state = normalize_signal_store_state(result.get("signal_store_state"))
    signal_row = dict(result.get("signal_row") or {})
    state["signal_trace_artifact_rows"] = list(state.get("signal_trace_artifact_rows") or []) + [
        _signal_trace_row(
            _token(signal_row.get("signal_id")),
            int(max(0, _as_int(current_tick, 0))),
            PROCESS_SIGNAL_EMIT_PULSE,
            canonical_sha256(signal_row),
            "trace.signal_pulse_emit",
            {"edges": _as_list(_as_map(signal_row.get("value_ref")).get("edges"))},
        )
    ]
    state = normalize_signal_store_state(state)
    result["signal_trace_artifact_rows"] = list(state.get("signal_trace_artifact_rows") or [])
    result["signal_store_state"] = state
    return result


__all__ = [
    "PROCESS_SIGNAL_EMIT_PULSE",
    "PROCESS_SIGNAL_SET",
    "REFUSAL_BUS_DEFINITION_INVALID",
    "REFUSAL_CARRIER_TYPE_UNREGISTERED",
    "REFUSAL_NOISE_POLICY_UNREGISTERED",
    "REFUSAL_PROTOCOL_DEFINITION_INVALID",
    "REFUSAL_SIGNAL_DELAY_POLICY_UNREGISTERED",
    "REFUSAL_SIGNAL_INVALID",
    "REFUSAL_SIGNAL_TYPE_UNREGISTERED",
    "build_bus_definition_row",
    "build_protocol_definition_row",
    "canonical_signal_hash",
    "canonical_signal_serialization",
    "canonical_signal_snapshot",
    "deterministic_signal_id",
    "normalize_bus_definition_rows",
    "normalize_protocol_definition_rows",
    "normalize_signal_rows",
    "normalize_signal_store_state",
    "process_signal_emit_pulse",
    "process_signal_set",
    "signal_coupling_change_token",
]
