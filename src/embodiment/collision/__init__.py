"""Deterministic EARTH-6 terrain collision helpers."""

from .macro_heightfield_provider import (
    DEFAULT_COLLISION_PROVIDER_ID,
    DEFAULT_MOVEMENT_SLOPE_PARAMS_ID,
    collision_provider_rows_by_id,
    invalidate_macro_heightfield_cache_for_tiles,
    movement_slope_params_rows_by_id,
    resolve_macro_heightfield_sample,
)

__all__ = [
    "DEFAULT_COLLISION_PROVIDER_ID",
    "DEFAULT_MOVEMENT_SLOPE_PARAMS_ID",
    "collision_provider_rows_by_id",
    "invalidate_macro_heightfield_cache_for_tiles",
    "movement_slope_params_rows_by_id",
    "resolve_macro_heightfield_sample",
]
