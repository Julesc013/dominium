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
    transitions: List[dict] = []
    transition_ids = set()
    for transition in sorted((item for item in transitions_raw if isinstance(item, dict)), key=lambda item: str(item.get("transition_id", ""))):
        transition_id = str(transition.get("transition_id", "")).strip()
        from_state_id = str(transition.get("from_state_id", "")).strip()
        to_state_id = str(transition.get("to_state_id", "")).strip()
        trigger_process_id = str(transition.get("trigger_process_id", "")).strip()
        if not transition_id or not from_state_id or not to_state_id or not trigger_process_id:
            raise StateMachineError(
                REFUSAL_CORE_STATE_INVALID,
                "state machine transition missing required fields",
                {"machine_id": machine_id, "transition_id": transition_id},
            )
        if transition_id in transition_ids:
            raise StateMachineError(
                REFUSAL_CORE_STATE_INVALID,
                "state machine transition_id must be unique",
                {"machine_id": machine_id, "transition_id": transition_id},
            )
        transition_ids.add(transition_id)
        transitions.append(
            {
                "transition_id": transition_id,
                "from_state_id": from_state_id,
                "to_state_id": to_state_id,
                "trigger_process_id": trigger_process_id,
                "priority": int(_as_int(transition.get("priority", 0), 0)),
                "extensions": dict(transition.get("extensions") or {}),
            }
        )
    return {
        "schema_version": "1.0.0",
        "machine_id": machine_id,
        "machine_type_id": machine_type_id,
        "state_id": state_id,
        "transitions": transitions,
        "extensions": dict(payload.get("extensions") or {}),
    }


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
    candidates: List[dict] = []
    for transition in list(machine.get("transitions") or []):
        row = dict(transition)
        if str(row.get("from_state_id", "")).strip() != state_id:
            continue
        if str(row.get("trigger_process_id", "")).strip() != trigger:
            continue
        if requested_transition_id and str(row.get("transition_id", "")).strip() != requested_transition_id:
            continue
        candidates.append(row)
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
    # Conflict resolution is deterministic: highest priority first, then lexical transition_id.
    selected = sorted(
        candidates,
        key=lambda row: (
            -1 * int(_as_int(row.get("priority", 0), 0)),
            str(row.get("transition_id", "")),
        ),
    )[0]
    machine["state_id"] = str(selected.get("to_state_id", "")).strip()
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
            "to_state_id": str(selected.get("to_state_id", "")),
            "priority": int(_as_int(selected.get("priority", 0), 0)),
            "trigger_process_id": trigger,
            "applied_tick": int(max(0, _as_int(current_tick, 0))),
        },
    }

