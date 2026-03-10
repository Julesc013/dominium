"""Shared deterministic MW-4 refinement-pipeline fixtures."""

from __future__ import annotations

import copy
import sys
from functools import lru_cache

from tools.xstack.compatx.canonical_json import canonical_sha256


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


@lru_cache(maxsize=4)
def _stress_report_cached(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.worldgen.mw4_probe import run_refinement_stress

    return dict(run_refinement_stress(repo_root))


def refinement_stress_report(repo_root: str) -> dict:
    return copy.deepcopy(_stress_report_cached(repo_root))


def refinement_report_hash(report: dict) -> str:
    return canonical_sha256(
        {
            "worldgen_result_hash_chain": str(report.get("worldgen_result_hash_chain", "")).strip(),
            "refinement_request_hash_chain": str(report.get("refinement_request_hash_chain", "")).strip(),
            "refinement_cache_hash_chain": str(report.get("refinement_cache_hash_chain", "")).strip(),
            "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")).strip(),
        }
    )
