"""Deterministic CTRL-8 effect engine for temporary modifiers."""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256


STACK_MODE_REPLACE = "replace"
STACK_MODE_MAX = "max"
STACK_MODE_MIN = "min"
STACK_MODE_ADD = "add"
STACK_MODE_MULTIPLY = "multiply"

REFUSAL_EFFECT_FORBIDDEN = "refusal.effect.forbidden"
REFUSAL_EFFECT_INVALID_TARGET = "refusal.effect.invalid_target"

_STACK_MODES = {
    STACK_MODE_REPLACE,
    STACK_MODE_MAX,
    STACK_MODE_MIN,
    STACK_MODE_ADD,
    STACK_MODE_MULTIPLY,
}

_DEFAULT_STACKING_POLICY_ROWS = {
    "stack.replace_latest": {
        "schema_version": "1.0.0",
        "stacking_policy_id": "stack.replace_latest",
        "mode": STACK_MODE_REPLACE,
        "tie_break_rule": "order.effect_type_applied_tick_effect_id",
        "extensions": {},
    },
    "stack.min": {
        "schema_version": "1.0.0",
        "stacking_policy_id": "stack.min",
        "mode": STACK_MODE_MIN,
        "tie_break_rule": "order.effect_type_applied_tick_effect_id",
        "extensions": {},
    },
    "stack.multiply": {
        "schema_version": "1.0.0",
        "stacking_policy_id": "stack.multiply",
        "mode": STACK_MODE_MULTIPLY,
        "tie_break_rule": "order.effect_type_applied_tick_effect_id",
        "extensions": {},
    },
    "stack.add": {
        "schema_version": "1.0.0",
        "stacking_policy_id": "stack.add",
        "mode": STACK_MODE_ADD,
        "tie_break_rule": "order.effect_type_applied_tick_effect_id",
        "extensions": {},
    },
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _effect_id_seed(
    *,
    effect_type_id: str,
    target_id: str,
    applied_tick: int,
    expires_tick: int | None,
    duration_ticks: int | None,
    magnitude: object,
    stacking_policy_id: str,
    source_event_id: str | None,
    extensions: Mapping[str, object],
) -> dict:
    return {
        "effect_type_id": str(effect_type_id),
        "target_id": str(target_id),
        "applied_tick": int(max(0, int(applied_tick))),
        "expires_tick": None if expires_tick is None else int(max(0, int(expires_tick))),
        "duration_ticks": None if duration_ticks is None else int(max(0, int(duration_ticks))),
        "magnitude": _canon(magnitude),
        "stacking_policy_id": str(stacking_policy_id),
        "source_event_id": None if source_event_id is None else str(source_event_id),
        "extensions": _canon(dict(extensions or {})),
    }


def _normalize_expires_tick(*, applied_tick: int, duration_ticks: int | None, expires_tick: int | None) -> int | None:
    if expires_tick is not None:
        return int(max(0, int(expires_tick)))
    if duration_ticks is None:
        return None
    return int(max(0, int(applied_tick)) + max(0, int(duration_ticks)))


def _normalize_duration_ticks(*, applied_tick: int, expires_tick: int | None, duration_ticks: int | None) -> int | None:
    if duration_ticks is not None:
        return int(max(0, int(duration_ticks)))
    if expires_tick is None:
        return None
    return int(max(0, int(expires_tick)) - max(0, int(applied_tick)))


def _normalize_stack_mode(value: object) -> str:
    token = str(value or "").strip()
    if token in _STACK_MODES:
        return token
    return STACK_MODE_REPLACE


def _normalize_stacking_policy_id(value: object) -> str:
    token = str(value or "").strip()
    if token:
        return token
    return "stack.replace_latest"


def _normalize_magnitude(value: object):
    if isinstance(value, Mapping):
        return _canon(dict(value))
    if isinstance(value, list):
        return _canon(list(value))
    if value is None:
        return {}
    if isinstance(value, (int, float, bool, str)):
        return value
    return str(value)


def build_effect(
    *,
    effect_type_id: str,
    target_id: str,
    applied_tick: int,
    magnitude: object,
    stacking_policy_id: str,
    duration_ticks: int | None = None,
    expires_tick: int | None = None,
    source_event_id: str | None = None,
    effect_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    applied = int(max(0, _as_int(applied_tick, 0)))
    normalized_expires = _normalize_expires_tick(
        applied_tick=applied,
        duration_ticks=duration_ticks,
        expires_tick=expires_tick,
    )
    normalized_duration = _normalize_duration_ticks(
        applied_tick=applied,
        expires_tick=normalized_expires,
        duration_ticks=duration_ticks,
    )
    effect_type_token = str(effect_type_id).strip()
    target_token = str(target_id).strip()
    source_event_token = str(source_event_id).strip() if source_event_id is not None else None
    stack_policy_token = _normalize_stacking_policy_id(stacking_policy_id)
    ext = dict(extensions or {})
    magnitude_payload = _normalize_magnitude(magnitude)
    provided_effect_id = str(effect_id).strip()
    if provided_effect_id:
        normalized_effect_id = provided_effect_id
    else:
        normalized_effect_id = "effect.instance.{}".format(
            canonical_sha256(
                _effect_id_seed(
                    effect_type_id=effect_type_token,
                    target_id=target_token,
                    applied_tick=applied,
                    expires_tick=normalized_expires,
                    duration_ticks=normalized_duration,
                    magnitude=magnitude_payload,
                    stacking_policy_id=stack_policy_token,
                    source_event_id=source_event_token,
                    extensions=ext,
                )
            )[:16]
        )

    payload = {
        "schema_version": "1.0.0",
        "effect_id": normalized_effect_id,
        "effect_type_id": effect_type_token,
        "target_id": target_token,
        "applied_tick": int(applied),
        "expires_tick": None if normalized_expires is None else int(normalized_expires),
        "duration_ticks": None if normalized_duration is None else int(max(0, normalized_duration)),
        "magnitude": magnitude_payload,
        "stacking_policy_id": stack_policy_token,
        "source_event_id": None if source_event_token is None else source_event_token,
        "deterministic_fingerprint": "",
        "extensions": dict(ext),
    }
    seed = dict(payload)
    seed["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = canonical_sha256(seed)
    return payload


def normalize_effect_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    by_id: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("target_id", "")),
            str(item.get("effect_type_id", "")),
            _as_int(item.get("applied_tick", 0), 0),
            str(item.get("effect_id", "")),
        ),
    ):
        effect_type_id = str(row.get("effect_type_id", "")).strip()
        target_id = str(row.get("target_id", "")).strip()
        if not effect_type_id or not target_id:
            continue
        normalized = build_effect(
            effect_id=str(row.get("effect_id", "")).strip(),
            effect_type_id=effect_type_id,
            target_id=target_id,
            applied_tick=max(0, _as_int(row.get("applied_tick", 0), 0)),
            expires_tick=(
                max(0, _as_int(row.get("expires_tick", 0), 0))
                if row.get("expires_tick") is not None
                else None
            ),
            duration_ticks=(
                max(0, _as_int(row.get("duration_ticks", 0), 0))
                if row.get("duration_ticks") is not None
                else None
            ),
            magnitude=row.get("magnitude"),
            stacking_policy_id=str(row.get("stacking_policy_id", "stack.replace_latest")).strip() or "stack.replace_latest",
            source_event_id=(
                None
                if row.get("source_event_id") is None
                else str(row.get("source_event_id", "")).strip() or None
            ),
            extensions=_as_map(row.get("extensions")),
        )
        effect_id = str(normalized.get("effect_id", "")).strip()
        if effect_id:
            by_id[effect_id] = normalized
    return sorted(
        (dict(by_id[key]) for key in sorted(by_id.keys())),
        key=lambda row: (
            str(row.get("target_id", "")),
            str(row.get("effect_type_id", "")),
            _as_int(row.get("applied_tick", 0), 0),
            str(row.get("effect_id", "")),
        ),
    )


