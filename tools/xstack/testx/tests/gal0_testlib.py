"""Shared deterministic GAL-0 galaxy-proxy fixtures for TestX."""

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
    from tools.worldgen.gal0_probe import verify_galaxy_proxy_window_replay

    return verify_galaxy_proxy_window_replay(normalized)


@lru_cache(maxsize=4)
def _regions(repo_root: str) -> dict:
    normalized = _ensure_repo_root(repo_root)
    from tools.worldgen.gal0_probe import region_threshold_report

    return region_threshold_report(normalized)


def galaxy_proxy_replay_report(repo_root: str) -> dict:
    return dict(_replay(_ensure_repo_root(repo_root)))


def galaxy_region_threshold_report(repo_root: str) -> dict:
    return dict(_regions(_ensure_repo_root(repo_root)))


def galaxy_proxy_hash(repo_root: str) -> str:
    return str(galaxy_proxy_replay_report(repo_root).get("combined_hash", "")).strip()
