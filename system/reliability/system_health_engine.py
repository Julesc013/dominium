"""SYS-6 deterministic system health aggregation engine."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def build_system_health_state_row(
    *,
    system_id: str,
    aggregated_hazard_levels: Mapping[str, object] | None,
    entropy_value: int | None,
    last_update_tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    system_token = str(system_id or "").strip()
    if not system_token:
        return {}
    hazards = dict(
        (
            str(key).strip(),
            int(max(0, _as_int(value, 0))),
        )
        for key, value in sorted(_as_map(aggregated_hazard_levels).items(), key=lambda item: str(item[0]))
        if str(key).strip()
    )
    payload = {
        "schema_version": "1.0.0",
        "system_id": system_token,
        "aggregated_hazard_levels": hazards,
        "entropy_value": None if entropy_value is None else int(max(0, _as_int(entropy_value, 0))),
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": str(deterministic_fingerprint or "").strip(),
        "extensions": _as_map(extensions),
    }
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_system_health_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    by_system: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("system_id", "")),
            int(max(0, _as_int(item.get("last_update_tick", 0), 0))),
        ),
    ):
        normalized = build_system_health_state_row(
            system_id=str(row.get("system_id", "")).strip(),
            aggregated_hazard_levels=_as_map(row.get("aggregated_hazard_levels")),
            entropy_value=(
                None
                if row.get("entropy_value") is None
                else int(max(0, _as_int(row.get("entropy_value", 0), 0)))
            ),
            last_update_tick=int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
            deterministic_fingerprint=str(row.get("deterministic_fingerprint", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        system_id = str(normalized.get("system_id", "")).strip()
        if system_id:
            by_system[system_id] = normalized
    return [dict(by_system[key]) for key in sorted(by_system.keys())]


def system_health_rows_by_system(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in normalize_system_health_state_rows(rows):
        system_id = str(row.get("system_id", "")).strip()
        if system_id:
            out[system_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _capsule_by_system(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        rows = []
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("system_id", "")),
    ):
        system_id = str(row.get("system_id", "")).strip()
        capsule_id = str(row.get("capsule_id", "")).strip()
        if system_id and capsule_id:
            out[system_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _system_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out = []
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("system_id", "")),
    ):
        system_id = str(row.get("system_id", "")).strip()
        if not system_id:
            continue
        out.append(row)
    return out


def _hazard_map_for_system(
    *,
    system_row: Mapping[str, object],
    capsule_row: Mapping[str, object] | None,
    model_hazard_rows: object,
    safety_event_rows: object,
    chem_degradation_event_rows: object,
) -> dict:
    system_id = str(system_row.get("system_id", "")).strip()
    system_ext = _as_map(system_row.get("extensions"))
    hazards: Dict[str, int] = {}

    for key_name in ("hazard_levels", "hazard_map", "hazard_inputs", "aggregated_hazard_levels"):
        for hazard_id, value in sorted(_as_map(system_ext.get(key_name)).items(), key=lambda item: str(item[0])):
            token = str(hazard_id).strip()
            if not token:
                continue
            hazards[token] = max(hazards.get(token, 0), int(max(0, _as_int(value, 0))))

    unresolved_count = int(max(0, _as_int(system_ext.get("unresolved_hazard_count", 0), 0)))
    if unresolved_count > 0:
        hazards["hazard.system.unresolved"] = max(hazards.get("hazard.system.unresolved", 0), unresolved_count * 100)

    if isinstance(capsule_row, Mapping):
        capsule_ext = _as_map(capsule_row.get("extensions"))
        capsule_hazard = int(max(0, _as_int(capsule_ext.get("hazard_level", 0), 0)))
        if capsule_hazard > 0:
            hazards["hazard.system.capsule"] = max(hazards.get("hazard.system.capsule", 0), capsule_hazard)

    for row in sorted(
        (dict(item) for item in list(model_hazard_rows or []) if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("target_id", "")),
            str(item.get("hazard_id", "")),
        ),
    ):
        target_id = str(row.get("target_id", "")).strip()
        if target_id != system_id:
            continue
        hazard_id = str(row.get("hazard_id", "")).strip() or str(row.get("effect_type_id", "")).strip() or "hazard.model"
        value = int(max(0, _as_int(row.get("hazard_level", row.get("severity", row.get("value", 0))), 0)))
        hazards[hazard_id] = max(hazards.get(hazard_id, 0), value)

    for row in sorted(
        (dict(item) for item in list(safety_event_rows or []) if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("target_id", "")),
            str(item.get("event_id", "")),
        ),
    ):
        target_ids = _sorted_tokens(list(row.get("target_ids") or []))
        target_id = str(row.get("target_id", "")).strip()
        if system_id not in set(target_ids + ([target_id] if target_id else [])):
            continue
        hazard_id = "hazard.safety.{}".format(str(row.get("event_type_id", "event")).strip().replace("event.", ""))[:64]
        severity = int(max(0, _as_int(row.get("severity", 0), 0)))
        hazards[hazard_id] = max(hazards.get(hazard_id, 0), severity * 100)

    for row in sorted(
        (dict(item) for item in list(chem_degradation_event_rows or []) if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("target_id", "")),
            str(item.get("event_id", "")),
        ),
    ):
        if str(row.get("target_id", "")).strip() != system_id:
            continue
        level = int(max(0, _as_int(row.get("level_after", row.get("severity", 0)), 0)))
        hazard_kind = str(row.get("degradation_kind", "")).strip()
        hazard_id = "hazard.chem.{}".format(hazard_kind or "degradation")
        hazards[hazard_id] = max(hazards.get(hazard_id, 0), level)

    return dict((key, int(hazards[key])) for key in sorted(hazards.keys()))


def _entropy_for_system(
    *,
    system_row: Mapping[str, object],
    entropy_state_rows: object,
) -> int | None:
    system_id = str(system_row.get("system_id", "")).strip()
    for row in sorted(
        (dict(item) for item in list(entropy_state_rows or []) if isinstance(item, Mapping)),
        key=lambda item: str(item.get("target_id", "")),
    ):
        if str(row.get("target_id", "")).strip() != system_id:
            continue
        for token in ("entropy_value", "entropy_raw", "value", "entropy_index"):
            if row.get(token) is not None:
                return int(max(0, _as_int(row.get(token, 0), 0)))
    ext = _as_map(system_row.get("extensions"))
    if ext.get("entropy_value") is not None:
        return int(max(0, _as_int(ext.get("entropy_value", 0), 0)))
    return None


def evaluate_system_health_tick(
    *,
    current_tick: int,
    system_rows: object,
    system_macro_capsule_rows: object,
    previous_health_rows: object,
    model_hazard_rows: object = None,
    safety_event_rows: object = None,
    chem_degradation_event_rows: object = None,
    entropy_state_rows: object = None,
    high_priority_system_ids: object = None,
    max_system_updates_per_tick: int = 256,
    low_priority_update_stride: int = 4,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    max_updates = int(max(1, _as_int(max_system_updates_per_tick, 256)))
    low_priority_stride = int(max(1, _as_int(low_priority_update_stride, 4)))

    systems = _system_rows(system_rows)
    capsules_by_system = _capsule_by_system(system_macro_capsule_rows)
    previous_by_system = system_health_rows_by_system(previous_health_rows)
    high_priority = set(_sorted_tokens(list(high_priority_system_ids or [])))

    output_by_system: Dict[str, dict] = dict((key, dict(value)) for key, value in previous_by_system.items())
    decision_rows: List[dict] = []
    deferred_rows: List[dict] = []
    processed_system_ids: List[str] = []

    update_count = 0
    for idx, system_row in enumerate(systems):
        system_id = str(system_row.get("system_id", "")).strip()
        if not system_id:
            continue
        system_ext = _as_map(system_row.get("extensions"))
        priority_class = str(system_ext.get("reliability_priority_class", "background")).strip() or "background"
        is_high_priority = (system_id in high_priority) or priority_class in {"inspection", "hazard", "roi"}

        if (not is_high_priority) and ((tick + idx) % low_priority_stride != 0):
            deferred_rows.append(
                {
                    "system_id": system_id,
                    "reason_code": "degrade.system.health_tick_stride",
                    "priority_class": priority_class,
                }
            )
            decision_rows.append(
                {
                    "decision_id": "decision.system.health.defer.{}".format(
                        canonical_sha256({"tick": tick, "system_id": system_id, "reason_code": "stride"})[:16]
                    ),
                    "tick": int(tick),
                    "process_id": "process.system_health_tick",
                    "result": "deferred",
                    "reason_code": "degrade.system.health_tick_stride",
                    "extensions": {
                        "system_id": system_id,
                        "priority_class": priority_class,
                    },
                }
            )
            continue

        if update_count >= max_updates:
            deferred_rows.append(
                {
                    "system_id": system_id,
                    "reason_code": "degrade.system.health_budget",
                    "priority_class": priority_class,
                }
            )
            decision_rows.append(
                {
                    "decision_id": "decision.system.health.defer.{}".format(
                        canonical_sha256({"tick": tick, "system_id": system_id, "reason_code": "budget"})[:16]
                    ),
                    "tick": int(tick),
                    "process_id": "process.system_health_tick",
                    "result": "deferred",
                    "reason_code": "degrade.system.health_budget",
                    "extensions": {
                        "system_id": system_id,
                        "priority_class": priority_class,
                    },
                }
            )
            continue

        update_count += 1
        capsule_row = dict(capsules_by_system.get(system_id) or {})
        hazards = _hazard_map_for_system(
            system_row=system_row,
            capsule_row=capsule_row,
            model_hazard_rows=model_hazard_rows,
            safety_event_rows=safety_event_rows,
            chem_degradation_event_rows=chem_degradation_event_rows,
        )
        entropy_value = _entropy_for_system(system_row=system_row, entropy_state_rows=entropy_state_rows)
        health_row = build_system_health_state_row(
            system_id=system_id,
            aggregated_hazard_levels=hazards,
            entropy_value=entropy_value,
            last_update_tick=tick,
            deterministic_fingerprint="",
            extensions={
                "source_process_id": "process.system_health_tick",
                "priority_class": priority_class,
                "current_tier": str(system_row.get("current_tier", "")).strip(),
                "capsule_id": str(capsule_row.get("capsule_id", "")).strip() or None,
            },
        )
        if health_row:
            output_by_system[system_id] = dict(health_row)
            processed_system_ids.append(system_id)

    normalized_health_rows = normalize_system_health_state_rows(list(output_by_system.values()))
    normalized_decisions = [
        dict(row)
        for row in sorted(
            (dict(item) for item in decision_rows if isinstance(item, Mapping)),
            key=lambda item: (
                int(max(0, _as_int(item.get("tick", 0), 0))),
                str(item.get("decision_id", "")),
            ),
        )
    ]
    normalized_deferred = [
        dict(row)
        for row in sorted(
            (dict(item) for item in deferred_rows if isinstance(item, Mapping)),
            key=lambda item: (
                str(item.get("system_id", "")),
                str(item.get("reason_code", "")),
            ),
        )
    ]

    result = {
        "result": "complete",
        "processed_system_ids": _sorted_tokens(processed_system_ids),
        "system_health_state_rows": normalized_health_rows,
        "decision_log_rows": normalized_decisions,
        "deferred_rows": normalized_deferred,
        "degraded": bool(normalized_deferred),
        "degrade_reason": "degrade.system.health_scheduler_budget" if normalized_deferred else None,
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


__all__ = [
    "build_system_health_state_row",
    "normalize_system_health_state_rows",
    "system_health_rows_by_system",
    "evaluate_system_health_tick",
]
