"""Deterministic GEO-2 render policies."""

from .floating_origin_policy import (
    REFUSAL_GEO_RENDER_REBASE_INVALID,
    REFUSAL_GEO_RENDER_TRUTH_MUTATION,
    apply_floating_origin,
    choose_floating_origin_offset,
)

__all__ = [
    "REFUSAL_GEO_RENDER_REBASE_INVALID",
    "REFUSAL_GEO_RENDER_TRUTH_MUTATION",
    "apply_floating_origin",
    "choose_floating_origin_offset",
]
