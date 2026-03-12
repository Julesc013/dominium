"""LOGIC-8 deterministic fault state and application helpers."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping

from src.meta.explain import build_explain_artifact
from src.safety.safety_engine import build_safety_event
from tools.xstack.compatx.canonical_json import canonical_sha256


PROCESS_LOGIC_FAULT_SET = "process.logic_fault_set"
PROCESS_LOGIC_FAULT_CLEAR = "process.logic_fault_clear"

REFUSAL_LOGIC_FAULT_INVALID = "refusal.logic.fault_invalid"
REFUSAL_LOGIC_FAULT_SHORT_UNRESOLVED = "refusal.logic.fault_short_unresolved"

_VALID_TARGET_KINDS = {"edge", "node", "element"}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if isinstance(value, float):
        return int(round(float(value)))
    if value is None or isinstance(value, (str, int, bool)):
        return value
    return str(value)


def logic_fault_kind_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    body = _as_map(payload)
    rows = body.get("logic_fault_kinds")
    if not isinstance(rows, list):
        rows = _as_map(body.get("record")).get("logic_fault_kinds")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: _token(item.get("fault_kind_id"))):
        fault_kind_id = _token(row.get("fault_kind_id"))
        if not fault_kind_id:
            continue
        payload_row = {
            "schema_version": "1.0.0",
            "fault_kind_id": fault_kind_id,
            "description": _token(row.get("description")),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
        payload_row["deterministic_fingerprint"] = canonical_sha256(dict(payload_row, deterministic_fingerprint=""))
        out[fault_kind_id] = payload_row
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_logic_fault_state_row(
    *,
    fault_id: str,
    fault_kind_id: str,
    target_kind: str,
    target_id: str,
    active: bool,
    tick_set: int,
    parameters: Mapping[str, object] | None = None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "fault_id": _token(fault_id),
        "fault_kind_id": _token(fault_kind_id),
        "target_kind": _token(target_kind).lower(),
        "target_id": _token(target_id),
        "active": bool(active),
        "parameters": _canon(_as_map(parameters)),
        "tick_set": int(max(0, _as_int(tick_set, 0))),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    if (
        (not payload["fault_id"])
        or (not payload["fault_kind_id"])
        or (payload["target_kind"] not in _VALID_TARGET_KINDS)
        or (not payload["target_id"])
    ):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_logic_fault_state_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: (_token(item.get("fault_id")), _token(item.get("target_id")))):
        normalized = build_logic_fault_state_row(
            fault_id=_token(row.get("fault_id")),
            fault_kind_id=_token(row.get("fault_kind_id")),
            target_kind=_token(row.get("target_kind")),
            target_id=_token(row.get("target_id")),
            active=bool(row.get("active", False)),
            parameters=_as_map(row.get("parameters")),
            tick_set=_as_int(row.get("tick_set"), 0),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        fault_id = _token(normalized.get("fault_id"))
        if fault_id:
            out[fault_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def _sorted_fault_rows(rows_by_id: Mapping[str, Mapping[str, object]]) -> List[dict]:
    return [dict(rows_by_id[fault_id]) for fault_id in sorted(rows_by_id.keys(), key=str)]


def process_logic_fault_set(
    *,
    current_tick: int,
    logic_fault_state_rows: object,
    fault_request: Mapping[str, object],
    logic_fault_kind_registry_payload: Mapping[str, object] | None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    request = _as_map(fault_request)
    kinds = logic_fault_kind_rows_by_id(logic_fault_kind_registry_payload)
    fault_kind_id = _token(request.get("fault_kind_id"))
    target_kind = _token(request.get("target_kind")).lower()
    target_id = _token(request.get("target_id"))
    if fault_kind_id not in kinds or target_kind not in _VALID_TARGET_KINDS or not target_id:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_FAULT_INVALID,
            "logic_fault_state_rows": normalize_logic_fault_state_rows(logic_fault_state_rows),
        }
    fault_id = _token(request.get("fault_id")) or "fault.logic.{}".format(
        canonical_sha256(
            {
                "fault_kind_id": fault_kind_id,
                "target_kind": target_kind,
                "target_id": target_id,
            }
        )[:16]
    )
    next_rows = {
        _token(row.get("fault_id")): dict(row)
        for row in normalize_logic_fault_state_rows(logic_fault_state_rows)
    }
    row = build_logic_fault_state_row(
        fault_id=fault_id,
        fault_kind_id=fault_kind_id,
        target_kind=target_kind,
        target_id=target_id,
        active=True,
        tick_set=tick,
        parameters=_as_map(request.get("parameters")),
        extensions=_as_map(request.get("extensions")),
    )
    if not row:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_FAULT_INVALID,
            "logic_fault_state_rows": normalize_logic_fault_state_rows(logic_fault_state_rows),
        }
    next_rows[fault_id] = row
    normalized = normalize_logic_fault_state_rows(list(next_rows.values()))
    return {
        "result": "complete",
        "reason_code": "",
        "fault_state_row": row,
        "logic_fault_state_rows": normalized,
    }


def process_logic_fault_clear(
    *,
    current_tick: int,
    logic_fault_state_rows: object,
    fault_request: Mapping[str, object],
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    request = _as_map(fault_request)
    existing = {
        _token(row.get("fault_id")): dict(row)
        for row in normalize_logic_fault_state_rows(logic_fault_state_rows)
    }
    fault_id = _token(request.get("fault_id"))
    if not fault_id:
        target_kind = _token(request.get("target_kind")).lower()
        target_id = _token(request.get("target_id"))
        fault_kind_id = _token(request.get("fault_kind_id"))
        for row in _sorted_fault_rows(existing):
            if (
                _token(row.get("target_kind")).lower() == target_kind
                and _token(row.get("target_id")) == target_id
                and ((not fault_kind_id) or (_token(row.get("fault_kind_id")) == fault_kind_id))
            ):
                fault_id = _token(row.get("fault_id"))
                break
    row = dict(existing.get(fault_id) or {})
    if not row:
        return {
            "result": "refused",
            "reason_code": REFUSAL_LOGIC_FAULT_INVALID,
            "logic_fault_state_rows": _sorted_fault_rows(existing),
        }
    updated = build_logic_fault_state_row(
        fault_id=_token(row.get("fault_id")),
        fault_kind_id=_token(row.get("fault_kind_id")),
        target_kind=_token(row.get("target_kind")),
        target_id=_token(row.get("target_id")),
        active=False,
        tick_set=_as_int(row.get("tick_set"), tick),
        parameters=_as_map(row.get("parameters")),
        extensions=dict(_as_map(row.get("extensions")), tick_cleared=tick),
    )
    existing[fault_id] = updated
    normalized = normalize_logic_fault_state_rows(_sorted_fault_rows(existing))
    return {
        "result": "complete",
        "reason_code": "",
        "fault_state_row": updated,
        "logic_fault_state_rows": normalized,
    }


def select_active_logic_fault_rows(
    *,
    logic_fault_state_rows: object,
    target_refs: Iterable[tuple[str, str]],
    current_tick: int,
    field_modifier_stubs: Mapping[str, object] | None = None,
) -> List[dict]:
    del current_tick
    modifiers = _as_map(field_modifier_stubs)
    radiation_level = int(max(0, _as_int(modifiers.get("field.radiation_intensity"), 0)))
    target_keys = {
        (_token(target_kind).lower(), _token(target_id))
        for target_kind, target_id in list(target_refs or [])
        if _token(target_kind) and _token(target_id)
    }
    selected: List[dict] = []
    for row in normalize_logic_fault_state_rows(logic_fault_state_rows):
        key = (_token(row.get("target_kind")).lower(), _token(row.get("target_id")))
        if key not in target_keys:
            continue
        active = bool(row.get("active", False))
        parameters = _as_map(row.get("parameters"))
        if (not active) and radiation_level > 0:
            activation_threshold = int(max(0, _as_int(parameters.get("activation_threshold"), 0)))
            if activation_threshold > 0 and radiation_level >= activation_threshold:
                active = True
        if not active:
            continue
        selected.append(dict(row))
    return sorted(
        selected,
        key=lambda item: (
            0 if _token(item.get("target_kind")) == "edge" else 1 if _token(item.get("target_kind")) == "node" else 2,
            _token(item.get("fault_kind_id")),
            _token(item.get("fault_id")),
        ),
    )


def _default_value_ref_for_fault(*, signal_type_id: str, forced_one: bool = False) -> dict:
    signal_type = _token(signal_type_id)
    if signal_type == "signal.scalar":
        return {"value_kind": "scalar", "value_fixed": 1000 if forced_one else 0, "units_id": None}
    if signal_type == "signal.pulse":
        edges = [{"tick_offset": 0, "edge_kind": "rising"}] if forced_one else []
        return {"value_kind": "pulse", "edges": edges}
    if signal_type == "signal.bus":
        return {
            "value_kind": "bus",
            "bus_id": "bus.logic.default",
            "encoding_id": "encoding.struct",
            "width": None,
            "sub_signals": [],
            "packed_fixed": 1 if forced_one else 0,
        }
    if signal_type == "signal.message":
        return {
            "value_kind": "message",
            "artifact_id": "artifact.logic.message.null" if not forced_one else "artifact.logic.message.fault_forced",
            "receipt_id": None,
            "receipt_metadata": {},
        }
    return {"value_kind": "boolean", "value": 1 if forced_one else 0}


def _fault_explain(
    *,
    current_tick: int,
    network_id: str,
    fault_row: Mapping[str, object],
    explain_kind_id: str,
    details: Mapping[str, object] | None = None,
) -> dict:
    fault_id = _token(fault_row.get("fault_id"))
    seed = {
        "tick": int(max(0, _as_int(current_tick, 0))),
        "network_id": _token(network_id),
        "fault_id": fault_id,
        "explain_kind_id": _token(explain_kind_id),
    }
    return build_explain_artifact(
        explain_id="{}.{}".format(_token(explain_kind_id), canonical_sha256(seed)[:16]),
        event_id="event.logic.fault.{}".format(canonical_sha256(seed)[:16]),
        target_id=_token(network_id),
        cause_chain=["cause.logic.fault"],
        remediation_hints=["inspect the faulted logic path or clear the declared fault state"],
        extensions=dict(
            _canon(_as_map(details)),
            event_kind_id=_token(explain_kind_id),
            fault_id=fault_id,
            fault_kind_id=_token(fault_row.get("fault_kind_id")),
            target_kind=_token(fault_row.get("target_kind")),
            target_id=_token(fault_row.get("target_id")),
        ),
    )


def _fault_safety_event(
    *,
    current_tick: int,
    network_id: str,
    fault_row: Mapping[str, object],
    status: str,
) -> dict:
    pattern_id = "safety.fail_safe_stop"
    pattern_type = "failsafe"
    fault_kind_id = _token(fault_row.get("fault_kind_id"))
    if fault_kind_id in {"fault.open", "fault.short"}:
        pattern_id = "safety.interlock.isolate"
        pattern_type = "interlock"
    return build_safety_event(
        event_id="",
        tick=int(max(0, _as_int(current_tick, 0))),
        instance_id="instance.safety.logic.{}".format(_token(fault_row.get("fault_id")).split(".")[-1]),
        pattern_id=pattern_id,
        pattern_type=pattern_type,
        status=_token(status) or "fault_detected",
        target_ids=[_token(network_id), _token(fault_row.get("target_id"))],
        action_count=0,
        details={
            "fault_id": _token(fault_row.get("fault_id")),
            "fault_kind_id": fault_kind_id,
            "target_kind": _token(fault_row.get("target_kind")),
            "target_id": _token(fault_row.get("target_id")),
        },
        extensions={"network_id": _token(network_id)},
    )


def apply_faults_to_signal_value(
    *,
    current_tick: int,
    network_id: str,
    signal_type_id: str,
    base_value_ref: Mapping[str, object],
    active_fault_rows: object,
    allow_roi_bounce: bool = False,
) -> dict:
    value_ref = _canon(_as_map(base_value_ref))
    applied_fault_rows: List[dict] = []
    explain_artifact_rows: List[dict] = []
    safety_event_rows: List[dict] = []
    requires_l2_timing = False
    for row in select_active_logic_fault_rows(
        logic_fault_state_rows=active_fault_rows,
        target_refs=[(_token(dict(item).get("target_kind")), _token(dict(item).get("target_id"))) for item in _as_list(active_fault_rows) if isinstance(item, Mapping)],
        current_tick=current_tick,
    ):
        fault_kind_id = _token(row.get("fault_kind_id"))
        parameters = _as_map(row.get("parameters"))
        if fault_kind_id == "fault.open":
            value_ref = _default_value_ref_for_fault(signal_type_id=signal_type_id, forced_one=False)
            applied_fault_rows.append(dict(row))
            explain_artifact_rows.append(
                _fault_explain(
                    current_tick=current_tick,
                    network_id=network_id,
                    fault_row=row,
                    explain_kind_id="explain.logic_fault_open",
                )
            )
            safety_event_rows.append(
                _fault_safety_event(current_tick=current_tick, network_id=network_id, fault_row=row, status="fault_detected")
            )
            continue
        if fault_kind_id == "fault.short":
            forced_value = _as_map(parameters.get("value_ref")) or _as_map(parameters.get("value_payload"))
            resolution_mode = _token(parameters.get("resolution_mode")) or ("force_value" if forced_value else "refuse")
            if resolution_mode != "force_value":
                explain_artifact_rows.append(
                    _fault_explain(
                        current_tick=current_tick,
                        network_id=network_id,
                        fault_row=row,
                        explain_kind_id="explain.logic_fault_short",
                        details={"resolution_mode": resolution_mode},
                    )
                )
                safety_event_rows.append(
                    _fault_safety_event(current_tick=current_tick, network_id=network_id, fault_row=row, status="fault_detected")
                )
                return {
                    "result": "refused",
                    "reason_code": REFUSAL_LOGIC_FAULT_SHORT_UNRESOLVED,
                    "value_ref": value_ref,
                    "applied_fault_rows": applied_fault_rows,
                    "explain_artifact_rows": explain_artifact_rows,
                    "safety_event_rows": safety_event_rows,
                    "requires_l2_timing": False,
                }
            value_ref = _canon(forced_value)
            applied_fault_rows.append(dict(row))
            explain_artifact_rows.append(
                _fault_explain(
                    current_tick=current_tick,
                    network_id=network_id,
                    fault_row=row,
                    explain_kind_id="explain.logic_fault_short",
                    details={"resolution_mode": resolution_mode},
                )
            )
            safety_event_rows.append(
                _fault_safety_event(current_tick=current_tick, network_id=network_id, fault_row=row, status="fault_detected")
            )
            continue
        if fault_kind_id == "fault.stuck_at_0":
            value_ref = _default_value_ref_for_fault(signal_type_id=signal_type_id, forced_one=False)
            applied_fault_rows.append(dict(row))
            explain_artifact_rows.append(
                _fault_explain(current_tick=current_tick, network_id=network_id, fault_row=row, explain_kind_id="explain.logic_stuck_at")
            )
            continue
        if fault_kind_id == "fault.stuck_at_1":
            value_ref = _default_value_ref_for_fault(signal_type_id=signal_type_id, forced_one=True)
            applied_fault_rows.append(dict(row))
            explain_artifact_rows.append(
                _fault_explain(current_tick=current_tick, network_id=network_id, fault_row=row, explain_kind_id="explain.logic_stuck_at")
            )
            continue
        if fault_kind_id == "fault.threshold_drift":
            if _token(_as_map(value_ref).get("value_kind")) == "scalar":
                drift_delta = int(_as_int(parameters.get("delta_fixed"), 0))
                next_value = int(_as_int(_as_map(value_ref).get("value_fixed"), 0) + drift_delta)
                next_payload = dict(_as_map(value_ref))
                next_payload["value_fixed"] = max(0, next_value)
                value_ref = _canon(next_payload)
                applied_fault_rows.append(dict(row))
            continue
        if fault_kind_id == "fault.bounce":
            applied_fault_rows.append(dict(row))
            if allow_roi_bounce and _token(_as_map(value_ref).get("value_kind")) == "pulse":
                edges = [
                    dict(item)
                    for item in _as_list(_as_map(value_ref).get("edges"))
                    if isinstance(item, Mapping)
                ]
                edges.append({"tick_offset": 0, "edge_kind": "toggle"})
                next_payload = dict(_as_map(value_ref))
                next_payload["edges"] = sorted(edges, key=lambda item: (_as_int(item.get("tick_offset"), 0), _token(item.get("edge_kind"))))[:8]
                value_ref = _canon(next_payload)
            else:
                requires_l2_timing = True
                explain_artifact_rows.append(
                    build_explain_artifact(
                        explain_id="explain.logic_timing_violation.{}".format(
                            canonical_sha256(
                                {
                                    "tick": int(max(0, _as_int(current_tick, 0))),
                                    "network_id": _token(network_id),
                                    "fault_id": _token(row.get("fault_id")),
                                    "fault_kind_id": fault_kind_id,
                                }
                            )[:16]
                        ),
                        event_id="event.logic.timing_violation.{}".format(
                            canonical_sha256(
                                {
                                    "tick": int(max(0, _as_int(current_tick, 0))),
                                    "network_id": _token(network_id),
                                    "fault_id": _token(row.get("fault_id")),
                                    "fault_kind_id": fault_kind_id,
                                }
                            )[:16]
                        ),
                        target_id=_token(network_id),
                        cause_chain=["cause.logic.bounce_requires_roi"],
                        remediation_hints=["enable ROI micro timing for bounce inspection or clear the bounce fault"],
                        extensions={
                            "event_kind_id": "explain.logic_timing_violation",
                            "fault_id": _token(row.get("fault_id")),
                            "fault_kind_id": fault_kind_id,
                        },
                    )
                )
    return {
        "result": "complete",
        "reason_code": "",
        "value_ref": _canon(value_ref),
        "applied_fault_rows": applied_fault_rows,
        "explain_artifact_rows": explain_artifact_rows,
        "safety_event_rows": safety_event_rows,
        "requires_l2_timing": requires_l2_timing,
    }


__all__ = [
    "PROCESS_LOGIC_FAULT_CLEAR",
    "PROCESS_LOGIC_FAULT_SET",
    "REFUSAL_LOGIC_FAULT_INVALID",
    "REFUSAL_LOGIC_FAULT_SHORT_UNRESOLVED",
    "apply_faults_to_signal_value",
    "build_logic_fault_state_row",
    "logic_fault_kind_rows_by_id",
    "normalize_logic_fault_state_rows",
    "process_logic_fault_clear",
    "process_logic_fault_set",
    "select_active_logic_fault_rows",
]
