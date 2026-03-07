"""Deterministic unified profile override helpers."""

from .profile_engine import (
    REFUSAL_PROFILE_INVALID,
    REFUSAL_PROFILE_MISSING,
    REFUSAL_PROFILE_OVERRIDE_NOT_ALLOWED,
    apply_override,
    build_profile_binding_row,
    build_profile_exception_event_row,
    build_profile_row,
    normalize_profile_binding_rows,
    normalize_profile_rows,
    profile_rows_by_id,
    profile_rows_by_id_from_registry,
    resolve_effective_profile_snapshot,
    resolve_profile,
)

__all__ = [
    "REFUSAL_PROFILE_INVALID",
    "REFUSAL_PROFILE_MISSING",
    "REFUSAL_PROFILE_OVERRIDE_NOT_ALLOWED",
    "build_profile_row",
    "normalize_profile_rows",
    "profile_rows_by_id",
    "profile_rows_by_id_from_registry",
    "build_profile_binding_row",
    "normalize_profile_binding_rows",
    "build_profile_exception_event_row",
    "resolve_profile",
    "apply_override",
    "resolve_effective_profile_snapshot",
]

