"""MAT-7 materialization package exports."""

from .materialization_engine import (
    MaterializationError,
    REFUSAL_MATERIALIZATION_BUDGET_EXCEEDED,
    REFUSAL_TRANSITION_INVARIANT_VIOLATION,
    dematerialize_structure_roi,
    materialize_structure_roi,
    normalize_distribution_aggregate_row,
    normalize_materialization_state_row,
    normalize_micro_part_instance_row,
    normalize_reenactment_descriptor_row,
)

__all__ = [
    "MaterializationError",
    "REFUSAL_MATERIALIZATION_BUDGET_EXCEEDED",
    "REFUSAL_TRANSITION_INVARIANT_VIOLATION",
    "dematerialize_structure_roi",
    "materialize_structure_roi",
    "normalize_distribution_aggregate_row",
    "normalize_materialization_state_row",
    "normalize_micro_part_instance_row",
    "normalize_reenactment_descriptor_row",
]
