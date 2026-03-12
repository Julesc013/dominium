"""Deterministic SOL-series astro helpers with lazy exports."""

from __future__ import annotations

import importlib


_EXPORT_MODULES = {
    "DEFAULT_OCCLUSION_POLICY_ID": ".illumination",
    "EMITTER_KIND_REGISTRY_REL": ".illumination",
    "ILLUMINATION_GEOMETRY_ENGINE_VERSION": ".illumination",
    "OCCLUSION_POLICY_REGISTRY_REL": ".illumination",
    "RECEIVER_KIND_REGISTRY_REL": ".illumination",
    "build_direction_position_ref": ".illumination",
    "build_emitter_descriptor": ".illumination",
    "build_illumination_view_artifact": ".illumination",
    "build_receiver_descriptor": ".illumination",
    "build_view_artifact_from_directions": ".illumination",
    "emitter_kind_registry_hash": ".illumination",
    "emitter_kind_rows": ".illumination",
    "occlusion_policy_registry_hash": ".illumination",
    "occlusion_policy_rows": ".illumination",
    "receiver_kind_registry_hash": ".illumination",
    "receiver_kind_rows": ".illumination",
}


def __getattr__(name: str):
    module_rel = _EXPORT_MODULES.get(name)
    if not module_rel:
        raise AttributeError(name)
    module = importlib.import_module(module_rel, __name__)
    return getattr(module, name)


__all__ = sorted(_EXPORT_MODULES.keys())
