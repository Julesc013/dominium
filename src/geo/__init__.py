"""Deterministic GEO kernel helpers."""

from .frame import (
    REFUSAL_GEO_FRAME_INVALID,
    REFUSAL_GEO_POSITION_INVALID,
    build_position_ref,
    field_sampling_cell_key,
    field_sampling_position,
    frame_get_transform,
    frame_graph_hash,
    position_distance,
    position_ref_hash,
    position_to_frame,
    roi_distance_mm,
)
from .index import (
    REFUSAL_GEO_CELL_KEY_INVALID,
    REFUSAL_GEO_OBJECT_KIND_MISSING,
    geo_cell_key_from_position,
    geo_cell_key_neighbors,
    geo_object_id,
    geo_refine_cell_key,
)
from .kernel import (
    REFUSAL_GEO_INVALID,
    REFUSAL_GEO_PROFILE_MISSING,
    geo_partition_cell_key,
    geo_project,
    geo_transform,
)
from .metric import REFUSAL_GEO_METRIC_INVALID, geo_distance, geo_geodesic, geo_neighbors
from .profile_binding import REFUSAL_GEO_DIMENSION_CHANGE, resolve_geo_profile_set
from .render import (
    REFUSAL_GEO_RENDER_REBASE_INVALID,
    REFUSAL_GEO_RENDER_TRUTH_MUTATION,
    apply_floating_origin,
    choose_floating_origin_offset,
)

__all__ = [
    "REFUSAL_GEO_CELL_KEY_INVALID",
    "REFUSAL_GEO_FRAME_INVALID",
    "REFUSAL_GEO_INVALID",
    "REFUSAL_GEO_METRIC_INVALID",
    "REFUSAL_GEO_OBJECT_KIND_MISSING",
    "REFUSAL_GEO_POSITION_INVALID",
    "REFUSAL_GEO_PROFILE_MISSING",
    "REFUSAL_GEO_DIMENSION_CHANGE",
    "REFUSAL_GEO_RENDER_REBASE_INVALID",
    "REFUSAL_GEO_RENDER_TRUTH_MUTATION",
    "build_position_ref",
    "field_sampling_cell_key",
    "field_sampling_position",
    "frame_get_transform",
    "frame_graph_hash",
    "apply_floating_origin",
    "choose_floating_origin_offset",
    "geo_cell_key_from_position",
    "geo_cell_key_neighbors",
    "geo_neighbors",
    "geo_distance",
    "geo_geodesic",
    "geo_object_id",
    "geo_transform",
    "geo_project",
    "geo_partition_cell_key",
    "geo_refine_cell_key",
    "position_distance",
    "position_ref_hash",
    "position_to_frame",
    "roi_distance_mm",
    "resolve_geo_profile_set",
]
