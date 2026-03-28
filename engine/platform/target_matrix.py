"""Deterministic ARCH-MATRIX target registry helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping

from ._canonical import canonical_sha256
from .platform_probe import canonical_platform_id


TARGET_MATRIX_REGISTRY_REL = os.path.join("data", "registries", "target_matrix_registry.json")


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_unique_strings(values: object) -> list[str]:
    return sorted({str(value).strip() for value in _as_list(values) if str(value).strip()})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


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
        with open(os.path.normpath(os.path.abspath(_token(path))), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _norm_repo_root(repo_root: str) -> str:
    return os.path.normpath(os.path.abspath(_token(repo_root) or "."))


def canonicalize_target_matrix_row(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "target_id": _token(item.get("target_id")),
        "os_id": _token(item.get("os_id")),
        "abi_id": _token(item.get("abi_id")),
        "arch_id": _token(item.get("arch_id")),
        "tier": max(1, min(3, _as_int(item.get("tier"), 3))),
        "supported_products": _sorted_unique_strings(item.get("supported_products")),
        "default_install_profiles": _sorted_unique_strings(item.get("default_install_profiles")),
        "capability_overrides": dict(_normalize_tree(_as_map(item.get("capability_overrides")))),
        "stability": dict(_normalize_tree(_as_map(item.get("stability")))),
        "extensions": dict(_normalize_tree(_as_map(item.get("extensions")))),
        "deterministic_fingerprint": _token(item.get("deterministic_fingerprint")),
    }
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def canonicalize_target_matrix_registry(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    record = _as_map(item.get("record"))
    targets = sorted(
        (
            canonicalize_target_matrix_row(row)
            for row in _as_list(record.get("targets"))
            if _token(_as_map(row).get("target_id"))
        ),
        key=lambda row: _token(row.get("target_id")),
    )
    normalized_record = {
        "registry_id": _token(record.get("registry_id")) or "dominium.registry.target_matrix_registry",
        "registry_version": _token(record.get("registry_version")) or "1.0.0",
        "targets": targets,
        "extensions": dict(_normalize_tree(_as_map(record.get("extensions")))),
        "deterministic_fingerprint": _token(record.get("deterministic_fingerprint")),
    }
    normalized_record["deterministic_fingerprint"] = canonical_sha256(
        dict(normalized_record, deterministic_fingerprint="")
    )
    return {
        "schema_id": _token(item.get("schema_id")) or "dominium.registry.target_matrix_registry",
        "schema_version": _token(item.get("schema_version")) or "1.0.0",
        "record": normalized_record,
    }


def load_target_matrix_registry(repo_root: str) -> dict:
    root = _norm_repo_root(repo_root)
    return canonicalize_target_matrix_registry(_read_json(os.path.join(root, TARGET_MATRIX_REGISTRY_REL)))


def target_matrix_rows_by_id(repo_root: str) -> dict[str, dict]:
    payload = load_target_matrix_registry(repo_root)
    out: dict[str, dict] = {}
    for row in _as_list(_as_map(payload.get("record")).get("targets")):
        row_map = _as_map(row)
        target_id = _token(row_map.get("target_id"))
        if target_id:
            out[target_id] = row_map
    return dict((key, out[key]) for key in sorted(out.keys()))


def target_matrix_registry_hash(repo_root: str) -> str:
    payload = load_target_matrix_registry(repo_root)
    return canonical_sha256(payload) if payload else ""


def _row_matches(
    row: Mapping[str, object],
    *,
    target_id: str,
    platform_id: str,
    platform_tag: str,
    os_id: str,
    arch_id: str,
    abi_id: str,
) -> bool:
    row_map = _as_map(row)
    extensions = _as_map(row_map.get("extensions"))
    if target_id and _token(row_map.get("target_id")) != target_id:
        return False
    if platform_id and canonical_platform_id(_token(extensions.get("platform_id"))) != canonical_platform_id(platform_id):
        return False
    if platform_tag and platform_tag not in _sorted_unique_strings(extensions.get("platform_tags")):
        return False
    if os_id and _token(row_map.get("os_id")) != os_id:
        return False
    if arch_id and _token(row_map.get("arch_id")) != arch_id:
        return False
    if abi_id and _token(row_map.get("abi_id")) != abi_id:
        return False
    return True


def _row_priority(row: Mapping[str, object]) -> tuple[int, int, int, str]:
    item = _as_map(row)
    extensions = _as_map(item.get("extensions"))
    built_priority = 0 if bool(extensions.get("built_in_mock_release", False)) else 1
    explicit_priority = 0 if bool(extensions.get("release_index_default", False)) else 1
    return (
        built_priority,
        int(item.get("tier", 3) or 3),
        explicit_priority,
        _token(item.get("target_id")),
    )


def select_target_matrix_row(
    repo_root: str,
    *,
    target_id: str = "",
    platform_id: str = "",
    platform_tag: str = "",
    os_id: str = "",
    arch_id: str = "",
    abi_id: str = "",
) -> dict:
    target_token = _token(target_id)
    platform_token = canonical_platform_id(platform_id) if _token(platform_id) else ""
    platform_tag_token = _token(platform_tag).lower()
    os_token = _token(os_id)
    arch_token = _token(arch_id)
    abi_token = _token(abi_id)
    rows = list(target_matrix_rows_by_id(repo_root).values())
    matches = [
        row
        for row in rows
        if _row_matches(
            row,
            target_id=target_token,
            platform_id=platform_token,
            platform_tag=platform_tag_token,
            os_id=os_token,
            arch_id=arch_token,
            abi_id=abi_token,
        )
    ]
    if not matches:
        return {}
    return dict(sorted(matches, key=_row_priority)[0])


def release_index_target_rows(repo_root: str) -> list[dict]:
    rows = []
    for row in target_matrix_rows_by_id(repo_root).values():
        item = _as_map(row)
        extensions = _as_map(item.get("extensions"))
        if int(item.get("tier", 3) or 3) > 2:
            continue
        if not bool(extensions.get("built_in_mock_release", False)):
            continue
        rows.append(item)
    return sorted(rows, key=_row_priority)


__all__ = [
    "TARGET_MATRIX_REGISTRY_REL",
    "canonicalize_target_matrix_registry",
    "canonicalize_target_matrix_row",
    "load_target_matrix_registry",
    "release_index_target_rows",
    "select_target_matrix_row",
    "target_matrix_registry_hash",
    "target_matrix_rows_by_id",
]
