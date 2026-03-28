"""CHEM-3 degradation engine exports."""

from .degradation_engine import (
    build_degradation_state,
    degradation_profile_rows_by_id,
    evaluate_degradation_tick,
    normalize_degradation_state_rows,
)

__all__ = [
    "build_degradation_state",
    "degradation_profile_rows_by_id",
    "evaluate_degradation_tick",
    "normalize_degradation_state_rows",
]

