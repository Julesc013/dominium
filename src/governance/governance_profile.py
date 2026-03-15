"""Deterministic governance profile helpers."""

from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Mapping

from src.meta_extensions_engine import normalize_extensions_tree


DEFAULT_GOVERNANCE_PROFILE_REL = os.path.join("data", "governance", "governance_profile.json")
DEFAULT_GOVERNANCE_MODE_REGISTRY_REL = os.path.join("data", "registries", "governance_mode_registry.json")

GOVERNANCE_MODE_OPEN = "gov.open"
GOVERNANCE_MODE_CORE_CLOSED = "gov.core_closed_ecosystem_open"
GOVERNANCE_MODE_MIXED = "gov.mixed"

FORK_POLICY_ID = "fork.explicit_prefix_required"
REDISTRIBUTION_POLICY_ID = "redistribution.by_artifact_kind"
ARCHIVE_POLICY_ID = "archive.primary_secondary_cold"

_OFFICIAL_RELEASE_RE = re.compile(r"^v(\d+\.\d+\.\d+)-(mock|alpha|beta|rc|stable)$")
_FORK_RELEASE_RE = re.compile(r"^fork\.([a-z0-9][a-z0-9_.-]*)\.v(\d+\.\d+\.\d+)-(mock|alpha|beta|rc|stable)$")


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: object) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_unique_tokens(values: object) -> list[str]:
    return sorted({_token(value) for value in _as_list(values) if _token(value)})


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(dict(value).items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in list(value)]
    if isinstance(value, tuple):
        return [_normalize_tree(item) for item in list(value)]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


def deterministic_fingerprint(payload: Mapping[str, object] | None) -> str:
    body = dict(_normalize_tree(dict(payload or {})))
    body["deterministic_fingerprint"] = ""
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def canonicalize_governance_mode_row(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "governance_mode_id": _token(item.get("governance_mode_id")),
        "open_source_surface_ids": _sorted_unique_tokens(item.get("open_source_surface_ids")),
        "closed_source_surface_ids": _sorted_unique_tokens(item.get("closed_source_surface_ids")),
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(normalize_extensions_tree(_as_map(item.get("extensions"))))),
        "stability": dict(_normalize_tree(_as_map(item.get("stability")))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def canonicalize_governance_profile(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "governance_version": _token(item.get("governance_version")) or "1.0.0",
        "governance_mode_id": _token(item.get("governance_mode_id")),
        "official_signer_ids": _sorted_unique_tokens(item.get("official_signer_ids")),
        "redistribution_policy_id": _token(item.get("redistribution_policy_id")) or REDISTRIBUTION_POLICY_ID,
        "fork_policy_id": _token(item.get("fork_policy_id")) or FORK_POLICY_ID,
        "archive_policy_id": _token(item.get("archive_policy_id")) or ARCHIVE_POLICY_ID,
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(normalize_extensions_tree(_as_map(item.get("extensions"))))),
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def governance_profile_hash(payload: Mapping[str, object] | None) -> str:
    return hashlib.sha256(
        json.dumps(
            canonicalize_governance_profile(payload),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def _read_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def load_governance_mode_registry(repo_root: str) -> dict:
    return _read_json(os.path.join(_norm(repo_root), DEFAULT_GOVERNANCE_MODE_REGISTRY_REL))


def governance_profile_path(repo_root: str, *, install_root: str = "") -> str:
    install_root_token = _token(install_root)
    if install_root_token:
        install_candidate = os.path.join(_norm(install_root_token), DEFAULT_GOVERNANCE_PROFILE_REL)
        if os.path.isfile(install_candidate):
            return install_candidate
    return os.path.join(_norm(repo_root), DEFAULT_GOVERNANCE_PROFILE_REL)


def load_governance_profile(repo_root: str, *, install_root: str = "") -> dict:
    payload = _read_json(governance_profile_path(repo_root, install_root=install_root))
    if not payload:
        return {}
    return canonicalize_governance_profile(payload)


def select_governance_mode_row(registry_payload: Mapping[str, object] | None, governance_mode_id: str) -> dict:
    target = _token(governance_mode_id)
    record = _as_map(_as_map(registry_payload).get("record"))
    for row in _as_list(record.get("governance_modes")):
        item = canonicalize_governance_mode_row(row)
        if _token(item.get("governance_mode_id")) == target:
            return item
    return {}


def parse_release_tag(tag: str) -> dict:
    token = _token(tag)
    match = _OFFICIAL_RELEASE_RE.match(token)
    if match:
        semver, channel_id = match.groups()
        return {
            "result": "complete",
            "tag_kind": "official",
            "release_tag": token,
            "fork_namespace": "",
            "semver": semver,
            "channel_id": channel_id,
            "refusal_code": "",
        }
    match = _FORK_RELEASE_RE.match(token)
    if match:
        fork_namespace, semver, channel_id = match.groups()
        return {
            "result": "complete",
            "tag_kind": "fork",
            "release_tag": token,
            "fork_namespace": fork_namespace,
            "semver": semver,
            "channel_id": channel_id,
            "refusal_code": "",
        }
    return {
        "result": "refused",
        "tag_kind": "",
        "release_tag": token,
        "fork_namespace": "",
        "semver": "",
        "channel_id": "",
        "refusal_code": "refusal.governance.fork_prefix_required",
    }


__all__ = [
    "ARCHIVE_POLICY_ID",
    "DEFAULT_GOVERNANCE_MODE_REGISTRY_REL",
    "DEFAULT_GOVERNANCE_PROFILE_REL",
    "FORK_POLICY_ID",
    "GOVERNANCE_MODE_CORE_CLOSED",
    "GOVERNANCE_MODE_MIXED",
    "GOVERNANCE_MODE_OPEN",
    "REDISTRIBUTION_POLICY_ID",
    "canonicalize_governance_mode_row",
    "canonicalize_governance_profile",
    "deterministic_fingerprint",
    "governance_profile_hash",
    "governance_profile_path",
    "load_governance_mode_registry",
    "load_governance_profile",
    "parse_release_tag",
    "select_governance_mode_row",
]
