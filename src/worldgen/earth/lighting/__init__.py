"""Deterministic EARTH-5 lighting helpers."""

from .illumination_engine import (
    DEFAULT_ILLUMINATION_MODEL_ID,
    EARTH_ILLUMINATION_ENGINE_VERSION,
    ILLUMINATION_MODEL_REGISTRY_REL,
    build_illumination_view_artifact,
    illumination_model_registry_hash,
    illumination_model_rows,
)
from .horizon_shadow_engine import (
    DEFAULT_SHADOW_MODEL_ID,
    EARTH_HORIZON_SHADOW_ENGINE_VERSION,
    SHADOW_MODEL_REGISTRY_REL,
    evaluate_horizon_shadow,
    shadow_model_registry_hash,
    shadow_model_rows,
)

__all__ = [
    "DEFAULT_ILLUMINATION_MODEL_ID",
    "DEFAULT_SHADOW_MODEL_ID",
    "EARTH_ILLUMINATION_ENGINE_VERSION",
    "EARTH_HORIZON_SHADOW_ENGINE_VERSION",
    "ILLUMINATION_MODEL_REGISTRY_REL",
    "SHADOW_MODEL_REGISTRY_REL",
    "build_illumination_view_artifact",
    "evaluate_horizon_shadow",
    "illumination_model_registry_hash",
    "illumination_model_rows",
    "shadow_model_registry_hash",
    "shadow_model_rows",
]
