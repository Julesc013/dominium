"""Deterministic embodiment helpers for EMB-0."""

from .body import (
    DEFAULT_BODY_TEMPLATE_ID,
    body_state_rows_by_subject_id,
    body_template_registry_hash,
    body_template_rows_by_id,
    build_body_state,
    instantiate_body_system,
    normalize_body_state_rows,
)
from .collision import (
    DEFAULT_COLLISION_PROVIDER_ID,
    DEFAULT_MOVEMENT_SLOPE_PARAMS_ID,
    collision_provider_rows_by_id,
    invalidate_macro_heightfield_cache_for_tiles,
    movement_slope_params_rows_by_id,
    resolve_macro_heightfield_sample,
)
from .lens import (
    lens_profile_registry_hash,
    lens_profile_rows_by_id,
    resolve_authorized_lens_profile,
    resolve_lens_camera_state,
)

__all__ = [
    "DEFAULT_BODY_TEMPLATE_ID",
    "DEFAULT_COLLISION_PROVIDER_ID",
    "DEFAULT_MOVEMENT_SLOPE_PARAMS_ID",
    "body_state_rows_by_subject_id",
    "body_template_registry_hash",
    "body_template_rows_by_id",
    "build_body_state",
    "collision_provider_rows_by_id",
    "invalidate_macro_heightfield_cache_for_tiles",
    "instantiate_body_system",
    "movement_slope_params_rows_by_id",
    "normalize_body_state_rows",
    "lens_profile_registry_hash",
    "lens_profile_rows_by_id",
    "resolve_authorized_lens_profile",
    "resolve_lens_camera_state",
    "resolve_macro_heightfield_sample",
]
