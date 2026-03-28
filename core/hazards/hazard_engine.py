"""Deterministic core HazardModel helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_CORE_HAZARD_INVALID = "refusal.core.hazard.invalid"


class HazardError(ValueError):
    """Deterministic hazard refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def normalize_hazard_model(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    hazard_id = str(payload.get("hazard_id", "")).strip()
    hazard_type_id = str(payload.get("hazard_type_id", "")).strip()
    target_id = str(payload.get("target_id", "")).strip()
    consequence_process_id = str(payload.get("consequence_process_id", "")).strip()
    if not hazard_id or not hazard_type_id or not target_id or not consequence_process_id:
        raise HazardError(
            REFUSAL_CORE_HAZARD_INVALID,
            "hazard model missing required identifiers",
            {
                "hazard_id": hazard_id,
                "hazard_type_id": hazard_type_id,
                "target_id": target_id,
                "consequence_process_id": consequence_process_id,
            },
        )
    accumulation = int(max(0, _as_int(payload.get("accumulation", 0), 0)))
    threshold = int(max(0, _as_int(payload.get("threshold", 0), 0)))
    active_value = payload.get("active")
    active = True if active_value is None else bool(active_value)
    return {
        "schema_version": "1.0.0",
        "hazard_id": hazard_id,
        "hazard_type_id": hazard_type_id,
        "target_id": target_id,
        "accumulation": accumulation,
        "threshold": threshold,
        "consequence_process_id": consequence_process_id,
        "active": bool(active),
        "extensions": dict(payload.get("extensions") or {}),
    }


def hazard_triggered(hazard_row: Mapping[str, object]) -> bool:
    row = normalize_hazard_model(hazard_row)
    return bool(row.get("active", True)) and int(row.get("accumulation", 0)) >= int(row.get("threshold", 0))


def accumulate_hazard(hazard_row: Mapping[str, object], *, delta: int) -> dict:
    row = normalize_hazard_model(hazard_row)
    before = int(row.get("accumulation", 0))
    updated_accumulation = int(max(0, before + int(_as_int(delta, 0))))
    row["accumulation"] = updated_accumulation
    return {
        "hazard": row,
        "before": int(before),
        "after": int(updated_accumulation),
        "triggered": bool(hazard_triggered(row)),
    }


def tick_hazard_models(
    *,
    hazard_rows: object,
    current_tick: int,
    delta_by_hazard_id: Mapping[str, object] | None = None,
    max_hazards: int | None = None,
    cost_units_per_hazard: int = 1,
) -> dict:
    """Advance hazards in deterministic order with threshold-trigger consequence intents."""

    hazards: List[dict] = []
    for row in list(hazard_rows or []):
        if not isinstance(row, dict):
            continue
        hazards.append(normalize_hazard_model(row))
    hazards = sorted(hazards, key=lambda row: str(row.get("hazard_id", "")))

    limit = len(hazards)
    if max_hazards is not None:
        limit = min(limit, max(0, _as_int(max_hazards, len(hazards))))

    processed = hazards[:limit]
    deferred = hazards[limit:]
    delta_index = dict((str(key), _as_int(value, 0)) for key, value in sorted((dict(delta_by_hazard_id or {})).items(), key=lambda item: str(item[0])))

    consequences: List[dict] = []
    updated: List[dict] = []
    tick = int(max(0, _as_int(current_tick, 0)))
    for row in processed:
        hazard_id = str(row.get("hazard_id", ""))
        delta = int(_as_int(delta_index.get(hazard_id, 0), 0))
        if not bool(row.get("active", True)):
            updated.append(dict(row))
            continue
        before = int(row.get("accumulation", 0))
        stepped = accumulate_hazard(row, delta=delta)
        hazard = dict(stepped.get("hazard") or row)
        after = int(hazard.get("accumulation", before))
        threshold = int(max(0, _as_int(hazard.get("threshold", 0), 0)))
        extensions = dict(hazard.get("extensions") or {})
        previously_crossed = bool(extensions.get("threshold_crossed", False))
        allow_retrigger = bool(extensions.get("allow_retrigger", False))
        crossed = bool(before < threshold <= after) if threshold > 0 else False
        triggered = bool(crossed and (allow_retrigger or (not previously_crossed)))
        if triggered:
            extensions["threshold_crossed"] = True
            extensions["last_trigger_tick"] = int(tick)
        extensions["last_tick"] = int(tick)
        hazard["extensions"] = extensions
        updated.append(hazard)
        if not triggered:
            continue
        consequence = {
            "hazard_id": hazard_id,
            "hazard_type_id": str(hazard.get("hazard_type_id", "")),
            "target_id": str(hazard.get("target_id", "")),
            "consequence_process_id": str(hazard.get("consequence_process_id", "")),
            "tick": int(tick),
            "accumulation": int(after),
            "threshold": int(threshold),
            "deterministic_fingerprint": "",
        }
        seed = dict(consequence)
        seed["deterministic_fingerprint"] = ""
        consequence["deterministic_fingerprint"] = canonical_sha256(seed)
        consequences.append(consequence)

    updated.extend(dict(row) for row in deferred)
    updated = sorted(updated, key=lambda row: str(row.get("hazard_id", "")))
    deferred_ids = [str(row.get("hazard_id", "")) for row in deferred]

    return {
        "hazards": updated,
        "consequence_events": sorted(
            consequences,
            key=lambda row: (
                int(_as_int(row.get("tick", 0), 0)),
                str(row.get("hazard_id", "")),
                str(row.get("consequence_process_id", "")),
            ),
        ),
        "processed_count": int(len(processed)),
        "deferred_hazard_ids": deferred_ids,
        "deferred_count": int(len(deferred_ids)),
        "cost_units": int(max(0, _as_int(cost_units_per_hazard, 1))) * int(len(processed)),
        "budget_outcome": "complete" if not deferred_ids else "degraded",
    }
