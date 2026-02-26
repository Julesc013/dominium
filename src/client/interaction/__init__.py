"""Deterministic client interaction affordance/dispatch/preview package."""

from .affordance_generator import build_affordance_list
from .interaction_dispatch import (
    build_interaction_envelope,
    build_interaction_intent,
    execute_affordance,
    run_interaction_command,
    select_target,
)
from .inspection_overlays import build_inspection_overlays
from .preview_generator import generate_interaction_preview

__all__ = [
    "build_affordance_list",
    "build_interaction_envelope",
    "build_interaction_intent",
    "build_inspection_overlays",
    "execute_affordance",
    "generate_interaction_preview",
    "run_interaction_command",
    "select_target",
]
