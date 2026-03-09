"""Deterministic MW worldgen helpers with lazy exports to avoid package import cycles."""

from __future__ import annotations

import importlib


_EXPORT_MODULES = {
    "DEFAULT_GALAXY_PRIORS_ID": ".mw_cell_generator",
    "GALAXY_PRIORS_REGISTRY_REL": ".mw_cell_generator",
    "MW_GALACTIC_FRAME_ID": ".mw_cell_generator",
    "PARSEC_MM": ".mw_cell_generator",
    "galaxy_priors_registry_hash": ".mw_cell_generator",
    "galaxy_priors_rows": ".mw_cell_generator",
    "generate_mw_cell_payload": ".mw_cell_generator",
    "normalize_star_system_artifact_rows": ".mw_cell_generator",
    "normalize_star_system_seed_rows": ".mw_cell_generator",
    "star_system_artifact_hash_chain": ".mw_cell_generator",
    "DEFAULT_QUERY_MAX_CELLS": ".system_query_engine",
    "build_procedural_astronomy_index": ".system_query_engine",
    "build_system_teleport_plan": ".system_query_engine",
    "filter_habitable_candidates": ".system_query_engine",
    "list_systems_in_cell": ".system_query_engine",
    "query_nearest_system": ".system_query_engine",
    "DEFAULT_SYSTEM_PRIORS_ID": ".mw_system_refiner_l2",
    "DEFAULT_PLANET_PRIORS_ID": ".mw_system_refiner_l2",
    "generate_mw_system_l2_payload": ".mw_system_refiner_l2",
    "normalize_star_artifact_rows": ".mw_system_refiner_l2",
    "normalize_planet_orbit_artifact_rows": ".mw_system_refiner_l2",
    "normalize_planet_basic_artifact_rows": ".mw_system_refiner_l2",
    "normalize_system_l2_summary_rows": ".mw_system_refiner_l2",
    "star_artifact_hash_chain": ".mw_system_refiner_l2",
    "planet_orbit_artifact_hash_chain": ".mw_system_refiner_l2",
    "planet_basic_artifact_hash_chain": ".mw_system_refiner_l2",
    "system_l2_summary_hash_chain": ".mw_system_refiner_l2",
}


def __getattr__(name: str):
    module_rel = _EXPORT_MODULES.get(name)
    if not module_rel:
        raise AttributeError(name)
    module = importlib.import_module(module_rel, __name__)
    return getattr(module, name)


__all__ = sorted(_EXPORT_MODULES.keys())
