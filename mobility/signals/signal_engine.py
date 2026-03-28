"""Deterministic MOB-8 signaling and interlocking helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from core.state.state_machine_engine import normalize_state_machine
from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_MOBILITY_SIGNAL_VIOLATION = "refusal.mob.signal_violation"
REFUSAL_MOBILITY_SIGNAL_INVALID = "refusal.mob.network_invalid"

_VALID_SIGNAL_ASPECTS = {"stop", "caution", "clear"}
_VALID_BLOCK_RESERVATION_STATUS = {"pending", "active", "released", "expired", "conflict"}
_VALID_SWITCH_LOCK_STATUS = {"locked", "unlocked"}


class SignalEngineError(ValueError):
    """Deterministic signaling/interlocking refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code or REFUSAL_MOBILITY_SIGNAL_INVALID)
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


def _normalize_signal_aspect(value: object) -> str:
    token = str(value or "").strip().lower()
    if token in _VALID_SIGNAL_ASPECTS:
        return token
    return "stop"


def _normalize_attached_to(value: object) -> dict:
    if isinstance(value, Mapping):
        payload = dict(value or {})
        edge_id = str(payload.get("edge_id", "")).strip()
        node_id = str(payload.get("node_id", "")).strip()
    else:
        token = str(value or "").strip()
        edge_id = token if token.startswith("edge.") else ""
        node_id = token if token.startswith("node.") else ""
    if bool(edge_id) == bool(node_id):
        raise SignalEngineError(
            REFUSAL_MOBILITY_SIGNAL_INVALID,
            "attached_to must declare exactly one of edge_id or node_id",
            {"attached_to": value},
        )
    if edge_id:
        return {"edge_id": edge_id}
    return {"node_id": node_id}


