"""Deterministic core HazardModel helpers."""

from __future__ import annotations

from typing import Mapping


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
    return {
        "schema_version": "1.0.0",
        "hazard_id": hazard_id,
        "hazard_type_id": hazard_type_id,
        "target_id": target_id,
        "accumulation": accumulation,
        "threshold": threshold,
        "consequence_process_id": consequence_process_id,
        "extensions": dict(payload.get("extensions") or {}),
    }


def hazard_triggered(hazard_row: Mapping[str, object]) -> bool:
    row = normalize_hazard_model(hazard_row)
    return int(row.get("accumulation", 0)) >= int(row.get("threshold", 0))


def accumulate_hazard(hazard_row: Mapping[str, object], *, delta: int) -> dict:
    row = normalize_hazard_model(hazard_row)
    updated_accumulation = int(max(0, int(row.get("accumulation", 0)) + int(_as_int(delta, 0))))
    row["accumulation"] = updated_accumulation
    return {
        "hazard": row,
        "triggered": bool(hazard_triggered(row)),
    }

