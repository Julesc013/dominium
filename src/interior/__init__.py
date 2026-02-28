"""Interior subsystem exports."""

from .interior_engine import (
    InteriorError,
    REFUSAL_INTERIOR_INVALID,
    REFUSAL_INTERIOR_PATH_NOT_FOUND,
    REFUSAL_INTERIOR_STATE_TRANSITION,
    apply_portal_transition,
    build_connectivity_cache_key,
    interior_graph_rows_by_id,
    normalize_interior_graph,
    normalize_interior_volume,
    normalize_portal,
    path_exists,
    portal_allows_connectivity,
    portal_rows_by_id,
    reachable_volumes,
    resolve_volume_world_transform,
    volume_rows_by_id,
)

__all__ = [
    "InteriorError",
    "REFUSAL_INTERIOR_INVALID",
    "REFUSAL_INTERIOR_PATH_NOT_FOUND",
    "REFUSAL_INTERIOR_STATE_TRANSITION",
    "apply_portal_transition",
    "build_connectivity_cache_key",
    "interior_graph_rows_by_id",
    "normalize_interior_graph",
    "normalize_interior_volume",
    "normalize_portal",
    "path_exists",
    "portal_allows_connectivity",
    "portal_rows_by_id",
    "reachable_volumes",
    "resolve_volume_world_transform",
    "volume_rows_by_id",
]
