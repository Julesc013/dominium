"""Deterministic archive-policy helpers for immutable release retention."""

from __future__ import annotations

import json
import os
from typing import Mapping, Sequence

from src.archive.deterministic_bundle import (
    DEFAULT_ARCHIVE_BUNDLE_PREFIX,
    build_deterministic_archive_bundle,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


DEFAULT_ARCHIVE_RECORD_REL = os.path.join("manifests", "archive_record.json")
DEFAULT_RELEASE_INDEX_HISTORY_ROOT_REL = os.path.join("manifests", "release_index_history")
DEFAULT_MIRROR_LIST = (
    "mirror.primary.default",
    "mirror.secondary.default",
    "mirror.cold_storage.default",
)


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


def _sorted_unique_strings(values: object) -> list[str]:
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


def _read_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def canonicalize_archive_record(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "release_id": _token(item.get("release_id")),
        "release_manifest_hash": _token(item.get("release_manifest_hash")).lower(),
        "release_index_hash": _token(item.get("release_index_hash")).lower(),
        "component_graph_hash": _token(item.get("component_graph_hash")).lower(),
        "governance_profile_hash": _token(item.get("governance_profile_hash")).lower(),
        "source_archive_hash": _token(item.get("source_archive_hash")).lower(),
        "mirror_list": _sorted_unique_strings(item.get("mirror_list")),
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
    }
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def archive_record_hash(payload: Mapping[str, object] | None) -> str:
    return canonical_sha256(canonicalize_archive_record(payload))


def load_archive_record(path: str) -> dict:
    return canonicalize_archive_record(_read_json(path))


def write_archive_record(path: str, payload: Mapping[str, object]) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(canonicalize_archive_record(payload)))
        handle.write("\n")
    return target


def release_index_history_rel(channel_id: str, release_id: str) -> str:
    channel_token = _token(channel_id) or "mock"
    release_token = _token(release_id) or "release.unknown"
    return _norm_rel(os.path.join(DEFAULT_RELEASE_INDEX_HISTORY_ROOT_REL, channel_token, "{}.json".format(release_token)))


__all__ = [
    "DEFAULT_ARCHIVE_BUNDLE_PREFIX",
    "DEFAULT_ARCHIVE_RECORD_REL",
    "DEFAULT_MIRROR_LIST",
    "DEFAULT_RELEASE_INDEX_HISTORY_ROOT_REL",
    "archive_record_hash",
    "build_deterministic_archive_bundle",
    "canonicalize_archive_record",
    "load_archive_record",
    "release_index_history_rel",
    "write_archive_record",
]
