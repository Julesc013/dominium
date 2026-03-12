"""Shared deterministic SOL-2 orbit-visualization fixtures for TestX."""

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
    from tools.astro.sol2_runtime_common import orbit_replay_report

    return orbit_replay_report(normalized)


def orbit_replay_report_payload(repo_root: str) -> dict:
    return dict(_replay(_ensure_repo_root(repo_root)))


def orbit_view_hash(repo_root: str) -> str:
    return str(orbit_replay_report_payload(repo_root).get("combined_hash", "")).strip()
