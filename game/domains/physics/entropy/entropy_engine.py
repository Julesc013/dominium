"""PHYS-4 deterministic entropy and irreversibility helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


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


def _hash_payload(value: Mapping[str, object]) -> str:
    return canonical_sha256(dict(value))


def _sorted_unique_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def build_entropy_state(
    *,
    target_id: str,
    entropy_value: int,
    last_update_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    token = str(target_id or "").strip()
    if not token:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "target_id": token,
        "entropy_value": int(max(0, _as_int(entropy_value, 0))),
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = _hash_payload(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_entropy_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("target_id", ""))):
        normalized = build_entropy_state(
            target_id=str(row.get("target_id", "")).strip(),
            entropy_value=_as_int(row.get("entropy_value", 0), 0),
            last_update_tick=_as_int(row.get("last_update_tick", 0), 0),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("target_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def entropy_state_rows_by_target_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_entropy_state_rows(rows)
    return dict(
        (str(row.get("target_id", "")).strip(), dict(row))
        for row in normalized
        if str(row.get("target_id", "")).strip()
    )


def build_entropy_contribution(
    *,
    contribution_id: str,
    source_transformation_id: str,
    entropy_increment_formula_id: str,
    parameters: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    contribution_token = str(contribution_id or "").strip()
    source_token = str(source_transformation_id or "").strip()
    formula_token = str(entropy_increment_formula_id or "").strip()
    if (not contribution_token) or (not source_token) or (not formula_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "contribution_id": contribution_token,
        "source_transformation_id": source_token,
        "entropy_increment_formula_id": formula_token,
        "parameters": _canon(_as_map(parameters)),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = _hash_payload(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_entropy_contribution_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("contribution_id", ""))):
        normalized = build_entropy_contribution(
            contribution_id=str(row.get("contribution_id", "")).strip(),
            source_transformation_id=str(row.get("source_transformation_id", "")).strip(),
            entropy_increment_formula_id=str(row.get("entropy_increment_formula_id", "")).strip(),
            parameters=_as_map(row.get("parameters")),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("contribution_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def entropy_contribution_rows_by_source_transformation_id(rows: object) -> Dict[str, List[dict]]:
    index: Dict[str, List[dict]] = {}
    for row in normalize_entropy_contribution_rows(rows):
        source_id = str(row.get("source_transformation_id", "")).strip()
        if not source_id:
            continue
        index.setdefault(source_id, []).append(dict(row))
    return dict(
        (key, sorted(value, key=lambda item: str(item.get("contribution_id", ""))))
        for key, value in sorted(index.items(), key=lambda item: str(item[0]))
    )


def build_entropy_effect_policy(
    *,
    policy_id: str,
    efficiency_degradation_curve_id: str,
    hazard_multiplier_curve_id: str,
    maintenance_interval_modifier_id: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    token = str(policy_id or "").strip()
    if not token:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "policy_id": token,
        "efficiency_degradation_curve_id": str(efficiency_degradation_curve_id or "").strip(),
        "hazard_multiplier_curve_id": str(hazard_multiplier_curve_id or "").strip(),
        "maintenance_interval_modifier_id": str(maintenance_interval_modifier_id or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = _hash_payload(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_entropy_effect_policy_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("policy_id", ""))):
        normalized = build_entropy_effect_policy(
            policy_id=str(row.get("policy_id", "")).strip(),
            efficiency_degradation_curve_id=str(row.get("efficiency_degradation_curve_id", "")).strip(),
            hazard_multiplier_curve_id=str(row.get("hazard_multiplier_curve_id", "")).strip(),
            maintenance_interval_modifier_id=str(row.get("maintenance_interval_modifier_id", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("policy_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def entropy_effect_policy_rows_by_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_entropy_effect_policy_rows(rows)
    return dict(
        (str(row.get("policy_id", "")).strip(), dict(row))
        for row in normalized
        if str(row.get("policy_id", "")).strip()
    )


def build_entropy_event(
    *,
    event_id: str,
    tick: int,
    target_id: str,
    source_transformation_id: str,
    contribution_id: str,
    entropy_increment_formula_id: str,
    entropy_delta: int,
    entropy_value_after: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    event_token = str(event_id or "").strip()
    target_token = str(target_id or "").strip()
    source_token = str(source_transformation_id or "").strip()
    contribution_token = str(contribution_id or "").strip()
    formula_token = str(entropy_increment_formula_id or "").strip()
    if (not event_token) or (not target_token) or (not source_token) or (not formula_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "event_id": event_token,
        "tick": int(max(0, _as_int(tick, 0))),
        "target_id": target_token,
        "source_transformation_id": source_token,
        "contribution_id": contribution_token or None,
        "entropy_increment_formula_id": formula_token,
        "entropy_delta": int(max(0, _as_int(entropy_delta, 0))),
        "entropy_value_after": int(max(0, _as_int(entropy_value_after, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = _hash_payload(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_entropy_event_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("target_id", "")),
            str(item.get("event_id", "")),
        ),
    ):
        normalized = build_entropy_event(
            event_id=str(row.get("event_id", "")).strip(),
            tick=_as_int(row.get("tick", 0), 0),
            target_id=str(row.get("target_id", "")).strip(),
            source_transformation_id=str(row.get("source_transformation_id", "")).strip(),
            contribution_id=str(row.get("contribution_id", "")).strip(),
            entropy_increment_formula_id=str(row.get("entropy_increment_formula_id", "")).strip(),
            entropy_delta=_as_int(row.get("entropy_delta", 0), 0),
            entropy_value_after=_as_int(row.get("entropy_value_after", 0), 0),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("event_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_entropy_reset_event(
    *,
    event_id: str,
    tick: int,
    target_id: str,
    entropy_before: int,
    entropy_after: int,
    reset_delta: int,
    reason_code: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    event_token = str(event_id or "").strip()
    target_token = str(target_id or "").strip()
    reason_token = str(reason_code or "").strip()
    if (not event_token) or (not target_token) or (not reason_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "event_id": event_token,
        "tick": int(max(0, _as_int(tick, 0))),
        "target_id": target_token,
        "entropy_before": int(max(0, _as_int(entropy_before, 0))),
        "entropy_after": int(max(0, _as_int(entropy_after, 0))),
        "reset_delta": int(max(0, _as_int(reset_delta, 0))),
        "reason_code": reason_token,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = _hash_payload(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_entropy_reset_event_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("target_id", "")),
            str(item.get("event_id", "")),
        ),
    ):
        normalized = build_entropy_reset_event(
            event_id=str(row.get("event_id", "")).strip(),
            tick=_as_int(row.get("tick", 0), 0),
            target_id=str(row.get("target_id", "")).strip(),
            entropy_before=_as_int(row.get("entropy_before", 0), 0),
            entropy_after=_as_int(row.get("entropy_after", 0), 0),
            reset_delta=_as_int(row.get("reset_delta", 0), 0),
            reason_code=str(row.get("reason_code", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("event_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def compute_entropy_increment(
    *,
    contribution_row: Mapping[str, object],
    context_values: Mapping[str, object] | None = None,
) -> int:
    row = dict(contribution_row or {})
    context = dict(context_values or {})
    formula_id = str(row.get("entropy_increment_formula_id", "")).strip().lower()
    params = _as_map(row.get("parameters"))

    basis_value = int(max(0, _as_int(context.get("basis_value", params.get("basis_value", 0)), 0)))
    numerator = int(max(0, _as_int(params.get("numerator", 1), 1)))
    denominator = int(max(1, _as_int(params.get("denominator", 1000), 1000)))
    min_increment = int(max(0, _as_int(params.get("min_increment", 0), 0)))
    offset = int(max(0, _as_int(params.get("offset", 0), 0)))

    if formula_id in {"formula.entropy.fixed", "formula.entropy.constant"}:
        fixed_value = int(max(0, _as_int(params.get("fixed_increment", params.get("value", 0)), 0)))
        return int(fixed_value)

    if formula_id in {"formula.entropy.none", "formula.entropy.zero"}:
        return 0

    # Default deterministic linear policy for PHYS-4 stubs.
    value = int((int(basis_value) * int(numerator)) // int(denominator))
    value = int(max(0, value + int(offset)))
    if basis_value > 0:
        value = int(max(value, min_increment))
    return int(max(0, value))


def record_entropy_contribution(
    *,
    entropy_state_rows: object,
    contribution_rows: object,
    source_transformation_id: str,
    target_id: str,
    tick: int,
    context_values: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    source_token = str(source_transformation_id or "").strip()
    target_token = str(target_id or "").strip()
    if (not source_token) or (not target_token):
        return {
            "result": "refused",
            "reason_code": "refusal.entropy.invalid_target_or_source",
        }

    rows_by_source = entropy_contribution_rows_by_source_transformation_id(contribution_rows)
    contribution_list = list(rows_by_source.get(source_token) or [])
    if not contribution_list:
        return {
            "result": "skipped",
            "reason_code": "entropy.no_contribution_mapping",
            "source_transformation_id": source_token,
            "target_id": target_token,
        }
    contribution_row = dict(contribution_list[0])
    entropy_increment = int(
        max(
            0,
            compute_entropy_increment(
                contribution_row=contribution_row,
                context_values=dict(context_values or {}),
            ),
        )
    )
    if entropy_increment <= 0:
        return {
            "result": "skipped",
            "reason_code": "entropy.zero_increment",
            "source_transformation_id": source_token,
            "target_id": target_token,
        }

    states_by_target = entropy_state_rows_by_target_id(entropy_state_rows)
    existing_row = dict(states_by_target.get(target_token) or {})
    entropy_before = int(max(0, _as_int(existing_row.get("entropy_value", 0), 0)))
    entropy_after = int(entropy_before + entropy_increment)
    updated_state = build_entropy_state(
        target_id=target_token,
        entropy_value=int(entropy_after),
        last_update_tick=int(max(0, _as_int(tick, 0))),
        extensions={
            **(dict(existing_row.get("extensions") or {}) if isinstance(existing_row.get("extensions"), Mapping) else {}),
            **(dict(extensions or {}) if isinstance(extensions, Mapping) else {}),
        },
    )
    if not updated_state:
        return {
            "result": "refused",
            "reason_code": "refusal.entropy.state_invalid",
            "target_id": target_token,
        }
    states_by_target[target_token] = dict(updated_state)
    normalized_state_rows = [dict(states_by_target[key]) for key in sorted(states_by_target.keys())]

    event_id = "event.entropy.{}".format(
        canonical_sha256(
            {
                "tick": int(max(0, _as_int(tick, 0))),
                "target_id": target_token,
                "source_transformation_id": source_token,
                "contribution_id": str(contribution_row.get("contribution_id", "")).strip(),
                "entropy_delta": int(entropy_increment),
                "entropy_after": int(entropy_after),
            }
        )[:16]
    )
    event_row = build_entropy_event(
        event_id=event_id,
        tick=int(max(0, _as_int(tick, 0))),
        target_id=target_token,
        source_transformation_id=source_token,
        contribution_id=str(contribution_row.get("contribution_id", "")).strip(),
        entropy_increment_formula_id=str(contribution_row.get("entropy_increment_formula_id", "")).strip(),
        entropy_delta=int(entropy_increment),
        entropy_value_after=int(entropy_after),
        extensions={
            "entropy_before": int(entropy_before),
            "parameters": _canon(_as_map(contribution_row.get("parameters"))),
            **(dict(extensions or {}) if isinstance(extensions, Mapping) else {}),
        },
    )
    if not event_row:
        return {
            "result": "refused",
            "reason_code": "refusal.entropy.event_invalid",
            "target_id": target_token,
        }
    return {
        "result": "complete",
        "entropy_state": dict(updated_state),
        "entropy_state_rows": normalize_entropy_state_rows(normalized_state_rows),
        "entropy_event": dict(event_row),
        "entropy_delta": int(entropy_increment),
        "entropy_before": int(entropy_before),
        "entropy_after": int(entropy_after),
        "contribution": dict(contribution_row),
    }


def apply_entropy_reset(
    *,
    entropy_state_rows: object,
    target_id: str,
    tick: int,
    reason_code: str,
    reset_value: int | None = None,
    reset_fraction_numerator: int = 1,
    reset_fraction_denominator: int = 2,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    target_token = str(target_id or "").strip()
    reason_token = str(reason_code or "").strip()
    if (not target_token) or (not reason_token):
        return {"result": "refused", "reason_code": "refusal.entropy.reset_invalid"}

    states_by_target = entropy_state_rows_by_target_id(entropy_state_rows)
    existing_row = dict(states_by_target.get(target_token) or {})
    entropy_before = int(max(0, _as_int(existing_row.get("entropy_value", 0), 0)))
    if entropy_before <= 0:
        return {
            "result": "complete",
            "skipped": "no_entropy",
            "entropy_state_rows": normalize_entropy_state_rows(list(states_by_target.values())),
        }

    if reset_value is None:
        numerator = int(max(0, _as_int(reset_fraction_numerator, 1)))
        denominator = int(max(1, _as_int(reset_fraction_denominator, 2)))
        computed_reset = int((int(entropy_before) * int(numerator)) // int(denominator))
    else:
        computed_reset = int(max(0, _as_int(reset_value, 0)))
    reset_delta = int(max(0, min(entropy_before, computed_reset)))
    entropy_after = int(max(0, entropy_before - reset_delta))

    updated_state = build_entropy_state(
        target_id=target_token,
        entropy_value=int(entropy_after),
        last_update_tick=int(max(0, _as_int(tick, 0))),
        extensions={
            **(dict(existing_row.get("extensions") or {}) if isinstance(existing_row.get("extensions"), Mapping) else {}),
            "last_reset_tick": int(max(0, _as_int(tick, 0))),
            **(dict(extensions or {}) if isinstance(extensions, Mapping) else {}),
        },
    )
    states_by_target[target_token] = dict(updated_state)
    normalized_state_rows = [dict(states_by_target[key]) for key in sorted(states_by_target.keys())]

    event_id = "event.entropy.reset.{}".format(
        canonical_sha256(
            {
                "tick": int(max(0, _as_int(tick, 0))),
                "target_id": target_token,
                "entropy_before": int(entropy_before),
                "entropy_after": int(entropy_after),
                "reason_code": reason_token,
            }
        )[:16]
    )
    reset_event = build_entropy_reset_event(
        event_id=event_id,
        tick=int(max(0, _as_int(tick, 0))),
        target_id=target_token,
        entropy_before=int(entropy_before),
        entropy_after=int(entropy_after),
        reset_delta=int(reset_delta),
        reason_code=reason_token,
        extensions=dict(extensions or {}),
    )
    if not reset_event:
        return {"result": "refused", "reason_code": "refusal.entropy.reset_event_invalid"}
    return {
        "result": "complete",
        "entropy_state": dict(updated_state),
        "entropy_state_rows": normalize_entropy_state_rows(normalized_state_rows),
        "entropy_reset_event": dict(reset_event),
        "entropy_before": int(entropy_before),
        "entropy_after": int(entropy_after),
        "reset_delta": int(reset_delta),
    }


def evaluate_entropy_effects(
    *,
    entropy_state_row: Mapping[str, object],
    effect_policy_row: Mapping[str, object] | None,
) -> dict:
    state_row = dict(entropy_state_row or {})
    policy_row = dict(effect_policy_row or {})
    policy_ext = _as_map(policy_row.get("extensions"))
    entropy_value = int(max(0, _as_int(state_row.get("entropy_value", 0), 0)))

    entropy_scale = int(max(1, _as_int(policy_ext.get("entropy_unit_scale", 1000), 1000)))
    efficiency_loss_per_unit = int(max(0, _as_int(policy_ext.get("efficiency_loss_per_unit", 1), 1)))
    efficiency_floor = int(max(0, min(1000, _as_int(policy_ext.get("efficiency_floor_permille", 600), 600))))
    hazard_gain_per_unit = int(max(0, _as_int(policy_ext.get("hazard_gain_per_unit", 1), 1)))
    hazard_cap = int(max(1000, _as_int(policy_ext.get("hazard_multiplier_cap_permille", 3000), 3000)))
    maintenance_loss_per_unit = int(max(0, _as_int(policy_ext.get("maintenance_interval_loss_per_unit", 1), 1)))
    maintenance_floor = int(max(100, min(1000, _as_int(policy_ext.get("maintenance_interval_floor_permille", 300), 300))))

    entropy_steps = int(entropy_value // entropy_scale)
    efficiency_multiplier_permille = int(max(efficiency_floor, 1000 - int(entropy_steps * efficiency_loss_per_unit)))
    hazard_multiplier_permille = int(min(hazard_cap, 1000 + int(entropy_steps * hazard_gain_per_unit)))
    maintenance_interval_modifier_permille = int(
        max(maintenance_floor, 1000 - int(entropy_steps * maintenance_loss_per_unit))
    )

    return {
        "target_id": str(state_row.get("target_id", "")).strip(),
        "policy_id": str(policy_row.get("policy_id", "")).strip(),
        "entropy_value": int(entropy_value),
        "efficiency_multiplier_permille": int(efficiency_multiplier_permille),
        "hazard_multiplier_permille": int(hazard_multiplier_permille),
        "maintenance_interval_modifier_permille": int(maintenance_interval_modifier_permille),
        "degraded": bool(efficiency_multiplier_permille < 1000 or maintenance_interval_modifier_permille < 1000),
        "warnings": _sorted_unique_tokens(policy_ext.get("warnings") or []),
    }


__all__ = [
    "apply_entropy_reset",
    "build_entropy_contribution",
    "build_entropy_effect_policy",
    "build_entropy_event",
    "build_entropy_reset_event",
    "build_entropy_state",
    "compute_entropy_increment",
    "entropy_contribution_rows_by_source_transformation_id",
    "entropy_effect_policy_rows_by_id",
    "entropy_state_rows_by_target_id",
    "evaluate_entropy_effects",
    "normalize_entropy_contribution_rows",
    "normalize_entropy_effect_policy_rows",
    "normalize_entropy_event_rows",
    "normalize_entropy_reset_event_rows",
    "normalize_entropy_state_rows",
    "record_entropy_contribution",
]

