"""SYS domain exports."""

from src.system.system_collapse_engine import (
    REFUSAL_SYSTEM_COLLAPSE_INELIGIBLE,
    REFUSAL_SYSTEM_COLLAPSE_INVALID,
    SystemCollapseError,
    boundary_invariant_rows_by_id,
    build_boundary_invariant_row,
    build_interface_signature_row,
    build_system_macro_capsule_row,
    build_system_state_vector_row,
    collapse_system_graph,
    interface_signature_rows_by_system,
    normalize_boundary_invariant_rows,
    normalize_interface_signature_rows,
    normalize_system_macro_capsule_rows,
    normalize_system_rows,
    normalize_system_state_vector_rows,
    system_rows_by_id,
)

__all__ = [
    "REFUSAL_SYSTEM_COLLAPSE_INELIGIBLE",
    "REFUSAL_SYSTEM_COLLAPSE_INVALID",
    "SystemCollapseError",
    "build_interface_signature_row",
    "normalize_interface_signature_rows",
    "interface_signature_rows_by_system",
    "build_boundary_invariant_row",
    "normalize_boundary_invariant_rows",
    "boundary_invariant_rows_by_id",
    "build_system_state_vector_row",
    "normalize_system_state_vector_rows",
    "build_system_macro_capsule_row",
    "normalize_system_macro_capsule_rows",
    "normalize_system_rows",
    "system_rows_by_id",
    "collapse_system_graph",
]
