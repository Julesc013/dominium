"""Deterministic SAFETY-0 safety pattern evaluation helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_SAFETY_PATTERN_INVALID = "refusal.safety.pattern_invalid"
REFUSAL_SAFETY_INSTANCE_INVALID = "refusal.safety.instance_invalid"

_VALID_PATTERN_TYPES = {
    "interlock",
    "failsafe",
    "relief",
    "breaker",
    "redundancy",
    "deadman",
    "loto",
    "graceful_degradation",
}
_VALID_OPERATORS = {"eq", "neq", "gt", "gte", "lt", "lte", "present", "missing", "in", "nin"}


class SafetyEngineError(ValueError):
    """Safety engine deterministic refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code or REFUSAL_SAFETY_PATTERN_INVALID)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_float(value: object, default_value: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default_value)


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


def _normalize_pattern_type(value: object) -> str:
    token = str(value or "").strip().lower()
    if token in _VALID_PATTERN_TYPES:
        return token
    return "interlock"


def _normalize_operator(value: object) -> str:
    token = str(value or "").strip().lower()
    if token in _VALID_OPERATORS:
        return token
    return "eq"


def _normalize_condition_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: List[dict] = []
    for idx, row in enumerate(
        sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("predicate_id", "")))
    ):
        predicate_id = str(row.get("predicate_id", "")).strip() or "predicate.safety.{}".format(str(idx).zfill(3))
        condition = {
            "predicate_id": predicate_id,
            "operator": _normalize_operator(row.get("operator")),
            "left_operand": str(row.get("left_operand", "")).strip(),
            "right_operand": _canon(row.get("right_operand")),
            "target_id": str(row.get("target_id", "")).strip() or None,
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
        condition["deterministic_fingerprint"] = canonical_sha256(dict(condition, deterministic_fingerprint=""))
        out.append(condition)
    return [dict(row) for row in out]


def _normalize_action_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: List[dict] = []
    for idx, row in enumerate(
        sorted(
            (dict(item) for item in rows if isinstance(item, Mapping)),
            key=lambda item: (str(item.get("action_id", "")), str(item.get("action_type", ""))),
        )
    ):
        action_id = str(row.get("action_id", "")).strip() or "action.safety.{}".format(str(idx).zfill(3))
        action = {
            "action_id": action_id,
            "action_type": str(row.get("action_type", "")).strip().lower() or "noop",
            "process_id": str(row.get("process_id", "")).strip() or None,
            "target_ref": str(row.get("target_ref", "")).strip() or None,
            "parameters": _canon(_as_map(row.get("parameters"))),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
        action["deterministic_fingerprint"] = canonical_sha256(dict(action, deterministic_fingerprint=""))
        out.append(action)
    return [dict(row) for row in out]


def safety_pattern_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("safety_patterns")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("safety_patterns")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("pattern_id", ""))):
        pattern_id = str(row.get("pattern_id", "")).strip()
        if not pattern_id:
            continue
        ext = _as_map(row.get("extensions"))
        triggering_conditions = row.get("triggering_conditions")
        if not isinstance(triggering_conditions, list):
            triggering_conditions = ext.get("triggering_conditions")
        enforced_actions = row.get("enforced_actions")
        if not isinstance(enforced_actions, list):
            enforced_actions = ext.get("enforced_actions")
        required_substrates = row.get("required_substrates")
        if not isinstance(required_substrates, list):
            required_substrates = ext.get("required_substrates")
        payload_row = {
            "schema_version": "1.0.0",
            "pattern_id": pattern_id,
            "pattern_type": _normalize_pattern_type(row.get("pattern_type") or ext.get("pattern_type")),
            "triggering_conditions": _normalize_condition_rows(triggering_conditions),
            "enforced_actions": _normalize_action_rows(enforced_actions),
            "required_substrates": _sorted_tokens(required_substrates),
            "deterministic_fingerprint": "",
            "extensions": _canon(ext),
        }
        payload_row["deterministic_fingerprint"] = canonical_sha256(dict(payload_row, deterministic_fingerprint=""))
        out[pattern_id] = payload_row
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_safety_instance(
    *,
    instance_id: str,
    pattern_id: str,
    target_ids: object,
    active: bool,
    created_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "instance_id": str(instance_id or "").strip(),
        "pattern_id": str(pattern_id or "").strip(),
        "target_ids": _sorted_tokens(target_ids),
        "active": bool(active),
        "created_tick": int(max(0, _as_int(created_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if not payload["instance_id"] or not payload["pattern_id"]:
        raise SafetyEngineError(
            REFUSAL_SAFETY_INSTANCE_INVALID,
            "safety instance requires instance_id and pattern_id",
            {"instance_id": payload["instance_id"], "pattern_id": payload["pattern_id"]},
        )
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_safety_instance_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("instance_id", ""))):
        instance_id = str(row.get("instance_id", "")).strip()
        if not instance_id:
            continue
        try:
            out[instance_id] = build_safety_instance(
                instance_id=instance_id,
                pattern_id=str(row.get("pattern_id", "")).strip(),
                target_ids=row.get("target_ids"),
                active=bool(row.get("active", True)),
                created_tick=_as_int(row.get("created_tick", 0), 0),
                extensions=_as_map(row.get("extensions")),
            )
        except SafetyEngineError:
            continue
    return [dict(out[key]) for key in sorted(out.keys())]


def build_safety_event(
    *,
    event_id: str,
    tick: int,
    instance_id: str,
    pattern_id: str,
    pattern_type: str,
    status: str,
    target_ids: object,
    action_count: int,
    details: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "event_id": str(event_id or "").strip(),
        "tick": int(max(0, _as_int(tick, 0))),
        "instance_id": str(instance_id or "").strip(),
        "pattern_id": str(pattern_id or "").strip(),
        "pattern_type": _normalize_pattern_type(pattern_type),
        "status": str(status or "").strip().lower() or "triggered",
        "target_ids": _sorted_tokens(target_ids),
        "action_count": int(max(0, _as_int(action_count, 0))),
        "details": _canon(_as_map(details)),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if not payload["event_id"]:
        payload["event_id"] = "event.safety.{}".format(
            canonical_sha256(
                {
                    "tick": int(payload["tick"]),
                    "instance_id": payload["instance_id"],
                    "pattern_id": payload["pattern_id"],
                    "status": payload["status"],
                    "target_ids": payload["target_ids"],
                }
            )[:16]
        )
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_safety_event_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (_as_int(item.get("tick", 0), 0), str(item.get("event_id", ""))),
    ):
        event_id = str(row.get("event_id", "")).strip()
        payload = build_safety_event(
            event_id=event_id,
            tick=_as_int(row.get("tick", 0), 0),
            instance_id=str(row.get("instance_id", "")).strip(),
            pattern_id=str(row.get("pattern_id", "")).strip(),
            pattern_type=str(row.get("pattern_type", "interlock")).strip(),
            status=str(row.get("status", "triggered")).strip(),
            target_ids=row.get("target_ids"),
            action_count=_as_int(row.get("action_count", 0), 0),
            details=_as_map(row.get("details")),
            extensions=_as_map(row.get("extensions")),
        )
        out[str(payload.get("event_id", "")).strip()] = payload
    return [dict(out[key]) for key in sorted(out.keys(), key=lambda key: (_as_int(out[key].get("tick", 0), 0), key))]


def _lookup_operand(context_row: Mapping[str, object], operand: str) -> object:
    token = str(operand or "").strip()
    if not token:
        return None
    current: object = context_row
    for part in token.split("."):
        if not part:
            continue
        if not isinstance(current, Mapping):
            return None
        current = dict(current).get(part)
    return current


def _evaluate_predicate(
    *,
    predicate_row: Mapping[str, object],
    context_row: Mapping[str, object],
) -> dict:
    row = dict(predicate_row or {})
    operator = _normalize_operator(row.get("operator"))
    left_operand = str(row.get("left_operand", "")).strip()
    right_operand = row.get("right_operand")
    left_value = _lookup_operand(context_row, left_operand)
    if operator == "present":
        result = left_value is not None
    elif operator == "missing":
        result = left_value is None
    elif operator == "eq":
        result = left_value == right_operand
    elif operator == "neq":
        result = left_value != right_operand
    elif operator == "gt":
        result = _as_float(left_value, 0.0) > _as_float(right_operand, 0.0)
    elif operator == "gte":
        result = _as_float(left_value, 0.0) >= _as_float(right_operand, 0.0)
    elif operator == "lt":
        result = _as_float(left_value, 0.0) < _as_float(right_operand, 0.0)
    elif operator == "lte":
        result = _as_float(left_value, 0.0) <= _as_float(right_operand, 0.0)
    elif operator == "in":
        values = right_operand if isinstance(right_operand, list) else []
        result = left_value in values
    elif operator == "nin":
        values = right_operand if isinstance(right_operand, list) else []
        result = left_value not in values
    else:
        result = False
    return {
        "predicate_id": str(row.get("predicate_id", "")).strip(),
        "operator": operator,
        "left_operand": left_operand,
        "left_value": _canon(left_value),
        "right_operand": _canon(right_operand),
        "result": bool(result),
    }


def evaluate_safety_instances(
    *,
    instance_rows: object,
    pattern_rows_by_id: Mapping[str, dict] | None,
    context_rows_by_target_id: Mapping[str, Mapping[str, object]] | None,
    current_tick: int,
    max_instance_updates: int,
) -> dict:
    instances = normalize_safety_instance_rows(instance_rows)
    pattern_map = dict(pattern_rows_by_id or {})
    context_map = dict(context_rows_by_target_id or {})
    max_updates = int(max(0, _as_int(max_instance_updates, 0)))
    evaluated_ids: List[str] = []
    deferred_ids: List[str] = []
    triggered_ids: List[str] = []
    action_rows: List[dict] = []
    event_rows: List[dict] = []
    missing_pattern_ids: List[str] = []

    for idx, instance in enumerate(instances):
        instance_id = str(instance.get("instance_id", "")).strip()
        pattern_id = str(instance.get("pattern_id", "")).strip()
        if idx >= max_updates:
            deferred_ids.append(instance_id)
            event_rows.append(
                build_safety_event(
                    event_id="",
                    tick=int(current_tick),
                    instance_id=instance_id,
                    pattern_id=pattern_id,
                    pattern_type="interlock",
                    status="deferred",
                    target_ids=instance.get("target_ids"),
                    action_count=0,
                    details={"reason": "budget"},
                    extensions={},
                )
            )
            continue
        evaluated_ids.append(instance_id)
        if not bool(instance.get("active", True)):
            event_rows.append(
                build_safety_event(
                    event_id="",
                    tick=int(current_tick),
                    instance_id=instance_id,
                    pattern_id=pattern_id,
                    pattern_type="interlock",
                    status="inactive",
                    target_ids=instance.get("target_ids"),
                    action_count=0,
                    details={},
                    extensions={},
                )
            )
            continue

        pattern_row = dict(pattern_map.get(pattern_id) or {})
        if not pattern_row:
            missing_pattern_ids.append(pattern_id)
            event_rows.append(
                build_safety_event(
                    event_id="",
                    tick=int(current_tick),
                    instance_id=instance_id,
                    pattern_id=pattern_id,
                    pattern_type="interlock",
                    status="missing_pattern",
                    target_ids=instance.get("target_ids"),
                    action_count=0,
                    details={},
                    extensions={},
                )
            )
            continue

        target_ids = _sorted_tokens(instance.get("target_ids"))
        primary_target_id = target_ids[0] if target_ids else ""
        condition_rows = [dict(row) for row in list(pattern_row.get("triggering_conditions") or []) if isinstance(row, Mapping)]
        condition_results: List[dict] = []
        for condition in condition_rows:
            raw_target_id = condition.get("target_id")
            target_id = ("" if raw_target_id is None else str(raw_target_id).strip()) or primary_target_id
            context_row = _as_map(context_map.get(target_id))
            condition_results.append(
                _evaluate_predicate(
                    predicate_row=condition,
                    context_row=context_row,
                )
            )
        triggered = bool(condition_results) and all(bool(row.get("result", False)) for row in condition_results)
        if triggered:
            triggered_ids.append(instance_id)
            actions = [dict(row) for row in list(pattern_row.get("enforced_actions") or []) if isinstance(row, Mapping)]
            for action_idx, action in enumerate(actions):
                action_rows.append(
                    {
                        "instance_id": instance_id,
                        "pattern_id": pattern_id,
                        "pattern_type": str(pattern_row.get("pattern_type", "interlock")).strip() or "interlock",
                        "target_ids": list(target_ids),
                        "action_sequence": int(action_idx),
                        "action_id": str(action.get("action_id", "")).strip() or "action.unknown",
                        "action_type": str(action.get("action_type", "")).strip().lower() or "noop",
                        "process_id": str(action.get("process_id", "")).strip() or None,
                        "target_ref": str(action.get("target_ref", "")).strip() or None,
                        "parameters": _as_map(action.get("parameters")),
                        "extensions": _as_map(action.get("extensions")),
                    }
                )
            event_rows.append(
                build_safety_event(
                    event_id="",
                    tick=int(current_tick),
                    instance_id=instance_id,
                    pattern_id=pattern_id,
                    pattern_type=str(pattern_row.get("pattern_type", "interlock")).strip() or "interlock",
                    status="triggered",
                    target_ids=target_ids,
                    action_count=int(len(actions)),
                    details={"condition_results": [dict(row) for row in condition_results]},
                    extensions={},
                )
            )
        else:
            event_rows.append(
                build_safety_event(
                    event_id="",
                    tick=int(current_tick),
                    instance_id=instance_id,
                    pattern_id=pattern_id,
                    pattern_type=str(pattern_row.get("pattern_type", "interlock")).strip() or "interlock",
                    status="clear",
                    target_ids=target_ids,
                    action_count=0,
                    details={"condition_results": [dict(row) for row in condition_results]},
                    extensions={},
                )
            )
    normalized_events = normalize_safety_event_rows(event_rows)
    sorted_actions = sorted(
        action_rows,
        key=lambda row: (
            str(row.get("instance_id", "")),
            int(_as_int(row.get("action_sequence", 0), 0)),
            str(row.get("action_id", "")),
        ),
    )
    return {
        "evaluated_instance_ids": _sorted_tokens(evaluated_ids),
        "deferred_instance_ids": _sorted_tokens(deferred_ids),
        "triggered_instance_ids": _sorted_tokens(triggered_ids),
        "missing_pattern_ids": _sorted_tokens(missing_pattern_ids),
        "actions": [dict(row) for row in sorted_actions],
        "events": [dict(row) for row in normalized_events],
        "cost_units": int(len(evaluated_ids)),
        "budget_outcome": "degraded" if deferred_ids else "complete",
    }


__all__ = [
    "REFUSAL_SAFETY_INSTANCE_INVALID",
    "REFUSAL_SAFETY_PATTERN_INVALID",
    "SafetyEngineError",
    "build_safety_event",
    "build_safety_instance",
    "evaluate_safety_instances",
    "normalize_safety_event_rows",
    "normalize_safety_instance_rows",
    "safety_pattern_rows_by_id",
]
