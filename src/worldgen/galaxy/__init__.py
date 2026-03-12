"""Galaxy worldgen helpers with lazy exports to avoid package import cycles."""

from __future__ import annotations

import importlib


_EXPORT_MODULES = {
    "GALACTIC_REGION_REGISTRY_REL": ".galaxy_proxy_field_engine",
    "GALAXY_PROXY_ENGINE_VERSION": ".galaxy_proxy_field_engine",
    "GALAXY_PROXY_SPATIAL_SCOPE_ID": ".galaxy_proxy_field_engine",
    "build_galaxy_proxy_field_updates": ".galaxy_proxy_field_engine",
    "build_galaxy_proxy_update_plan": ".galaxy_proxy_field_engine",
    "classify_galactic_region": ".galaxy_proxy_field_engine",
    "evaluate_galaxy_cell_proxy": ".galaxy_proxy_field_engine",
    "galactic_region_id_from_value": ".galaxy_proxy_field_engine",
    "galactic_region_registry_hash": ".galaxy_proxy_field_engine",
    "galactic_region_rows": ".galaxy_proxy_field_engine",
    "galactic_region_value_from_id": ".galaxy_proxy_field_engine",
    "galaxy_proxy_window_hash": ".galaxy_proxy_field_engine",
    "radiation_background_proxy_permille": ".galaxy_proxy_field_engine",
    "BLACK_HOLE_LOCAL_SUBKEY": ".galaxy_object_stub_generator",
    "GALAXY_OBJECT_STUB_GENERATOR_VERSION": ".galaxy_object_stub_generator",
    "MAX_GALAXY_OBJECT_STUBS_PER_CELL": ".galaxy_object_stub_generator",
    "RNG_WORLDGEN_GALAXY_OBJECTS": ".galaxy_object_stub_generator",
    "build_galaxy_object_hazard_hooks": ".galaxy_object_stub_generator",
    "build_galaxy_object_layer_source_payloads": ".galaxy_object_stub_generator",
    "build_galaxy_object_stub_row": ".galaxy_object_stub_generator",
    "galaxy_object_stub_hash_chain": ".galaxy_object_stub_generator",
    "generate_galaxy_object_stub_payload": ".galaxy_object_stub_generator",
    "normalize_galaxy_object_stub_rows": ".galaxy_object_stub_generator",
}


def __getattr__(name: str):
    module_rel = _EXPORT_MODULES.get(name)
    if not module_rel:
        raise AttributeError(name)
    module = importlib.import_module(module_rel, __name__)
    return getattr(module, name)


__all__ = sorted(_EXPORT_MODULES.keys())
