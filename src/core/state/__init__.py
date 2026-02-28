"""Deterministic core state-machine helpers."""

from .state_machine_engine import (
    StateMachineError,
    apply_transition,
    normalize_state_machine,
)

__all__ = [
    "StateMachineError",
    "apply_transition",
    "normalize_state_machine",
]

