"""Shared deterministic EARTH-10 material-proxy fixtures for TestX."""

from __future__ import annotations

import sys
from functools import lru_cache


def _ensure_repo_root(repo_root: str) -> str:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    return repo_root


@lru_cache(maxsize=4)
def _replay(repo_root: str) -> dict:
    normalized = _ensure_repo_root(repo_root)
    from tools.worldgen.earth10_probe import verify_material_proxy_window_replay

    return verify_material_proxy_window_replay(normalized)


@lru_cache(maxsize=4)
def _flags(repo_root: str) -> dict:
    normalized = _ensure_repo_root(repo_root)
    from tools.worldgen.earth10_probe import surface_flag_consistency_report

    return surface_flag_consistency_report(normalized)


@lru_cache(maxsize=4)
def _albedo(repo_root: str) -> dict:
    normalized = _ensure_repo_root(repo_root)
    from tools.worldgen.earth10_probe import albedo_proxy_range_report

    return albedo_proxy_range_report(normalized)


@lru_cache(maxsize=4)
def _hash(repo_root: str) -> str:
    normalized = _ensure_repo_root(repo_root)
    from tools.worldgen.earth10_probe import material_proxy_hash

    return str(material_proxy_hash(normalized)).strip()


def material_proxy_replay_report(repo_root: str) -> dict:
    return dict(_replay(_ensure_repo_root(repo_root)))


def material_proxy_flag_report(repo_root: str) -> dict:
    return dict(_flags(_ensure_repo_root(repo_root)))


def material_proxy_albedo_report(repo_root: str) -> dict:
    return dict(_albedo(_ensure_repo_root(repo_root)))


def earth_material_proxy_hash(repo_root: str) -> str:
    return str(_hash(_ensure_repo_root(repo_root))).strip()
