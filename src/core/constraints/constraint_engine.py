"""Deterministic core ConstraintComponent helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping


REFUSAL_CORE_CONSTRAINT_INVALID = "refusal.core.constraint.invalid"
REFUSAL_CORE_CONSTRAINT_PARTICIPANT_MISSING = "refusal.core.constraint.participant_missing"


class ConstraintError(ValueError):
    """Deterministic constraint refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _registry_rows(payload: Mapping[str, object] | None, list_key: str) -> List[dict]:
    root = dict(payload or {})
    rows = root.get(list_key)
    if not isinstance(rows, list):
        rows = (dict(root.get("record") or {})).get(list_key)
    if not isinstance(rows, list):
        return []
    return [dict(row) for row in rows if isinstance(row, dict)]


def normalize_constraint_type(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    constraint_type_id = str(payload.get("constraint_type_id", "")).strip()
    if not constraint_type_id:
        raise ConstraintError(
            REFUSAL_CORE_CONSTRAINT_INVALID,
            "constraint type missing constraint_type_id",
            {"constraint_type_id": constraint_type_id},
        )
    enforcement_tier = str(payload.get("enforcement_tier", "")).strip() or "micro"
    if enforcement_tier not in {"macro", "meso", "micro"}:
        raise ConstraintError(
            REFUSAL_CORE_CONSTRAINT_INVALID,
            "constraint type enforcement_tier must be macro|meso|micro",
            {"constraint_type_id": constraint_type_id, "enforcement_tier": enforcement_tier},
        )
    return {
        "schema_version": "1.0.0",
        "constraint_type_id": constraint_type_id,
        "description": str(payload.get("description", "")).strip(),
        "applicable_entity_kinds": _sorted_unique_strings(payload.get("applicable_entity_kinds")),
        "enforcement_tier": enforcement_tier,
        "extensions": dict(payload.get("extensions") or {}),
    }


def constraint_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _registry_rows(registry_payload, "constraint_types")
    out: Dict[str, dict] = {}
    for row in sorted(rows, key=lambda item: str(item.get("constraint_type_id", ""))):
        normalized = normalize_constraint_type(row)
        out[str(normalized.get("constraint_type_id", ""))] = normalized
    return out


def normalize_constraint_component(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    constraint_id = str(payload.get("constraint_id", "")).strip()
    constraint_type_id = str(payload.get("constraint_type_id", "")).strip()
    enforcement_policy_id = str(payload.get("enforcement_policy_id", "")).strip()
    participant_ids = _sorted_unique_strings(payload.get("participant_ids"))
    if not participant_ids:
        participant_ids = _sorted_unique_strings(payload.get("participants"))
    if not constraint_id or not constraint_type_id or not enforcement_policy_id or not participant_ids:
        raise ConstraintError(
            REFUSAL_CORE_CONSTRAINT_INVALID,
            "constraint component missing required identifiers or participant_ids",
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
    active_value = payload.get("active")
    active = True if active_value is None else bool(active_value)
    return {
        "schema_version": "1.0.0",
        "constraint_id": constraint_id,
        "constraint_type_id": constraint_type_id,
        "participant_ids": participant_ids,
        # Legacy alias preserved for compatibility while component callers migrate.
        "participants": list(participant_ids),
        "parameters": dict(parameters),
        "enforcement_policy_id": enforcement_policy_id,
        "active": bool(active),
        "extensions": dict(extensions),
    }


def validate_constraint_participants(constraint_row: Mapping[str, object], known_participant_ids: List[str]) -> bool:
    normalized = normalize_constraint_component(constraint_row)
    known = set(_sorted_unique_strings(list(known_participant_ids or [])))
    for participant_id in list(normalized.get("participant_ids") or []):
        if str(participant_id) not in known:
            return False
    return True


def tick_constraints(
    *,
    constraint_rows: object,
    known_participant_ids: object,
    max_constraints: int | None = None,
    cost_units_per_constraint: int = 1,
) -> dict:
    """Evaluate active constraints in deterministic order with budget-aware degradation."""

    known = set(_sorted_unique_strings(list(known_participant_ids or [])) if isinstance(known_participant_ids, list) else [])
    normalized_rows: List[dict] = []
    for row in list(constraint_rows or []):
        if not isinstance(row, dict):
            continue
        normalized_rows.append(normalize_constraint_component(row))
    normalized_rows = sorted(normalized_rows, key=lambda item: str(item.get("constraint_id", "")))

    limit = len(normalized_rows)
    if max_constraints is not None:
        limit = min(limit, max(0, _as_int(max_constraints, len(normalized_rows))))

    processed = normalized_rows[:limit]
    deferred = normalized_rows[limit:]

    violations: List[dict] = []
    evaluated: List[dict] = []
    for row in processed:
        if not bool(row.get("active", True)):
            evaluated.append(
                {
                    "constraint_id": str(row.get("constraint_id", "")),
                    "constraint_type_id": str(row.get("constraint_type_id", "")),
                    "status": "inactive",
                }
            )
            continue
        missing = sorted(
            participant_id
            for participant_id in list(row.get("participant_ids") or [])
            if str(participant_id) not in known
        )
        if missing:
            violations.append(
                {
                    "constraint_id": str(row.get("constraint_id", "")),
                    "reason_code": REFUSAL_CORE_CONSTRAINT_PARTICIPANT_MISSING,
                    "missing_participant_ids": missing,
                }
            )
            evaluated.append(
                {
                    "constraint_id": str(row.get("constraint_id", "")),
                    "constraint_type_id": str(row.get("constraint_type_id", "")),
                    "status": "invalid_participants",
                }
            )
            continue
        evaluated.append(
            {
                "constraint_id": str(row.get("constraint_id", "")),
                "constraint_type_id": str(row.get("constraint_type_id", "")),
                "status": "valid",
                "participant_ids": list(row.get("participant_ids") or []),
                "enforcement_policy_id": str(row.get("enforcement_policy_id", "")),
            }
        )

    cost_units = int(max(0, _as_int(cost_units_per_constraint, 1))) * int(len(processed))
    budget_outcome = "complete" if not deferred else "degraded"
    return {
        "constraints": normalized_rows,
        "evaluated": evaluated,
        "violations": violations,
        "deferred_constraint_ids": [str(row.get("constraint_id", "")) for row in deferred],
        "processed_count": int(len(processed)),
        "deferred_count": int(len(deferred)),
        "cost_units": int(cost_units),
        "budget_outcome": budget_outcome,
    }


def build_constraint_enforcement_hooks(
    *,
    constraint_rows: object,
    known_participant_ids: object,
    max_constraints: int | None = None,
    cost_units_per_constraint: int = 1,
) -> dict:
    """Build deterministic, policy-filtered hook payloads for downstream domains."""

    ticked = tick_constraints(
        constraint_rows=constraint_rows,
        known_participant_ids=known_participant_ids,
        max_constraints=max_constraints,
        cost_units_per_constraint=cost_units_per_constraint,
    )
    hooks: Dict[str, List[dict]] = {}
    for row in list(ticked.get("evaluated") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "")) != "valid":
            continue
        constraint_type_id = str(row.get("constraint_type_id", "")).strip()
        hooks.setdefault(constraint_type_id, []).append(dict(row))
    for key in sorted(hooks.keys()):
        hooks[key] = sorted(hooks[key], key=lambda item: str(item.get("constraint_id", "")))
    ticked["enforcement_hooks"] = dict((key, hooks[key]) for key in sorted(hooks.keys()))
    return ticked
