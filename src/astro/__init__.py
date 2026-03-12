"""Deterministic SOL-series astro helpers with lazy exports."""

from __future__ import annotations

import importlib


_EXPORT_MODULES = {
    "DEFAULT_EPHEMERIS_PROVIDER_ID": ".ephemeris",
    "DEFAULT_ORBIT_PATH_POLICY_ID": ".ephemeris",
    "DEFAULT_OCCLUSION_POLICY_ID": ".illumination",
    "EMITTER_KIND_REGISTRY_REL": ".illumination",
    "EPHEMERIS_PROVIDER_REGISTRY_REL": ".ephemeris",
    "ILLUMINATION_GEOMETRY_ENGINE_VERSION": ".illumination",
    "KEPLER_PROXY_ENGINE_VERSION": ".ephemeris",
    "OCCLUSION_POLICY_REGISTRY_REL": ".illumination",
    "ORBIT_PATH_POLICY_REGISTRY_REL": ".ephemeris",
    "ORBIT_VIEW_ENGINE_VERSION": ".views",
    "RECEIVER_KIND_REGISTRY_REL": ".illumination",
    "build_orbit_body_descriptors": ".ephemeris",
    "build_orbit_layer_source_payloads": ".views",
    "build_orbit_position_ref": ".ephemeris",
    "build_orbit_view_surface": ".views",
    "build_direction_position_ref": ".illumination",
    "build_emitter_descriptor": ".illumination",
    "build_illumination_view_artifact": ".illumination",
    "build_receiver_descriptor": ".illumination",
    "build_view_artifact_from_directions": ".illumination",
    "cos_permille_from_angle_mdeg": ".illumination",
    "emitter_kind_registry_hash": ".illumination",
    "emitter_kind_rows": ".illumination",
    "ephemeris_provider_registry_hash": ".ephemeris",
    "ephemeris_provider_rows": ".ephemeris",
    "occlusion_policy_registry_hash": ".illumination",
    "occlusion_policy_rows": ".illumination",
    "orbit_path_policy_registry_hash": ".ephemeris",
    "orbit_path_policy_rows": ".ephemeris",
    "orbit_view_artifact_hash": ".views",
    "receiver_kind_registry_hash": ".illumination",
    "receiver_kind_rows": ".illumination",
    "resolve_ephemeris_provider": ".ephemeris",
    "sample_orbit_path_points": ".ephemeris",
    "sin_permille_from_angle_mdeg": ".illumination",
}


def __getattr__(name: str):
    module_rel = _EXPORT_MODULES.get(name)
    if not module_rel:
        raise AttributeError(name)
    module = importlib.import_module(module_rel, __name__)
    return getattr(module, name)


__all__ = sorted(_EXPORT_MODULES.keys())
