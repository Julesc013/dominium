"""Deterministic core state-machine helpers."""

from .state_machine_engine import (
    StateMachineError,
    apply_transition,
    normalize_state_machine,
    normalize_state_transition,
    tick_state_machines,
)

__all__ = [
    "StateMachineError",
    "apply_transition",
    "normalize_state_machine",
    "normalize_state_transition",
    "tick_state_machines",
]