def effect_type_rows_by_id(effect_type_registry: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(effect_type_registry)
    rows = payload.get("effect_types")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("effect_types")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("effect_type_id", ""))):
        effect_type_id = str(row.get("effect_type_id", "")).strip()
        if not effect_type_id:
            continue
        out[effect_type_id] = {
            "schema_version": "1.0.0",
            "effect_type_id": effect_type_id,
            "description": str(row.get("description", "")).strip(),
            "applies_to": _sorted_unique_strings(row.get("applies_to")),
            "modifies": _sorted_unique_strings(row.get("modifies")),
            "default_visibility_policy_id": str(row.get("default_visibility_policy_id", "")).strip(),
            "extensions": _as_map(row.get("extensions")),
        }
    return out


def stacking_policy_rows_by_id(stacking_policy_registry: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(stacking_policy_registry)
    rows = payload.get("stacking_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("stacking_policies")
    if not isinstance(rows, list):
        rows = []

    out: Dict[str, dict] = dict((key, dict(value)) for key, value in _DEFAULT_STACKING_POLICY_ROWS.items())
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("stacking_policy_id", ""))):
        stacking_policy_id = str(row.get("stacking_policy_id", "")).strip()
        if not stacking_policy_id:
            continue
        out[stacking_policy_id] = {
            "schema_version": "1.0.0",
            "stacking_policy_id": stacking_policy_id,
            "mode": _normalize_stack_mode(row.get("mode")),
            "tie_break_rule": str(row.get("tie_break_rule", "")).strip() or "order.effect_type_applied_tick_effect_id",
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def prune_expired_effect_rows(*, effect_rows: object, current_tick: int) -> List[dict]:
    tick = int(max(0, _as_int(current_tick, 0)))
    normalized = normalize_effect_rows(effect_rows)
    active: List[dict] = []
    for row in normalized:
        expires_tick = row.get("expires_tick")
        if expires_tick is None:
            active.append(dict(row))
            continue
        if tick >= int(max(0, _as_int(expires_tick, 0))):
            continue
        active.append(dict(row))
    return sorted(
        active,
        key=lambda row: (
            str(row.get("target_id", "")),
            str(row.get("effect_type_id", "")),
            _as_int(row.get("applied_tick", 0), 0),
            str(row.get("effect_id", "")),
        ),
    )


def active_effect_rows_by_target(*, effect_rows: object, current_tick: int) -> Dict[str, List[dict]]:
    active_rows = prune_expired_effect_rows(effect_rows=effect_rows, current_tick=current_tick)
    out: Dict[str, List[dict]] = {}
    for row in active_rows:
        target_id = str(row.get("target_id", "")).strip()
        if not target_id:
            continue
        out.setdefault(target_id, []).append(dict(row))
    return dict(
        (
            target_id,
            sorted(
                (dict(row) for row in out[target_id]),
                key=lambda row: (
                    str(row.get("effect_type_id", "")),
                    _as_int(row.get("applied_tick", 0), 0),
                    str(row.get("effect_id", "")),
                ),
            ),
        )
        for target_id in sorted(out.keys())
    )


def _extract_numeric_value(raw_value: object) -> int:
    if isinstance(raw_value, bool):
        return 1 if raw_value else 0
    if isinstance(raw_value, (int, float)):
        return int(raw_value)
    if isinstance(raw_value, str):
        token = str(raw_value).strip()
        return _as_int(token, 0)
    if isinstance(raw_value, Mapping):
        payload = _as_map(raw_value)
        for key in ("value", "permille", "raw"):
            if key in payload:
                return _extract_numeric_value(payload.get(key))
        return 0
    return 0


def _magnitude_value_for_key(magnitude: object, key: str) -> int:
    token = str(key).strip()
    if not token:
        return 0
    if isinstance(magnitude, Mapping):
        payload = _as_map(magnitude)
        if token in payload:
            return _extract_numeric_value(payload.get(token))
        if "value" in payload:
            return _extract_numeric_value(payload.get("value"))
        return 0
    return _extract_numeric_value(magnitude)


def _apply_stack_mode(
    *,
    current_value: int | None,
    next_value: int,
    mode: str,
) -> int:
    stack_mode = _normalize_stack_mode(mode)
    if current_value is None:
        if stack_mode == STACK_MODE_MULTIPLY:
            return int(next_value if next_value != 0 else 1000)
        return int(next_value)
    if stack_mode == STACK_MODE_REPLACE:
        return int(next_value)
    if stack_mode == STACK_MODE_MAX:
        return int(max(int(current_value), int(next_value)))
    if stack_mode == STACK_MODE_MIN:
        return int(min(int(current_value), int(next_value)))
    if stack_mode == STACK_MODE_ADD:
        return int(current_value) + int(next_value)
    if stack_mode == STACK_MODE_MULTIPLY:
        return int((int(current_value) * int(next_value)) // 1000)
    return int(next_value)


def get_effective_modifier(
    *,
    target_id: str,
    key: str,
    effect_rows: object,
    current_tick: int,
    effect_type_registry: Mapping[str, object] | None = None,
    stacking_policy_registry: Mapping[str, object] | None = None,
) -> dict:
    target_token = str(target_id).strip()
    key_token = str(key).strip()
    if not target_token or not key_token:
        out = {
            "value": 0,
            "present": False,
            "query_cost_units": 1,
            "applied_effect_ids": [],
            "deterministic_fingerprint": "",
        }
        seed = dict(out)
        seed["deterministic_fingerprint"] = ""
        out["deterministic_fingerprint"] = canonical_sha256(seed)
        return out

    effect_type_rows = effect_type_rows_by_id(effect_type_registry)
    stack_rows = stacking_policy_rows_by_id(stacking_policy_registry)
    active_by_target = active_effect_rows_by_target(effect_rows=effect_rows, current_tick=current_tick)
    active_rows = list(active_by_target.get(target_token) or [])
    ordered_rows = sorted(
        active_rows,
        key=lambda row: (
            str(row.get("effect_type_id", "")),
            _as_int(row.get("applied_tick", 0), 0),
            str(row.get("effect_id", "")),
        ),
    )

    value: int | None = None
    applied_effect_ids: List[str] = []
    applied_modes: List[str] = []
    for row in ordered_rows:
        effect_type_id = str(row.get("effect_type_id", "")).strip()
        type_row = dict(effect_type_rows.get(effect_type_id) or {})
        modifies = _sorted_unique_strings(type_row.get("modifies"))
        if modifies and key_token not in set(modifies):
            continue
        magnitude_value = _magnitude_value_for_key(row.get("magnitude"), key_token)
        stack_policy_id = _normalize_stacking_policy_id(row.get("stacking_policy_id"))
        stack_mode = _normalize_stack_mode((dict(stack_rows.get(stack_policy_id) or {})).get("mode"))
        value = _apply_stack_mode(current_value=value, next_value=magnitude_value, mode=stack_mode)
        applied_effect_ids.append(str(row.get("effect_id", "")).strip())
        applied_modes.append(stack_mode)

    result_value = int(value if value is not None else 0)
    out = {
        "value": int(result_value),
        "present": bool(applied_effect_ids),
        "query_cost_units": 1,
        "applied_effect_ids": [token for token in applied_effect_ids if token],
        "stacking_modes": list(applied_modes),
        "deterministic_fingerprint": "",
    }
    seed = dict(out)
    seed["deterministic_fingerprint"] = ""
    out["deterministic_fingerprint"] = canonical_sha256(seed)
    return out


def get_effective_modifier_map(
    *,
    target_id: str,
    keys: Sequence[str],
    effect_rows: object,
    current_tick: int,
    effect_type_registry: Mapping[str, object] | None = None,
    stacking_policy_registry: Mapping[str, object] | None = None,
) -> dict:
    key_rows = [token for token in _sorted_unique_strings(list(keys or [])) if token]
    modifiers = {}
    total_cost = 0
    for key in key_rows:
        row = get_effective_modifier(
            target_id=target_id,
            key=key,
            effect_rows=effect_rows,
            current_tick=current_tick,
            effect_type_registry=effect_type_registry,
            stacking_policy_registry=stacking_policy_registry,
        )
        modifiers[key] = dict(row)
        total_cost += int(max(0, _as_int(row.get("query_cost_units", 0), 0)))
    out = {
        "target_id": str(target_id).strip(),
        "modifiers": dict((token, modifiers[token]) for token in sorted(modifiers.keys())),
        "query_cost_units": int(total_cost),
        "deterministic_fingerprint": "",
    }
    seed = dict(out)
    seed["deterministic_fingerprint"] = ""
    out["deterministic_fingerprint"] = canonical_sha256(seed)
    return out


__all__ = [
    "REFUSAL_EFFECT_FORBIDDEN",
    "REFUSAL_EFFECT_INVALID_TARGET",
    "STACK_MODE_ADD",
    "STACK_MODE_MAX",
    "STACK_MODE_MIN",
    "STACK_MODE_MULTIPLY",
    "STACK_MODE_REPLACE",
    "active_effect_rows_by_target",
    "build_effect",
    "effect_type_rows_by_id",
    "get_effective_modifier",
    "get_effective_modifier_map",
    "normalize_effect_rows",
    "prune_expired_effect_rows",
    "stacking_policy_rows_by_id",
]
