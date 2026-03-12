"""Deterministic SOL-1 illumination geometry helpers."""

from .illumination_geometry_engine import (
    DEFAULT_OCCLUSION_POLICY_ID,
    EMITTER_KIND_REGISTRY_REL,
    ILLUMINATION_GEOMETRY_ENGINE_VERSION,
    OCCLUSION_POLICY_REGISTRY_REL,
    RECEIVER_KIND_REGISTRY_REL,
    build_direction_position_ref,
    build_emitter_descriptor,
    build_illumination_view_artifact,
    build_receiver_descriptor,
    build_view_artifact_from_directions,
    emitter_kind_registry_hash,
    emitter_kind_rows,
    occlusion_policy_registry_hash,
    occlusion_policy_rows,
    receiver_kind_registry_hash,
    receiver_kind_rows,
)

__all__ = [
    "DEFAULT_OCCLUSION_POLICY_ID",
    "EMITTER_KIND_REGISTRY_REL",
    "ILLUMINATION_GEOMETRY_ENGINE_VERSION",
    "OCCLUSION_POLICY_REGISTRY_REL",
    "RECEIVER_KIND_REGISTRY_REL",
    "build_direction_position_ref",
    "build_emitter_descriptor",
    "build_illumination_view_artifact",
    "build_receiver_descriptor",
    "build_view_artifact_from_directions",
    "emitter_kind_registry_hash",
    "emitter_kind_rows",
    "occlusion_policy_registry_hash",
    "occlusion_policy_rows",
    "receiver_kind_registry_hash",
    "receiver_kind_rows",
]
