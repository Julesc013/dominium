"""FAST XI-4b src-domain mapping TestX helpers."""

from __future__ import annotations

import json
import os

from tools.review.xi4b_src_domain_mapping_common import (
    SRC_DOMAIN_MAPPING_LOCK_PROPOSAL_REL,
    SRC_DOMAIN_MAPPING_REL,
    TMP_BUNDLE_MANIFEST_REL,
    XI4B_REVIEW_MANIFEST_REL,
    artifact_hashes,
    build_xi4b_snapshot,
)


_CACHE: dict[str, dict[str, object]] = {}


def _load_json(repo_root: str, rel_path: str) -> dict:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def _load_text(repo_root: str, rel_path: str) -> str:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def committed_src_domain_mapping(repo_root: str) -> dict:
    return _load_json(repo_root, SRC_DOMAIN_MAPPING_REL)


def committed_lock_proposal(repo_root: str) -> dict:
    return _load_json(repo_root, SRC_DOMAIN_MAPPING_LOCK_PROPOSAL_REL)


def committed_review_manifest(repo_root: str) -> dict:
    return _load_json(repo_root, XI4B_REVIEW_MANIFEST_REL)


def committed_bundle_manifest_text(repo_root: str) -> str:
    return _load_text(repo_root, TMP_BUNDLE_MANIFEST_REL)


def fresh_snapshot(repo_root: str) -> dict[str, object]:
    key = os.path.abspath(repo_root)
    cached = _CACHE.get(key)
    if cached is None:
        cached = build_xi4b_snapshot(key)
        _CACHE[key] = cached
    return cached


def fresh_hashes(repo_root: str) -> dict[str, str]:
    return artifact_hashes(fresh_snapshot(repo_root))


__all__ = [
    "committed_bundle_manifest_text",
    "committed_lock_proposal",
    "committed_review_manifest",
    "committed_src_domain_mapping",
    "fresh_hashes",
    "fresh_snapshot",
]
