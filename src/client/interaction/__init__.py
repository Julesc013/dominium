"""Deterministic client interaction affordance/dispatch/preview package."""

from .affordance_generator import build_affordance_list
from .interaction_dispatch import (
    build_interaction_envelope,
    build_interaction_intent,
    execute_affordance,
    run_interaction_command,
    select_target,
)

__all__ = [
    "build_affordance_list",
    "build_interaction_envelope",
    "build_interaction_intent",
    "execute_affordance",
    "run_interaction_command",
    "select_target",
]
