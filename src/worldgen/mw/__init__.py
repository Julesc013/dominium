"""Deterministic MW Milky Way generation helpers."""

from .mw_cell_generator import (
    DEFAULT_GALAXY_PRIORS_ID,
    GALAXY_PRIORS_REGISTRY_REL,
    galaxy_priors_registry_hash,
    galaxy_priors_rows,
    generate_mw_cell_payload,
    normalize_star_system_artifact_rows,
    normalize_star_system_seed_rows,
    star_system_artifact_hash_chain,
)


_QUERY_EXPORTS = {
    "DEFAULT_QUERY_MAX_CELLS",
    "build_procedural_astronomy_index",
    "build_system_teleport_plan",
    "filter_habitable_candidates",
    "list_systems_in_cell",
    "query_nearest_system",
}


def __getattr__(name: str):
    if name in _QUERY_EXPORTS:
        from . import system_query_engine as _system_query_engine

        return getattr(_system_query_engine, name)
    raise AttributeError(name)

__all__ = [
    "DEFAULT_GALAXY_PRIORS_ID",
    "DEFAULT_QUERY_MAX_CELLS",
    "GALAXY_PRIORS_REGISTRY_REL",
    "build_procedural_astronomy_index",
    "build_system_teleport_plan",
    "filter_habitable_candidates",
    "galaxy_priors_registry_hash",
    "galaxy_priors_rows",
    "generate_mw_cell_payload",
    "list_systems_in_cell",
    "normalize_star_system_artifact_rows",
    "normalize_star_system_seed_rows",
    "query_nearest_system",
    "star_system_artifact_hash_chain",
]
