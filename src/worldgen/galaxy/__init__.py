"""GAL-0 galaxy metadata proxy exports."""

from .galaxy_proxy_field_engine import (
    GALACTIC_REGION_REGISTRY_REL,
    GALAXY_PROXY_ENGINE_VERSION,
    GALAXY_PROXY_SPATIAL_SCOPE_ID,
    build_galaxy_proxy_field_updates,
    build_galaxy_proxy_update_plan,
    classify_galactic_region,
    evaluate_galaxy_cell_proxy,
    galactic_region_id_from_value,
    galactic_region_registry_hash,
    galactic_region_rows,
    galactic_region_value_from_id,
    galaxy_proxy_window_hash,
    radiation_background_proxy_permille,
)


__all__ = [
    "GALACTIC_REGION_REGISTRY_REL",
    "GALAXY_PROXY_ENGINE_VERSION",
    "GALAXY_PROXY_SPATIAL_SCOPE_ID",
    "build_galaxy_proxy_field_updates",
    "build_galaxy_proxy_update_plan",
    "classify_galactic_region",
    "evaluate_galaxy_cell_proxy",
    "galactic_region_id_from_value",
    "galactic_region_registry_hash",
    "galactic_region_rows",
    "galactic_region_value_from_id",
    "galaxy_proxy_window_hash",
    "radiation_background_proxy_permille",
]
