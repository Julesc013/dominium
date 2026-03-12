"""Shared deterministic GAL-1 galaxy-object fixtures for TestX."""

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
    from tools.worldgen.gal1_probe import verify_galaxy_object_replay

    return verify_galaxy_object_replay(normalized)


@lru_cache(maxsize=4)
def _central_black_hole(repo_root: str) -> dict:
    normalized = _ensure_repo_root(repo_root)
    from tools.worldgen.gal1_probe import central_black_hole_report

    return central_black_hole_report(normalized)


@lru_cache(maxsize=4)
def _bounded_generation(repo_root: str) -> dict:
    normalized = _ensure_repo_root(repo_root)
    from tools.worldgen.gal1_probe import bounded_generation_report

    return bounded_generation_report(normalized)


def galaxy_object_replay_report(repo_root: str) -> dict:
    return dict(_replay(_ensure_repo_root(repo_root)))


def central_black_hole_once_report(repo_root: str) -> dict:
    return dict(_central_black_hole(_ensure_repo_root(repo_root)))


def bounded_galaxy_object_generation_report(repo_root: str) -> dict:
    return dict(_bounded_generation(_ensure_repo_root(repo_root)))


def galaxy_object_replay_hash(repo_root: str) -> str:
    normalized = _ensure_repo_root(repo_root)
    from tools.worldgen.gal1_probe import galaxy_object_hash

    return str(galaxy_object_hash(normalized)).strip()
