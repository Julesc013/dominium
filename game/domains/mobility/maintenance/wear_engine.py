"""Deterministic MOB-9 mobility wear and maintenance helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from models.model_engine import compute_wear_ratio_permille
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


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def build_wear_state(
    *,
    target_id: str,
    wear_type_id: str,
    accumulated_value: int,
    last_update_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "target_id": str(target_id or "").strip(),
        "wear_type_id": str(wear_type_id or "").strip(),
        "accumulated_value": int(max(0, _as_int(accumulated_value, 0))),
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_wear_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[Tuple[str, str], dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (str(item.get("target_id", "")), str(item.get("wear_type_id", ""))),
    ):
        target_id = str(row.get("target_id", "")).strip()
        wear_type_id = str(row.get("wear_type_id", "")).strip()
        if (not target_id) or (not wear_type_id):
            continue
        key = (target_id, wear_type_id)
        out[key] = build_wear_state(
            target_id=target_id,
            wear_type_id=wear_type_id,
            accumulated_value=int(max(0, _as_int(row.get("accumulated_value", 0), 0))),
            last_update_tick=int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def wear_rows_by_target_and_type(rows: object) -> Dict[Tuple[str, str], dict]:
    return dict(
        (
            (str(row.get("target_id", "")).strip(), str(row.get("wear_type_id", "")).strip()),
            dict(row),
        )
        for row in normalize_wear_state_rows(rows)
        if str(row.get("target_id", "")).strip() and str(row.get("wear_type_id", "")).strip()
    )


def wear_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("wear_types")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("wear_types")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("wear_type_id", ""))):
        wear_type_id = str(row.get("wear_type_id", "")).strip()
        if not wear_type_id:
            continue
        ext = _as_map(row.get("extensions"))
        out[wear_type_id] = {
            "schema_version": "1.0.0",
            "wear_type_id": wear_type_id,
            "description": str(row.get("description", "")).strip(),
            "accumulation_policy_id": str(
                row.get("accumulation_policy_id", "")
            ).strip()
            or str(ext.get("accumulation_policy_id", "")).strip()
            or "accum.per_tick",
            "hazard_threshold": int(
                max(
                    1,
                    _as_int(
                        row.get("hazard_threshold", ext.get("hazard_threshold", 100000)),
                        100000,
                    ),
                )
            ),
            "effect_modifier_id": (
                None
                if (row.get("effect_modifier_id") is None and ext.get("effect_modifier_id") is None)
                else (
                    str(row.get("effect_modifier_id", "")).strip()
                    or str(ext.get("effect_modifier_id", "")).strip()
                    or None
                )
            ),
            "schema_ref": str(row.get("schema_ref", "")).strip(),
            "extensions": _canon(ext),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def wear_accumulation_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("accumulation_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("accumulation_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("accumulation_policy_id", "")),
    ):
        policy_id = str(row.get("accumulation_policy_id", "")).strip()
        if not policy_id:
            continue
        out[policy_id] = {
            "schema_version": "1.0.0",
            "accumulation_policy_id": policy_id,
            "description": str(row.get("description", "")).strip(),
            "schema_ref": str(row.get("schema_ref", "")).strip(),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def wear_ratio_permille(*, accumulated_value: int, hazard_threshold: int) -> int:
    return int(
        compute_wear_ratio_permille(
            accumulated_value=int(accumulated_value),
            hazard_threshold=int(hazard_threshold),
        )
    )


def track_wear_modifier_permille(
    *,
    target_id: str,
    wear_rows: object,
    wear_type_rows: Mapping[str, dict] | None,
    default_threshold: int = 100000,
) -> int:
    rows_by_key = wear_rows_by_target_and_type(wear_rows)
    row = dict(rows_by_key.get((str(target_id or "").strip(), "wear.track")) or {})
    wear_type_row = dict((dict(wear_type_rows or {})).get("wear.track") or {})
    accumulated = int(max(0, _as_int(row.get("accumulated_value", 0), 0)))
    track_limit = int(max(1, _as_int(wear_type_row.get("hazard_threshold", default_threshold), default_threshold)))
    wear_score = int(wear_ratio_permille(accumulated_value=accumulated, hazard_threshold=track_limit))
    # 0 wear => 1000 permille, threshold wear => 600 permille, severe wear floors at 200.
    degraded = int(min(800, (int(wear_score) * 400) // 1000))
    return int(max(200, 1000 - degraded))


def _policy_base_increment(update_row: Mapping[str, object], policy_row: Mapping[str, object]) -> int:
    row = dict(update_row or {})
    ext = _as_map(policy_row.get("extensions"))
    explicit_increment = row.get("increment")
    if explicit_increment is not None:
        return int(max(0, _as_int(explicit_increment, 0)))
    per_cycle = int(max(0, _as_int(ext.get("base_rate_per_cycle", 0), 0)))
    per_tick = int(max(0, _as_int(ext.get("base_rate_per_tick", 0), 0)))
    cycles = int(max(0, _as_int(row.get("cycles", 0), 0)))
    dt_ticks = int(max(1, _as_int(row.get("dt_ticks", 1), 1)))
    if cycles > 0 and per_cycle > 0:
        return int(cycles * per_cycle)
    return int(per_tick * dt_ticks)


def apply_wear_updates(
    *,
    wear_rows: object,
    update_rows: object,
    wear_type_rows: Mapping[str, dict] | None,
    accumulation_policy_rows: Mapping[str, dict] | None,
    current_tick: int,
    max_updates: int,
) -> dict:
    rows_by_key = wear_rows_by_target_and_type(wear_rows)
    wear_type_map = dict(wear_type_rows or {})
    accumulation_policy_map = dict(accumulation_policy_rows or {})
    normalized_updates: List[dict] = []
    for row in sorted(
        (dict(item) for item in list(update_rows or []) if isinstance(item, Mapping)),
        key=lambda item: (str(item.get("target_id", "")), str(item.get("wear_type_id", ""))),
    ):
        target_id = str(row.get("target_id", "")).strip()
        wear_type_id = str(row.get("wear_type_id", "")).strip()
        if (not target_id) or (not wear_type_id):
            continue
        normalized_updates.append(
            {
                "target_id": target_id,
                "wear_type_id": wear_type_id,
                "increment": row.get("increment"),
                "cycles": int(max(0, _as_int(row.get("cycles", 0), 0))),
                "dt_ticks": int(max(1, _as_int(row.get("dt_ticks", 1), 1))),
                "environment_scale_permille": int(
                    max(100, min(3000, _as_int(row.get("environment_scale_permille", 1000), 1000)))
                ),
                "load_scale_permille": int(
                    max(100, min(3000, _as_int(row.get("load_scale_permille", 1000), 1000)))
                ),
                "extensions": _as_map(row.get("extensions")),
            }
        )

    max_updates_norm = int(max(0, _as_int(max_updates, 0)))
    processed_keys: List[str] = []
    deferred_keys: List[str] = []
    threshold_crossings: List[dict] = []

    for idx, update in enumerate(normalized_updates):
        key_token = "{}::{}".format(str(update.get("target_id", "")), str(update.get("wear_type_id", "")))
        if idx >= max_updates_norm:
            deferred_keys.append(key_token)
            continue
        wear_type_id = str(update.get("wear_type_id", "")).strip()
        wear_type_row = dict(wear_type_map.get(wear_type_id) or {})
        accumulation_policy_id = str(wear_type_row.get("accumulation_policy_id", "")).strip() or "accum.per_tick"
        accumulation_policy_row = dict(accumulation_policy_map.get(accumulation_policy_id) or {})
        base_increment = _policy_base_increment(update, accumulation_policy_row)
        increment = int(
            max(
                0,
                (int(base_increment) * int(update.get("environment_scale_permille", 1000)) * int(update.get("load_scale_permille", 1000))) // 1_000_000,
            )
        )
        key = (str(update.get("target_id", "")).strip(), wear_type_id)
        existing = dict(rows_by_key.get(key) or {})
        accumulated_before = int(max(0, _as_int(existing.get("accumulated_value", 0), 0)))
        accumulated_after = int(max(0, accumulated_before + increment))
        merged_extensions = dict(_as_map(existing.get("extensions")))
        merged_extensions.update(
            {
                "last_increment": int(increment),
                "last_policy_id": accumulation_policy_id,
                "last_environment_scale_permille": int(update.get("environment_scale_permille", 1000)),
                "last_load_scale_permille": int(update.get("load_scale_permille", 1000)),
                "last_base_increment": int(base_increment),
                "last_update_origin": dict(update.get("extensions") or {}),
            }
        )
        next_row = build_wear_state(
            target_id=key[0],
            wear_type_id=key[1],
            accumulated_value=accumulated_after,
            last_update_tick=int(max(0, _as_int(current_tick, 0))),
            extensions=merged_extensions,
        )
        rows_by_key[key] = next_row
        limit_value = int(_as_int(wear_type_row.get("hazard_threshold", 100000), 100000))
        if limit_value <= 0:
            limit_value = 1
        before_score = wear_ratio_permille(accumulated_value=accumulated_before, hazard_threshold=limit_value)
        after_score = wear_ratio_permille(accumulated_value=accumulated_after, hazard_threshold=limit_value)
        if before_score < 1000 and after_score >= 1000:
            threshold_crossings.append(
                {
                    "target_id": key[0],
                    "wear_type_id": key[1],
                    "hazard_threshold": int(limit_value),
                    "accumulated_value": int(accumulated_after),
                    "wear_ratio_permille": int(after_score),
                }
            )
        processed_keys.append(key_token)

    out_rows = [dict(rows_by_key[key]) for key in sorted(rows_by_key.keys())]
    return {
        "wear_rows": out_rows,
        "processed_update_keys": _sorted_tokens(processed_keys),
        "deferred_update_keys": _sorted_tokens(deferred_keys),
        "threshold_crossings": sorted(
            [dict(row) for row in threshold_crossings],
            key=lambda row: (str(row.get("target_id", "")), str(row.get("wear_type_id", ""))),
        ),
        "cost_units": int(len(processed_keys)),
        "budget_outcome": "degraded" if deferred_keys else "complete",
    }


def service_wear_rows(
    *,
    wear_rows: object,
    target_id: str,
    wear_type_ids: object,
    reset_fraction_numerator: int,
    reset_fraction_denominator: int,
    current_tick: int,
) -> dict:
    rows_by_key = wear_rows_by_target_and_type(wear_rows)
    target_token = str(target_id or "").strip()
    selected_wear_types = set(_sorted_tokens(list(wear_type_ids or [])))
    numerator = int(max(0, _as_int(reset_fraction_numerator, 0)))
    denominator = int(max(1, _as_int(reset_fraction_denominator, 1)))
    changed_rows: List[dict] = []

    for key in sorted(rows_by_key.keys()):
        row = dict(rows_by_key.get(key) or {})
        if str(row.get("target_id", "")).strip() != target_token:
            continue
        wear_type_id = str(row.get("wear_type_id", "")).strip()
        if selected_wear_types and wear_type_id not in selected_wear_types:
            continue
        before_value = int(max(0, _as_int(row.get("accumulated_value", 0), 0)))
        reduced = int((before_value * max(0, denominator - numerator)) // denominator)
        ext = dict(_as_map(row.get("extensions")))
        ext.update(
            {
                "serviced_tick": int(max(0, _as_int(current_tick, 0))),
                "service_reduction": int(before_value - reduced),
                "service_fraction": {
                    "numerator": int(numerator),
                    "denominator": int(denominator),
                },
            }
        )
        rows_by_key[key] = build_wear_state(
            target_id=target_token,
            wear_type_id=wear_type_id,
            accumulated_value=int(reduced),
            last_update_tick=int(max(0, _as_int(current_tick, 0))),
            extensions=ext,
        )
        changed_rows.append(
            {
                "target_id": target_token,
                "wear_type_id": wear_type_id,
                "before": int(before_value),
                "after": int(reduced),
            }
        )

    return {
        "wear_rows": [dict(rows_by_key[key]) for key in sorted(rows_by_key.keys())],
        "serviced_rows": [dict(row) for row in sorted(changed_rows, key=lambda row: str(row.get("wear_type_id", "")))],
    }


def wear_summary_for_target(
    *,
    wear_rows: object,
    target_ids: object,
    wear_type_rows: Mapping[str, dict] | None,
) -> dict:
    rows_by_key = wear_rows_by_target_and_type(wear_rows)
    type_rows = dict(wear_type_rows or {})
    targets = _sorted_tokens(list(target_ids or []))
    summary_rows: List[dict] = []
    for target_id in targets:
        for wear_type_id in sorted(type_rows.keys()):
            row = dict(rows_by_key.get((target_id, wear_type_id)) or {})
            if not row:
                continue
            type_row = dict(type_rows.get(wear_type_id) or {})
            limit_value = int(_as_int(type_row.get("hazard_threshold", 100000), 100000))
            if limit_value <= 0:
                limit_value = 1
            accumulated = int(max(0, _as_int(row.get("accumulated_value", 0), 0)))
            score_value = int(wear_ratio_permille(accumulated_value=accumulated, hazard_threshold=limit_value))
            summary_rows.append(
                {
                    "target_id": target_id,
                    "wear_type_id": wear_type_id,
                    "accumulated_value": accumulated,
                    "hazard_threshold": int(limit_value),
                    "wear_ratio_permille": int(score_value),
                    "critical": bool(score_value >= 1000),
                }
            )
    return {
        "rows": sorted(summary_rows, key=lambda row: (str(row.get("target_id", "")), str(row.get("wear_type_id", "")))),
        "critical_count": int(len([row for row in summary_rows if bool(row.get("critical", False))])),
    }


__all__ = [
    "apply_wear_updates",
    "build_wear_state",
    "normalize_wear_state_rows",
    "service_wear_rows",
    "track_wear_modifier_permille",
    "wear_accumulation_policy_rows_by_id",
    "wear_ratio_permille",
    "wear_rows_by_target_and_type",
    "wear_summary_for_target",
    "wear_type_rows_by_id",
]
