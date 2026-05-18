"""Deterministic LIB-6 bundle manifest helpers."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from typing import Dict, Iterable, List, Mapping, Sequence

from meta_extensions_engine import normalize_extensions_map, normalize_extensions_tree


BUNDLE_MANIFEST_NAME = "bundle.manifest.json"
BUNDLE_CONTENT_DIR = "content"
BUNDLE_HASHES_DIR = "hashes"
BUNDLE_HASH_INDEX_NAME = "content.sha256.json"
BUNDLE_HASH_INDEX_REL = "{}/{}".format(BUNDLE_HASHES_DIR, BUNDLE_HASH_INDEX_NAME)
HASH_ALGORITHM = "sha256"
ZERO_SHA256 = "0" * 64


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _norm_rel(path: object) -> str:
    text = str(path or "").replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    while text.startswith("/"):
        text = text[1:]
    return text


def _normalize_value(value: object, key: str = "") -> object:
    if isinstance(value, Mapping):
        return {
            str(name): _normalize_value(item, str(name))
            for name, item in sorted(dict(value).items(), key=lambda row: str(row[0]))
        }
    if isinstance(value, list):
        return [_normalize_value(item) for item in list(value)]
    if isinstance(value, str):
        if key.endswith("_path") or key.endswith("_ref") or key in {"relative_path"}:
            return _norm_rel(value)
        return value
    return value


def canonical_json_text(payload: object) -> str:
    return json.dumps(
        _normalize_value(normalize_extensions_tree(payload)),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def canonical_sha256(payload: object) -> str:
    return hashlib.sha256(canonical_json_text(payload).encode("utf-8")).hexdigest()


def deterministic_fingerprint(payload: Mapping[str, object]) -> str:
    body = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    if isinstance(body, dict):
        body["deterministic_fingerprint"] = ""
        for row in list(body.get("included_artifacts") or []):
            if isinstance(row, dict):
                row["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def ensure_dir(path: str) -> None:
    if path:
        os.makedirs(path, exist_ok=True)


def write_json(path: str, payload: Mapping[str, object]) -> str:
    target = os.path.abspath(str(path or "").strip())
    ensure_dir(os.path.dirname(target))
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(
            _normalize_value(normalize_extensions_tree(dict(payload or {}))),
            handle,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
        handle.write("\n")
    return target


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return _as_map(_normalize_value(normalize_extensions_tree(payload)))


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_rel_files(root_path: str) -> List[str]:
    entries: List[str] = []
    for current_root, dirnames, filenames in os.walk(root_path):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            abs_path = os.path.join(current_root, filename)
            entries.append(_norm_rel(os.path.relpath(abs_path, root_path)))
    return sorted(entries)


def normalize_bundle_item(payload: Mapping[str, object] | None) -> dict:
    row = _as_map(payload)
    item = {
        "item_kind": str(row.get("item_kind", "")).strip(),
        "item_id_or_hash": str(row.get("item_id_or_hash", "")).strip(),
        "relative_path": _norm_rel(row.get("relative_path", "")),
        "content_hash": str(row.get("content_hash", "")).strip().lower(),
        "deterministic_fingerprint": "",
        "extensions": normalize_extensions_map(_as_map(row.get("extensions"))),
    }
    item["deterministic_fingerprint"] = canonical_sha256(
        {
            "item_kind": item["item_kind"],
            "item_id_or_hash": item["item_id_or_hash"],
            "relative_path": item["relative_path"],
            "content_hash": item["content_hash"],
            "deterministic_fingerprint": "",
            "extensions": item["extensions"],
        }
    )
    return _as_map(_normalize_value(item))


def _bundle_projection(items: Sequence[Mapping[str, object]]) -> List[dict]:
    out: List[dict] = []
    for row in list(items or []):
        item = normalize_bundle_item(row)
        out.append(
            {
                "item_kind": str(item.get("item_kind", "")).strip(),
                "item_id_or_hash": str(item.get("item_id_or_hash", "")).strip(),
                "relative_path": _norm_rel(item.get("relative_path", "")),
                "content_hash": str(item.get("content_hash", "")).strip().lower(),
            }
        )
    return sorted(out, key=lambda row: (row["relative_path"], row["item_kind"], row["item_id_or_hash"], row["content_hash"]))


def compute_bundle_hash(items: Sequence[Mapping[str, object]]) -> str:
    return canonical_sha256({"included_artifacts": _bundle_projection(items)})


def stable_bundle_id(bundle_kind: str, items: Sequence[Mapping[str, object]]) -> str:
    token = str(bundle_kind or "").strip() or "bundle.unknown"
    return "{}.{}".format(token, compute_bundle_hash(items)[:16])


def normalize_bundle_manifest(payload: Mapping[str, object] | None) -> dict:
    row = _as_map(payload)
    items = [normalize_bundle_item(item) for item in _as_list(row.get("included_artifacts"))]
    items = sorted(
        items,
        key=lambda item: (
            str(item.get("relative_path", "")),
            str(item.get("item_kind", "")),
            str(item.get("item_id_or_hash", "")),
            str(item.get("content_hash", "")),
        ),
    )
    manifest = {
        "bundle_id": str(row.get("bundle_id", "")).strip(),
        "bundle_kind": str(row.get("bundle_kind", "")).strip(),
        "created_by_build_id": str(row.get("created_by_build_id", "")).strip(),
        "contract_registry_hash": str(row.get("contract_registry_hash", ZERO_SHA256)).strip().lower() or ZERO_SHA256,
        "included_artifacts": items,
        "included_hashes": [str(item.get("content_hash", "")).strip().lower() for item in items],
        "bundle_hash": str(row.get("bundle_hash", "")).strip().lower(),
        "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip().lower(),
        "extensions": normalize_extensions_map(_as_map(row.get("extensions"))),
    }
    if not manifest["bundle_hash"]:
        manifest["bundle_hash"] = compute_bundle_hash(items)
    if not manifest["bundle_id"]:
        manifest["bundle_id"] = stable_bundle_id(manifest["bundle_kind"], items)
    manifest["deterministic_fingerprint"] = deterministic_fingerprint(manifest)
    return _as_map(_normalize_value(manifest))


def build_bundle_manifest(
    *,
    bundle_kind: str,
    created_by_build_id: str,
    contract_registry_hash: str,
    included_artifacts: Sequence[Mapping[str, object]],
    bundle_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    items = [normalize_bundle_item(item) for item in list(included_artifacts or [])]
    bundle_hash = compute_bundle_hash(items)
    manifest = {
        "bundle_id": str(bundle_id or "").strip() or stable_bundle_id(bundle_kind, items),
        "bundle_kind": str(bundle_kind or "").strip(),
        "created_by_build_id": str(created_by_build_id or "").strip() or "build.unknown",
        "contract_registry_hash": str(contract_registry_hash or ZERO_SHA256).strip().lower() or ZERO_SHA256,
        "included_artifacts": items,
        "included_hashes": [str(item.get("content_hash", "")).strip().lower() for item in _bundle_projection(items)],
        "bundle_hash": bundle_hash,
        "deterministic_fingerprint": "",
        "extensions": normalize_extensions_map(_as_map(extensions)),
    }
    manifest["deterministic_fingerprint"] = deterministic_fingerprint(manifest)
    return normalize_bundle_manifest(manifest)


def build_hash_index_payload(items: Sequence[Mapping[str, object]], bundle_hash: str) -> dict:
    rows = [
        {
            "relative_path": str(item.get("relative_path", "")).strip(),
            "content_hash": str(item.get("content_hash", "")).strip().lower(),
        }
        for item in _bundle_projection(items)
    ]
    payload = {
        "hash_algorithm": HASH_ALGORITHM,
        "bundle_hash": str(bundle_hash or "").strip().lower(),
        "items": rows,
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(
        {
            "hash_algorithm": payload["hash_algorithm"],
            "bundle_hash": payload["bundle_hash"],
            "items": rows,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    )
    return _as_map(_normalize_value(payload))


def collect_file_entry(
    *,
    source_path: str,
    relative_path: str,
    item_kind: str,
    item_id_or_hash: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    abs_source = os.path.abspath(str(source_path or "").strip())
    return {
        "source_path": abs_source,
        "relative_path": _norm_rel(relative_path),
        "item_kind": str(item_kind or "").strip(),
        "item_id_or_hash": str(item_id_or_hash or "").strip(),
        "content_hash": sha256_file(abs_source),
        "extensions": normalize_extensions_map(_as_map(extensions)),
    }


def collect_directory_entries(
    *,
    source_root: str,
    bundle_rel_root: str,
    item_kind: str,
    item_id_or_hash: str,
    extensions: Mapping[str, object] | None = None,
) -> List[dict]:
    abs_root = os.path.abspath(str(source_root or "").strip())
    rows: List[dict] = []
    for rel_path in iter_rel_files(abs_root):
        rows.append(
            collect_file_entry(
                source_path=os.path.join(abs_root, rel_path.replace("/", os.sep)),
                relative_path="{}/{}".format(_norm_rel(bundle_rel_root), rel_path) if _norm_rel(bundle_rel_root) else rel_path,
                item_kind=item_kind,
                item_id_or_hash=item_id_or_hash,
                extensions=extensions,
            )
        )
    return rows


def write_bundle_directory(
    *,
    bundle_root: str,
    bundle_kind: str,
    created_by_build_id: str,
    contract_registry_hash: str,
    file_entries: Sequence[Mapping[str, object]],
    bundle_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    target_root = os.path.abspath(str(bundle_root or "").strip())
    ensure_dir(target_root)
    ensure_dir(os.path.join(target_root, BUNDLE_CONTENT_DIR))
    ensure_dir(os.path.join(target_root, BUNDLE_HASHES_DIR))

    items: List[dict] = []
    for row in sorted(
        list(file_entries or []),
        key=lambda item: (
            _norm_rel(_as_map(item).get("relative_path", "")),
            str(_as_map(item).get("item_kind", "")),
            str(_as_map(item).get("item_id_or_hash", "")),
        ),
    ):
        entry = collect_file_entry(
            source_path=str(_as_map(row).get("source_path", "")).strip(),
            relative_path=str(_as_map(row).get("relative_path", "")).strip(),
            item_kind=str(_as_map(row).get("item_kind", "")).strip(),
            item_id_or_hash=str(_as_map(row).get("item_id_or_hash", "")).strip(),
            extensions=_as_map(row).get("extensions"),
        )
        dest_path = os.path.join(target_root, BUNDLE_CONTENT_DIR, entry["relative_path"].replace("/", os.sep))
        ensure_dir(os.path.dirname(dest_path))
        shutil.copyfile(entry["source_path"], dest_path)
        items.append(normalize_bundle_item(entry))

    manifest = build_bundle_manifest(
        bundle_kind=bundle_kind,
        created_by_build_id=created_by_build_id,
        contract_registry_hash=contract_registry_hash,
        included_artifacts=items,
        bundle_id=bundle_id,
        extensions=extensions,
    )
    hash_index = build_hash_index_payload(list(manifest.get("included_artifacts") or []), str(manifest.get("bundle_hash", "")).strip())
    write_json(os.path.join(target_root, BUNDLE_MANIFEST_NAME), manifest)
    write_json(os.path.join(target_root, BUNDLE_HASH_INDEX_REL.replace("/", os.sep)), hash_index)
    return {
        "bundle_root": target_root.replace("\\", "/"),
        "bundle_manifest_path": os.path.join(target_root, BUNDLE_MANIFEST_NAME).replace("\\", "/"),
        "bundle_hash": str(manifest.get("bundle_hash", "")).strip(),
        "bundle_manifest": manifest,
        "hash_index": hash_index,
    }


def verify_bundle_directory(bundle_root: str) -> dict:
    target_root = os.path.abspath(str(bundle_root or "").strip())
    manifest_path = os.path.join(target_root, BUNDLE_MANIFEST_NAME)
    hash_index_path = os.path.join(target_root, BUNDLE_HASH_INDEX_REL.replace("/", os.sep))
    errors: List[dict] = []
    if not os.path.isfile(manifest_path):
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.manifest_missing",
            "errors": [{"code": "bundle_manifest_missing", "path": "$.bundle.manifest.json", "message": "bundle.manifest.json is missing"}],
            "bundle_manifest": {},
        }
    if not os.path.isfile(hash_index_path):
        return {
            "result": "refused",
            "refusal_code": "refusal.bundle.hash_index_missing",
            "errors": [{"code": "bundle_hash_index_missing", "path": "$.hashes.content", "message": "hashes/content.sha256.json is missing"}],
            "bundle_manifest": load_json(manifest_path),
        }

    manifest = normalize_bundle_manifest(load_json(manifest_path))
    hash_index = load_json(hash_index_path)
    content_root = os.path.join(target_root, BUNDLE_CONTENT_DIR)
    actual_rel_paths = iter_rel_files(content_root) if os.path.isdir(content_root) else []
    manifest_items = [normalize_bundle_item(item) for item in list(manifest.get("included_artifacts") or [])]
    expected_rel_paths = [str(item.get("relative_path", "")).strip() for item in manifest_items]
    if actual_rel_paths != expected_rel_paths:
        errors.append(
            {
                "code": "bundle_content_index_mismatch",
                "path": "$.included_artifacts",
                "message": "bundle content files do not match manifest ordering",
            }
        )

    actual_items: List[dict] = []
    for item in manifest_items:
        rel_path = str(item.get("relative_path", "")).strip()
        abs_path = os.path.join(content_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            errors.append(
                {
                    "code": "bundle_content_missing",
                    "path": "$.content.{}".format(rel_path),
                    "message": "bundle content file is missing",
                }
            )
            continue
        actual_hash = sha256_file(abs_path)
        if actual_hash != str(item.get("content_hash", "")).strip().lower():
            errors.append(
                {
                    "code": "bundle_content_hash_mismatch",
                    "path": "$.content.{}".format(rel_path),
                    "message": "bundle content hash mismatch",
                }
            )
        actual_items.append(
            normalize_bundle_item(
                {
                    "item_kind": item.get("item_kind"),
                    "item_id_or_hash": item.get("item_id_or_hash"),
                    "relative_path": rel_path,
                    "content_hash": actual_hash,
                    "extensions": item.get("extensions"),
                }
            )
        )

    actual_bundle_hash = compute_bundle_hash(actual_items)
    if actual_bundle_hash != str(manifest.get("bundle_hash", "")).strip().lower():
        errors.append(
            {
                "code": "bundle_hash_mismatch",
                "path": "$.bundle_hash",
                "message": "bundle hash mismatch",
            }
        )

    expected_fingerprint = deterministic_fingerprint(manifest)
    if expected_fingerprint != str(manifest.get("deterministic_fingerprint", "")).strip().lower():
        errors.append(
            {
                "code": "bundle_manifest_fingerprint_mismatch",
                "path": "$.deterministic_fingerprint",
                "message": "bundle manifest deterministic_fingerprint mismatch",
            }
        )

    expected_hash_index = build_hash_index_payload(actual_items, actual_bundle_hash)
    if canonical_sha256(hash_index) != canonical_sha256(expected_hash_index):
        errors.append(
            {
                "code": "bundle_hash_index_mismatch",
                "path": "$.hashes.content.sha256.json",
                "message": "bundle hash index does not match bundle contents",
            }
        )

    return {
        "result": "complete" if not errors else "refused",
        "refusal_code": "" if not errors else "refusal.bundle.hash_mismatch",
        "errors": sorted(errors, key=lambda row: (str(row.get("path", "")), str(row.get("code", "")))),
        "bundle_manifest": manifest,
        "hash_index": hash_index,
        "bundle_hash": actual_bundle_hash,
        "content_root": content_root.replace("\\", "/"),
    }


__all__ = [
    "BUNDLE_CONTENT_DIR",
    "BUNDLE_HASHES_DIR",
    "BUNDLE_HASH_INDEX_NAME",
    "BUNDLE_HASH_INDEX_REL",
    "BUNDLE_MANIFEST_NAME",
    "HASH_ALGORITHM",
    "ZERO_SHA256",
    "build_bundle_manifest",
    "build_hash_index_payload",
    "canonical_sha256",
    "collect_directory_entries",
    "collect_file_entry",
    "deterministic_fingerprint",
    "ensure_dir",
    "iter_rel_files",
    "load_json",
    "normalize_bundle_item",
    "normalize_bundle_manifest",
    "sha256_file",
    "stable_bundle_id",
    "verify_bundle_directory",
    "write_bundle_directory",
    "write_json",
]
