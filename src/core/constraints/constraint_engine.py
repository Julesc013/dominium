"""Deterministic core ConstraintComponent helpers."""

from __future__ import annotations

from typing import List, Mapping


REFUSAL_CORE_CONSTRAINT_INVALID = "refusal.core.constraint.invalid"


class ConstraintError(ValueError):
    """Deterministic constraint refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def normalize_constraint_component(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    constraint_id = str(payload.get("constraint_id", "")).strip()
    constraint_type_id = str(payload.get("constraint_type_id", "")).strip()
    enforcement_policy_id = str(payload.get("enforcement_policy_id", "")).strip()
    participants = _sorted_unique_strings(payload.get("participants"))
    if not constraint_id or not constraint_type_id or not enforcement_policy_id or not participants:
        raise ConstraintError(
            REFUSAL_CORE_CONSTRAINT_INVALID,
            "constraint component missing required identifiers or participants",
            {
                "constraint_id": constraint_id,
                "constraint_type_id": constraint_type_id,
                "enforcement_policy_id": enforcement_policy_id,
            },
        )
    parameters = payload.get("parameters")
    if parameters is None:
        parameters = {}
    if not isinstance(parameters, dict):
        raise ConstraintError(
            REFUSAL_CORE_CONSTRAINT_INVALID,
            "constraint component parameters must be object",
            {"constraint_id": constraint_id},
        )
    extensions = payload.get("extensions")
    if not isinstance(extensions, dict):
        extensions = {}
    return {
        "schema_version": "1.0.0",
        "constraint_id": constraint_id,
        "constraint_type_id": constraint_type_id,
        "participants": participants,
        "parameters": dict(parameters),
        "enforcement_policy_id": enforcement_policy_id,
        "extensions": dict(extensions),
    }


def validate_constraint_participants(constraint_row: Mapping[str, object], known_participant_ids: List[str]) -> bool:
    normalized = normalize_constraint_component(constraint_row)
    known = set(_sorted_unique_strings(list(known_participant_ids or [])))
    for participant_id in list(normalized.get("participants") or []):
        if str(participant_id) not in known:
            return False
    return True

