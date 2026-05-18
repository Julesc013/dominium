"""Deterministic core StateMachineComponent helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping


REFUSAL_CORE_STATE_INVALID = "refusal.core.state_machine.invalid"
REFUSAL_CORE_STATE_TRANSITION_MISSING = "refusal.core.state_machine.transition_missing"


class StateMachineError(ValueError):
    """Deterministic state machine refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def normalize_state_transition(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    transition_id = str(payload.get("transition_id", "")).strip()
    from_state = str(payload.get("from_state", payload.get("from_state_id", ""))).strip()
    to_state = str(payload.get("to_state", payload.get("to_state_id", ""))).strip()
    trigger_process_id = str(payload.get("trigger_process_id", "")).strip()
    if not transition_id or not from_state or not to_state or not trigger_process_id:
        raise StateMachineError(
            REFUSAL_CORE_STATE_INVALID,
            "state transition missing required fields",
            {
                "transition_id": transition_id,
                "from_state": from_state,
                "to_state": to_state,
                "trigger_process_id": trigger_process_id,
            },
        )
    guard_conditions = payload.get("guard_conditions")
    if guard_conditions is None:
        guard_conditions = {}
    if not isinstance(guard_conditions, dict):
        raise StateMachineError(
            REFUSAL_CORE_STATE_INVALID,
            "state transition guard_conditions must be object",
            {"transition_id": transition_id},
        )
    return {
        "schema_version": "1.0.0",
        "transition_id": transition_id,
        "from_state": from_state,
        "to_state": to_state,
        "trigger_process_id": trigger_process_id,
        "guard_conditions": dict(guard_conditions),
        "priority": int(_as_int(payload.get("priority", 0), 0)),
        "extensions": dict(payload.get("extensions") or {}),
    }


def normalize_state_machine(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    machine_id = str(payload.get("machine_id", "")).strip()
    machine_type_id = str(payload.get("machine_type_id", "")).strip()
    state_id = str(payload.get("state_id", "")).strip()
    if not machine_id or not machine_type_id or not state_id:
        raise StateMachineError(
            REFUSAL_CORE_STATE_INVALID,
            "state machine missing required machine_id/machine_type_id/state_id",
            {"machine_id": machine_id, "machine_type_id": machine_type_id, "state_id": state_id},
        )

    transitions_raw = payload.get("transitions")
    if transitions_raw is None:
        transitions_raw = []
    if not isinstance(transitions_raw, list):
        raise StateMachineError(
            REFUSAL_CORE_STATE_INVALID,
            "state machine transitions must be an array",
            {"machine_id": machine_id},
        )

    transition_rows_raw = payload.get("transition_rows")
    if transition_rows_raw is None:
        transition_rows_raw = []
    if not isinstance(transition_rows_raw, list):
        raise StateMachineError(
            REFUSAL_CORE_STATE_INVALID,
            "state machine transition_rows must be an array",
            {"machine_id": machine_id},
        )

    transition_ids: List[str] = []
    transition_rows: Dict[str, dict] = {}

    for item in transitions_raw:
        if isinstance(item, str):
            token = str(item).strip()
            if token:
                transition_ids.append(token)
            continue
        if not isinstance(item, dict):
            continue
        normalized = normalize_state_transition(item)
        transition_id = str(normalized.get("transition_id", ""))
        transition_ids.append(transition_id)
        transition_rows[transition_id] = normalized

    for item in transition_rows_raw:
        if not isinstance(item, dict):
            continue
        normalized = normalize_state_transition(item)
        transition_id = str(normalized.get("transition_id", ""))
        transition_rows[transition_id] = normalized
        transition_ids.append(transition_id)

    ordered_transition_ids: List[str] = []
    seen = set()
    for token in sorted(str(item).strip() for item in transition_ids if str(item).strip()):
        if token in seen:
            continue
        seen.add(token)
        ordered_transition_ids.append(token)

    for transition_id in list(transition_rows.keys()):
        if transition_id not in seen:
            ordered_transition_ids.append(transition_id)
            seen.add(transition_id)

    if not ordered_transition_ids:
        raise StateMachineError(
            REFUSAL_CORE_STATE_INVALID,
            "state machine must declare at least one transition id",
            {"machine_id": machine_id},
        )

    ordered_transition_rows = [
        dict(transition_rows[transition_id])
        for transition_id in sorted(transition_rows.keys())
    ]

    return {
        "schema_version": "1.0.0",
        "machine_id": machine_id,
        "machine_type_id": machine_type_id,
        "state_id": state_id,
        "transitions": list(ordered_transition_ids),
        "transition_rows": ordered_transition_rows,
        "extensions": dict(payload.get("extensions") or {}),
    }


def _candidate_transitions(
    machine_row: Mapping[str, object],
    *,
    trigger_process_id: str,
    requested_transition_id: str,
) -> List[dict]:
    state_id = str(machine_row.get("state_id", "")).strip()
    trigger = str(trigger_process_id).strip()
    transition_rows = [
        dict(item)
        for item in list(machine_row.get("transition_rows") or [])
        if isinstance(item, dict)
    ]
    candidates: List[dict] = []
    for row in transition_rows:
        if str(row.get("from_state", "")).strip() != state_id:
            continue
        if str(row.get("trigger_process_id", "")).strip() != trigger:
            continue
        if requested_transition_id and str(row.get("transition_id", "")).strip() != requested_transition_id:
            continue
        candidates.append(row)
    return candidates


def apply_transition(
    machine_row: Mapping[str, object],
    *,
    trigger_process_id: str,
    transition_id: str = "",
    current_tick: int = 0,
) -> dict:
    machine = normalize_state_machine(machine_row)
    state_id = str(machine.get("state_id", ""))
    requested_transition_id = str(transition_id).strip()
    trigger = str(trigger_process_id).strip()
    candidates = _candidate_transitions(
        machine,
        trigger_process_id=trigger,
        requested_transition_id=requested_transition_id,
    )
    if not candidates:
        raise StateMachineError(
            REFUSAL_CORE_STATE_TRANSITION_MISSING,
            "no deterministic transition available for process trigger",
            {
                "machine_id": str(machine.get("machine_id", "")),
                "state_id": state_id,
                "trigger_process_id": trigger,
                "transition_id": requested_transition_id,
            },
        )

    selected = sorted(
        candidates,
        key=lambda row: (
            -1 * int(_as_int(row.get("priority", 0), 0)),
            str(row.get("transition_id", "")),
        ),
    )[0]
    machine["state_id"] = str(selected.get("to_state", "")).strip()
    machine_extensions = dict(machine.get("extensions") or {})
    machine_extensions["last_transition"] = {
        "transition_id": str(selected.get("transition_id", "")),
        "trigger_process_id": trigger,
        "applied_tick": int(max(0, _as_int(current_tick, 0))),
    }
    machine["extensions"] = machine_extensions

    return {
        "machine": machine,
        "applied_transition": {
            "transition_id": str(selected.get("transition_id", "")),
            "from_state_id": state_id,
            "to_state_id": str(selected.get("to_state", "")),
            "priority": int(_as_int(selected.get("priority", 0), 0)),
            "trigger_process_id": trigger,
            "applied_tick": int(max(0, _as_int(current_tick, 0))),
        },
    }


def tick_state_machines(
    *,
    machine_rows: object,
    trigger_rows: object,
    current_tick: int,
    max_machines: int | None = None,
    cost_units_per_machine: int = 1,
) -> dict:
    """Apply process-triggered transitions deterministically across a machine set."""

    machines: Dict[str, dict] = {}
    for row in list(machine_rows or []):
        if not isinstance(row, dict):
            continue
        normalized = normalize_state_machine(row)
        machines[str(normalized.get("machine_id", ""))] = normalized

    ordered_machine_ids = sorted(machines.keys())
    limit = len(ordered_machine_ids)
    if max_machines is not None:
        limit = min(limit, max(0, _as_int(max_machines, len(ordered_machine_ids))))
    processed_machine_ids = set(ordered_machine_ids[:limit])

    normalized_triggers: List[dict] = []
    for row in list(trigger_rows or []):
        if not isinstance(row, dict):
            continue
        machine_id = str(row.get("machine_id", "")).strip()
        trigger_process_id = str(row.get("trigger_process_id", "")).strip()
        if not machine_id or not trigger_process_id:
            continue
        normalized_triggers.append(
            {
                "machine_id": machine_id,
                "trigger_process_id": trigger_process_id,
                "transition_id": str(row.get("transition_id", "")).strip(),
                "order": int(_as_int(row.get("order", 0), 0)),
            }
        )
    normalized_triggers = sorted(
        normalized_triggers,
        key=lambda row: (
            str(row.get("machine_id", "")),
            str(row.get("trigger_process_id", "")),
            str(row.get("transition_id", "")),
            int(_as_int(row.get("order", 0), 0)),
        ),
    )

    applied: List[dict] = []
    refusals: List[dict] = []
    for trigger in normalized_triggers:
        machine_id = str(trigger.get("machine_id", ""))
        if machine_id not in processed_machine_ids:
            continue
        machine = dict(machines.get(machine_id) or {})
        if not machine:
            refusals.append(
                {
                    "machine_id": machine_id,
                    "reason_code": REFUSAL_CORE_STATE_INVALID,
                    "message": "machine is missing",
                }
            )
            continue
        try:
            transitioned = apply_transition(
                machine,
                trigger_process_id=str(trigger.get("trigger_process_id", "")),
                transition_id=str(trigger.get("transition_id", "")),
                current_tick=int(max(0, _as_int(current_tick, 0))),
            )
        except StateMachineError as err:
            refusals.append(
                {
                    "machine_id": machine_id,
                    "reason_code": str(err.reason_code),
                    "message": str(err),
                    "details": dict(err.details),
                }
            )
            continue
        machines[machine_id] = dict(transitioned.get("machine") or {})
        row = dict(transitioned.get("applied_transition") or {})
        row["machine_id"] = machine_id
        applied.append(row)

    updated_rows = [dict(machines[key]) for key in sorted(machines.keys())]
    deferred_machine_ids = [machine_id for machine_id in ordered_machine_ids if machine_id not in processed_machine_ids]
    cost_units = int(max(0, _as_int(cost_units_per_machine, 1))) * int(len(processed_machine_ids))

    return {
        "machines": updated_rows,
        "applied_transitions": sorted(
            applied,
            key=lambda row: (
                str(row.get("machine_id", "")),
                int(_as_int(row.get("applied_tick", 0), 0)),
                str(row.get("transition_id", "")),
            ),
        ),
        "refusals": sorted(
            refusals,
            key=lambda row: (
                str(row.get("machine_id", "")),
                str(row.get("reason_code", "")),
            ),
        ),
        "processed_count": int(len(processed_machine_ids)),
        "deferred_machine_ids": deferred_machine_ids,
        "deferred_count": int(len(deferred_machine_ids)),
        "cost_units": int(cost_units),
        "budget_outcome": "complete" if not deferred_machine_ids else "degraded",
    }
