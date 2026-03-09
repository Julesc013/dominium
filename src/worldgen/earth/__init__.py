"""Deterministic EARTH-series worldgen helpers."""

from .earth_surface_generator import EARTH_SURFACE_GENERATOR_VERSION, generate_earth_surface_tile_plan
from .hydrology_engine import (
    DEFAULT_HYDROLOGY_PARAMS_ID,
    HYDROLOGY_ENGINE_VERSION,
    HYDROLOGY_PARAMS_REGISTRY_REL,
    apply_hydrology_to_surface_tile_artifact,
    build_fluid_channel_guidance,
    build_poll_transport_stub,
    compute_hydrology_window,
    hydrology_params_rows,
    hydrology_window_hash,
)
from .season_phase_engine import (
    EARTH_ORBIT_PHASE_SCALE,
    EARTH_SEASON_PHASE_ENGINE_VERSION,
    axial_tilt_mdeg,
    earth_orbit_phase,
    earth_orbit_phase_from_params,
    seasonal_wave_permille,
    solar_declination_mdeg,
)

__all__ = [
    "DEFAULT_HYDROLOGY_PARAMS_ID",
    "EARTH_SURFACE_GENERATOR_VERSION",
    "EARTH_ORBIT_PHASE_SCALE",
    "EARTH_SEASON_PHASE_ENGINE_VERSION",
    "HYDROLOGY_ENGINE_VERSION",
    "HYDROLOGY_PARAMS_REGISTRY_REL",
    "axial_tilt_mdeg",
    "apply_hydrology_to_surface_tile_artifact",
    "build_fluid_channel_guidance",
    "build_poll_transport_stub",
    "compute_hydrology_window",
    "earth_orbit_phase",
    "earth_orbit_phase_from_params",
    "generate_earth_surface_tile_plan",
    "hydrology_params_rows",
    "hydrology_window_hash",
    "seasonal_wave_permille",
    "solar_declination_mdeg",
]