def signal_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("signal_types")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("signal_types")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("signal_type_id", ""))):
        signal_type_id = str(row.get("signal_type_id", "")).strip()
        if not signal_type_id:
            continue
        out[signal_type_id] = {
            "schema_version": "1.0.0",
            "signal_type_id": signal_type_id,
            "schema_ref": str(row.get("schema_ref", "")).strip(),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def signal_rule_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("signal_rule_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("signal_rule_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("rule_policy_id", ""))):
        rule_policy_id = str(row.get("rule_policy_id", "")).strip()
        if not rule_policy_id:
            continue
        ext = _as_map(row.get("extensions"))
        aspects = [_normalize_signal_aspect(item) for item in list(ext.get("aspects") or [])]
        aspects = [item for item in aspects if item in _VALID_SIGNAL_ASPECTS]
        if not aspects:
            aspects = ["stop", "caution", "clear"]
        out[rule_policy_id] = {
            "schema_version": "1.0.0",
            "rule_policy_id": rule_policy_id,
            "description": str(ext.get("description", "")).strip() or "signal rule policy",
            "aspects": list(dict.fromkeys(aspects)),
            "transition_rules": [
                dict(item)
                for item in sorted(
                    (dict(item) for item in list(ext.get("transition_rules") or []) if isinstance(item, Mapping)),
                    key=lambda item: (str(item.get("rule_id", "")), str(item.get("when", ""))),
                )
            ],
            "interlocking_rules": [
                dict(item)
                for item in sorted(
                    (dict(item) for item in list(ext.get("interlocking_rules") or []) if isinstance(item, Mapping)),
                    key=lambda item: str(item.get("rule_id", "")),
                )
            ],
            "extensions": _canon(ext),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def deterministic_signal_id(
    *,
    attached_to: Mapping[str, object],
    signal_type_id: str,
    rule_policy_id: str,
) -> str:
    digest = canonical_sha256(
        {
            "attached_to": _canon(_normalize_attached_to(attached_to)),
            "signal_type_id": str(signal_type_id or "").strip(),
            "rule_policy_id": str(rule_policy_id or "").strip(),
        }
    )
    return "signal.mob.{}".format(digest[:16])


def deterministic_block_reservation_id(
    *,
    vehicle_id: str,
    edge_id: str,
    start_tick: int,
    end_tick: int,
) -> str:
    digest = canonical_sha256(
        {
            "vehicle_id": str(vehicle_id or "").strip(),
            "edge_id": str(edge_id or "").strip(),
            "start_tick": int(max(0, _as_int(start_tick, 0))),
            "end_tick": int(max(0, _as_int(end_tick, 0))),
        }
    )
    return "block_reservation.mob.{}".format(digest[:16])


def deterministic_switch_lock_id(*, machine_id: str, switch_node_id: str) -> str:
    digest = canonical_sha256(
        {
            "machine_id": str(machine_id or "").strip(),
            "switch_node_id": str(switch_node_id or "").strip(),
        }
    )
    return "switch_lock.mob.{}".format(digest[:16])


def build_signal(
    *,
    signal_id: str,
    attached_to: Mapping[str, object],
    signal_type_id: str,
    state_machine_id: str,
    rule_policy_id: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    attached = _normalize_attached_to(attached_to)
    payload = {
        "schema_version": "1.0.0",
        "signal_id": str(signal_id or "").strip(),
        "attached_to": attached,
        "signal_type_id": str(signal_type_id or "").strip(),
        "state_machine_id": str(state_machine_id or "").strip(),
        "rule_policy_id": str(rule_policy_id or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if not payload["signal_id"]:
        raise SignalEngineError(REFUSAL_MOBILITY_SIGNAL_INVALID, "signal_id is required", {})
    if not payload["signal_type_id"] or not payload["state_machine_id"] or not payload["rule_policy_id"]:
        raise SignalEngineError(
            REFUSAL_MOBILITY_SIGNAL_INVALID,
            "signal_type_id, state_machine_id, and rule_policy_id are required",
            {
                "signal_id": payload["signal_id"],
                "signal_type_id": payload["signal_type_id"],
                "state_machine_id": payload["state_machine_id"],
                "rule_policy_id": payload["rule_policy_id"],
            },
        )
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_signal_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("signal_id", ""))):
        signal_id = str(row.get("signal_id", "")).strip()
        if not signal_id:
            continue
        try:
            out[signal_id] = build_signal(
                signal_id=signal_id,
                attached_to=row.get("attached_to"),
                signal_type_id=str(row.get("signal_type_id", "")).strip(),
                state_machine_id=str(row.get("state_machine_id", "")).strip(),
                rule_policy_id=str(row.get("rule_policy_id", "")).strip(),
                extensions=_as_map(row.get("extensions")),
            )
        except SignalEngineError:
            continue
    return [dict(out[key]) for key in sorted(out.keys())]


def build_block_reservation(
    *,
    reservation_id: str,
    vehicle_id: str,
    edge_id: str,
    start_tick: int,
    end_tick: int,
    status: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    start_value = int(max(0, _as_int(start_tick, 0)))
    end_value = int(max(start_value, _as_int(end_tick, start_value)))
    status_token = str(status or "").strip().lower()
    if status_token not in _VALID_BLOCK_RESERVATION_STATUS:
        status_token = "pending"
    payload = {
        "schema_version": "1.0.0",
        "reservation_id": str(reservation_id or "").strip(),
        "vehicle_id": str(vehicle_id or "").strip(),
        "edge_id": str(edge_id or "").strip(),
        "start_tick": int(start_value),
        "end_tick": int(end_value),
        "status": status_token,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if not payload["reservation_id"] or not payload["vehicle_id"] or not payload["edge_id"]:
        raise SignalEngineError(
            REFUSAL_MOBILITY_SIGNAL_INVALID,
            "block reservation requires reservation_id, vehicle_id, and edge_id",
            dict(payload),
        )
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_block_reservation_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("reservation_id", ""))):
        reservation_id = str(row.get("reservation_id", "")).strip()
        if not reservation_id:
            continue
        try:
            out[reservation_id] = build_block_reservation(
                reservation_id=reservation_id,
                vehicle_id=str(row.get("vehicle_id", "")).strip(),
                edge_id=str(row.get("edge_id", "")).strip(),
                start_tick=_as_int(row.get("start_tick", 0), 0),
                end_tick=_as_int(row.get("end_tick", row.get("start_tick", 0)), 0),
                status=str(row.get("status", "pending")).strip() or "pending",
                extensions=_as_map(row.get("extensions")),
            )
        except SignalEngineError:
            continue
    return [dict(out[key]) for key in sorted(out.keys())]


def build_switch_lock(
    *,
    switch_lock_id: str,
    machine_id: str,
    switch_node_id: str,
    status: str,
    locked_tick: int,
    reason_code: str | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    status_token = str(status or "").strip().lower()
    if status_token not in _VALID_SWITCH_LOCK_STATUS:
        status_token = "locked"
    payload = {
        "schema_version": "1.0.0",
        "switch_lock_id": str(switch_lock_id or "").strip(),
        "machine_id": str(machine_id or "").strip(),
        "switch_node_id": str(switch_node_id or "").strip(),
        "status": status_token,
        "locked_tick": int(max(0, _as_int(locked_tick, 0))),
        "reason_code": None if reason_code is None else str(reason_code).strip() or None,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if not payload["switch_lock_id"] or not payload["machine_id"]:
        raise SignalEngineError(REFUSAL_MOBILITY_SIGNAL_INVALID, "switch lock requires switch_lock_id and machine_id", payload)
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_switch_lock_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("switch_lock_id", ""))):
        switch_lock_id = str(row.get("switch_lock_id", "")).strip()
        if not switch_lock_id:
            continue
        try:
            out[switch_lock_id] = build_switch_lock(
                switch_lock_id=switch_lock_id,
                machine_id=str(row.get("machine_id", "")).strip(),
                switch_node_id=str(row.get("switch_node_id", "")).strip(),
                status=str(row.get("status", "locked")).strip(),
                locked_tick=_as_int(row.get("locked_tick", 0), 0),
                reason_code=(None if row.get("reason_code") is None else str(row.get("reason_code", "")).strip() or None),
                extensions=_as_map(row.get("extensions")),
            )
        except SignalEngineError:
            continue
    return [dict(out[key]) for key in sorted(out.keys())]


def switch_lock_rows_by_machine_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_switch_lock_rows(rows):
        machine_id = str(row.get("machine_id", "")).strip()
        if machine_id:
            out[machine_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _is_reservation_active(row: Mapping[str, object], current_tick: int) -> bool:
    status = str(row.get("status", "")).strip().lower()
    if status not in {"pending", "active"}:
        return False
    start_tick = int(max(0, _as_int(row.get("start_tick", 0), 0)))
    end_tick = int(max(start_tick, _as_int(row.get("end_tick", start_tick), start_tick)))
    tick = int(max(0, _as_int(current_tick, 0)))
    return start_tick <= tick <= end_tick


def active_block_reservation_rows(rows: object, *, current_tick: int) -> List[dict]:
    return [
        dict(row)
        for row in normalize_block_reservation_rows(rows)
        if _is_reservation_active(row, current_tick=int(current_tick))
    ]


def _signal_aspects_for_policy(policy_row: Mapping[str, object] | None) -> List[str]:
    policy = _as_map(policy_row)
    aspects = [_normalize_signal_aspect(item) for item in list(policy.get("aspects") or [])]
    aspects = [item for item in aspects if item in _VALID_SIGNAL_ASPECTS]
    if not aspects:
        aspects = ["stop", "caution", "clear"]
    return list(dict.fromkeys(aspects))


def build_signal_state_machine(
    *,
    signal_id: str,
    state_machine_id: str,
    aspects: List[str],
    initial_aspect: str = "stop",
) -> dict:
    normalized_aspects = [_normalize_signal_aspect(item) for item in list(aspects or [])]
    normalized_aspects = [item for item in normalized_aspects if item in _VALID_SIGNAL_ASPECTS]
    if not normalized_aspects:
        normalized_aspects = ["stop", "caution", "clear"]
    initial = _normalize_signal_aspect(initial_aspect)
    if initial not in set(normalized_aspects):
        initial = normalized_aspects[0]
    transition_rows = []
    for from_state in sorted(normalized_aspects):
        for to_state in sorted(normalized_aspects):
            transition_rows.append(
                {
                    "schema_version": "1.0.0",
                    "transition_id": "transition.mob.signal.{}".format(
                        canonical_sha256(
                            {
                                "machine_id": str(state_machine_id or "").strip(),
                                "from_state": from_state,
                                "to_state": to_state,
                            }
                        )[:16]
                    ),
                    "from_state": from_state,
                    "to_state": to_state,
                    "trigger_process_id": "process.signal_set_aspect",
                    "guard_conditions": {},
                    "priority": 0,
                    "extensions": {"signal_id": str(signal_id or "").strip()},
                }
            )
    return normalize_state_machine(
        {
            "schema_version": "1.0.0",
            "machine_id": str(state_machine_id or "").strip(),
            "machine_type_id": "state_machine.mobility.signal",
            "state_id": initial,
            "transitions": [str(item.get("transition_id", "")).strip() for item in transition_rows],
            "transition_rows": transition_rows,
            "extensions": {
                "signal_id": str(signal_id or "").strip(),
                "aspects": sorted(normalized_aspects),
            },
        }
    )


def signal_state_machine_rows_by_id(rows: object) -> Dict[str, dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("machine_id", ""))):
        machine_id = str(row.get("machine_id", "")).strip()
        if not machine_id:
            continue
        try:
            out[machine_id] = normalize_state_machine(row)
        except Exception:
            continue
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def ensure_signal_state_machine_rows(
    *,
    signal_rows: object,
    signal_rule_policy_rows_by_id: Mapping[str, dict] | None,
    signal_state_machine_rows: object,
) -> List[dict]:
    policy_rows = dict(signal_rule_policy_rows_by_id or {})
    machine_by_id = signal_state_machine_rows_by_id(signal_state_machine_rows)
    for signal_row in normalize_signal_rows(signal_rows):
        signal_id = str(signal_row.get("signal_id", "")).strip()
        machine_id = str(signal_row.get("state_machine_id", "")).strip()
        if (not signal_id) or (not machine_id):
            continue
        if machine_id in machine_by_id:
            continue
        policy_id = str(signal_row.get("rule_policy_id", "")).strip()
        policy_row = dict(policy_rows.get(policy_id) or {})
        aspects = _signal_aspects_for_policy(policy_row)
        initial_aspect = str((dict(signal_row.get("extensions") or {})).get("initial_aspect", "stop")).strip() or "stop"
        machine_by_id[machine_id] = build_signal_state_machine(
            signal_id=signal_id,
            state_machine_id=machine_id,
            aspects=aspects,
            initial_aspect=initial_aspect,
        )
    return [dict(machine_by_id[key]) for key in sorted(machine_by_id.keys())]


def select_signal_transition_id(*, machine_row: Mapping[str, object], target_aspect: str) -> str:
    machine = normalize_state_machine(machine_row)
    target = _normalize_signal_aspect(target_aspect)
    current_state = str(machine.get("state_id", "")).strip().lower()
    candidates = [
        dict(item)
        for item in list(machine.get("transition_rows") or [])
        if isinstance(item, Mapping) and str(item.get("to_state", "")).strip().lower() == target
    ]
    if not candidates:
        raise SignalEngineError(
            REFUSAL_MOBILITY_SIGNAL_INVALID,
            "signal target aspect transition missing",
            {
                "machine_id": str(machine.get("machine_id", "")),
                "target_aspect": target,
            },
        )
    selected = sorted(
        candidates,
        key=lambda row: (
            0 if str(row.get("from_state", "")).strip().lower() == current_state else 1,
            -1 * int(_as_int(row.get("priority", 0), 0)),
            str(row.get("from_state", "")),
            str(row.get("transition_id", "")),
        ),
    )[0]
    transition_id = str(selected.get("transition_id", "")).strip()
    if not transition_id:
        raise SignalEngineError(
            REFUSAL_MOBILITY_SIGNAL_INVALID,
            "signal transition_id missing for target aspect",
            {
                "machine_id": str(machine.get("machine_id", "")),
                "target_aspect": target,
            },
        )
    return transition_id


def evaluate_signal_aspect(
    *,
    signal_row: Mapping[str, object],
    policy_row: Mapping[str, object] | None,
    current_tick: int,
    edge_occupancy_rows_by_edge_id: Mapping[str, dict] | None,
    active_block_reservation_rows: object,
    switch_machine_rows_by_id: Mapping[str, dict] | None,
    hazard_rows_by_signal_id: Mapping[str, dict] | None,
) -> dict:
    signal = dict(signal_row or {})
    policy = dict(policy_row or {})
    attached_to = _normalize_attached_to(signal.get("attached_to"))
    edge_id = str(attached_to.get("edge_id", "")).strip()
    node_id = str(attached_to.get("node_id", "")).strip()
    switch_rows = dict(switch_machine_rows_by_id or {})
    occupancy_by_edge = dict(edge_occupancy_rows_by_edge_id or {})
    active_reservations = [
        dict(item)
        for item in list(active_block_reservation_rows or [])
        if isinstance(item, Mapping)
    ]
    hazard_by_signal = dict(hazard_rows_by_signal_id or {})
    signal_id = str(signal.get("signal_id", "")).strip()

    occupancy_row = dict(occupancy_by_edge.get(edge_id) or {}) if edge_id else {}
    occupied = bool(int(max(0, _as_int(occupancy_row.get("current_occupancy", 0), 0))) > 0)
    reservation_conflict = False
    if edge_id:
        active_vehicle_id = str((dict(signal.get("extensions") or {})).get("active_vehicle_id", "")).strip()
        for row in active_reservations:
            if str(row.get("edge_id", "")).strip() != edge_id:
                continue
            vehicle_id = str(row.get("vehicle_id", "")).strip()
            if (not active_vehicle_id) or (vehicle_id != active_vehicle_id):
                reservation_conflict = True
                break
    switch_conflict = False
    if node_id:
        machine_id = str((dict(signal.get("extensions") or {})).get("switch_machine_id", "")).strip()
        required_edge_id = str((dict(signal.get("extensions") or {})).get("required_edge_id", "")).strip()
        if machine_id and required_edge_id:
            machine_row = dict(switch_rows.get(machine_id) or {})
            if machine_row and str(machine_row.get("state_id", "")).strip() != required_edge_id:
                switch_conflict = True
    hazard_row = dict(hazard_by_signal.get(signal_id) or {})
    hazard_active = bool(hazard_row.get("active", False))

    strict_interlocking = str(signal.get("rule_policy_id", "")).strip() == "policy.rail_strict_interlocking"
    if not strict_interlocking:
        for row in list(policy.get("interlocking_rules") or []):
            if not isinstance(row, Mapping):
                continue
            if bool(row.get("requires_unreserved", False)):
                strict_interlocking = True
                break

    if hazard_active or occupied:
        aspect = "stop"
        reason = "hazard_or_occupied"
    elif strict_interlocking and reservation_conflict:
        aspect = "stop"
        reason = "strict_reservation_conflict"
    elif reservation_conflict or switch_conflict:
        aspect = "caution"
        reason = "reservation_or_switch_conflict"
    else:
        aspect = "clear"
        reason = "default_clear"
    return {
        "signal_id": signal_id,
        "target_aspect": aspect,
        "reason": reason,
        "details": {
            "attached_to": dict(attached_to),
            "edge_occupied": bool(occupied),
            "reservation_conflict": bool(reservation_conflict),
            "switch_conflict": bool(switch_conflict),
            "hazard_active": bool(hazard_active),
            "strict_interlocking": bool(strict_interlocking),
            "evaluation_tick": int(max(0, _as_int(current_tick, 0))),
        },
    }


def evaluate_signal_aspects(
    *,
    signal_rows: object,
    signal_rule_policy_rows_by_id: Mapping[str, dict] | None,
    edge_occupancy_rows_by_edge_id: Mapping[str, dict] | None,
    block_reservation_rows: object,
    switch_machine_rows_by_id: Mapping[str, dict] | None,
    hazard_rows_by_signal_id: Mapping[str, dict] | None,
    current_tick: int,
    max_signal_updates: int,
) -> dict:
    normalized_signal_rows = normalize_signal_rows(signal_rows)
    policy_rows = dict(signal_rule_policy_rows_by_id or {})
    active_reservations = active_block_reservation_rows(
        block_reservation_rows,
        current_tick=int(max(0, _as_int(current_tick, 0))),
    )
    max_updates = int(max(0, _as_int(max_signal_updates, 0)))
    processed_signal_ids: List[str] = []
    deferred_signal_ids: List[str] = []
    evaluations: List[dict] = []
    for idx, signal_row in enumerate(sorted(normalized_signal_rows, key=lambda row: str(row.get("signal_id", "")))):
        signal_id = str(signal_row.get("signal_id", "")).strip()
        if not signal_id:
            continue
        if idx >= int(max_updates):
            deferred_signal_ids.append(signal_id)
            continue
        policy_id = str(signal_row.get("rule_policy_id", "")).strip()
        policy_row = dict(policy_rows.get(policy_id) or {})
        evaluation = evaluate_signal_aspect(
            signal_row=signal_row,
            policy_row=policy_row,
            current_tick=int(current_tick),
            edge_occupancy_rows_by_edge_id=edge_occupancy_rows_by_edge_id,
            active_block_reservation_rows=active_reservations,
            switch_machine_rows_by_id=switch_machine_rows_by_id,
            hazard_rows_by_signal_id=hazard_rows_by_signal_id,
        )
        evaluations.append(dict(evaluation))
        processed_signal_ids.append(signal_id)
    return {
        "evaluations": [dict(row) for row in evaluations],
        "processed_signal_ids": _sorted_tokens(processed_signal_ids),
        "deferred_signal_ids": _sorted_tokens(deferred_signal_ids),
        "budget_outcome": "degraded" if deferred_signal_ids else "complete",
        "cost_units": int(len(processed_signal_ids)),
    }


def route_reservation_windows(
    *,
    route_edge_ids: object,
    departure_tick: int,
    estimated_arrival_tick: int,
) -> List[dict]:
    edge_ids = _sorted_tokens(list(route_edge_ids or []))
    depart = int(max(0, _as_int(departure_tick, 0)))
    arrive = int(max(depart, _as_int(estimated_arrival_tick, depart)))
    if not edge_ids:
        return []
    total_window = max(1, int(arrive - depart))
    per_edge = max(1, total_window // max(1, len(edge_ids)))
    windows: List[dict] = []
    cursor = int(depart)
    for idx, edge_id in enumerate(edge_ids):
        start_tick = int(cursor)
        if idx >= len(edge_ids) - 1:
            end_tick = int(arrive)
        else:
            end_tick = int(max(start_tick, cursor + per_edge))
        windows.append({"edge_id": edge_id, "start_tick": start_tick, "end_tick": end_tick})
        cursor = int(end_tick)
    return windows


__all__ = [
    "REFUSAL_MOBILITY_SIGNAL_INVALID",
    "REFUSAL_MOBILITY_SIGNAL_VIOLATION",
    "SignalEngineError",
    "active_block_reservation_rows",
    "build_block_reservation",
    "build_signal",
    "build_signal_state_machine",
    "build_switch_lock",
    "deterministic_block_reservation_id",
    "deterministic_signal_id",
    "deterministic_switch_lock_id",
    "ensure_signal_state_machine_rows",
    "evaluate_signal_aspect",
    "evaluate_signal_aspects",
    "normalize_block_reservation_rows",
    "normalize_signal_rows",
    "normalize_switch_lock_rows",
    "route_reservation_windows",
    "select_signal_transition_id",
    "signal_rule_policy_rows_by_id",
    "signal_state_machine_rows_by_id",
    "signal_type_rows_by_id",
    "switch_lock_rows_by_machine_id",
]
