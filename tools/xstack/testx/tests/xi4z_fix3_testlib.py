"""FAST XI-4z-fix3 TestX helpers."""

from __future__ import annotations

import json
import os

from tools.review.xi4z_fix3_common import (
    SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL,
    SRC_DOMAIN_MAPPING_TARGET_PATHS_V4_REL,
    XI4Z_FIX3_REPORT_JSON_REL,
    XI5_READINESS_CONTRACT_V4_REL,
    artifact_hashes,
    build_xi4z_fix3_snapshot,
)


_CACHE: dict[str, dict[str, object]] = {}


def _load_json(repo_root: str, rel_path: str) -> dict:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def committed_lock_v4(repo_root: str) -> dict:
    return _load_json(repo_root, SRC_DOMAIN_MAPPING_LOCK_APPROVED_V4_REL)


def committed_readiness_contract_v4(repo_root: str) -> dict:
    return _load_json(repo_root, XI5_READINESS_CONTRACT_V4_REL)


def committed_target_paths_v4(repo_root: str) -> dict:
    return _load_json(repo_root, SRC_DOMAIN_MAPPING_TARGET_PATHS_V4_REL)


def committed_fix3_report(repo_root: str) -> dict:
    return _load_json(repo_root, XI4Z_FIX3_REPORT_JSON_REL)


def fresh_snapshot(repo_root: str) -> dict[str, object]:
    key = os.path.abspath(repo_root)
    cached = _CACHE.get(key)
    if cached is None:
        cached = build_xi4z_fix3_snapshot(key)
        _CACHE[key] = cached
    return cached


def fresh_hashes(repo_root: str) -> dict[str, str]:
    return artifact_hashes(fresh_snapshot(repo_root))
