"""Canonical UNIVERSAL-ID helpers."""

from __future__ import annotations

import json
import os
import re
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


UNIVERSAL_IDENTITY_FIELD = "universal_identity_block"
UNIVERSAL_IDENTITY_SCHEMA_NAME = "universal_identity_block"

IDENTITY_KIND_SUITE_RELEASE = "identity.suite_release"
IDENTITY_KIND_PRODUCT_BINARY = "identity.product_binary"
IDENTITY_KIND_PACK = "identity.pack"
IDENTITY_KIND_BUNDLE = "identity.bundle"
IDENTITY_KIND_PROTOCOL = "identity.protocol"
IDENTITY_KIND_SCHEMA = "identity.schema"
IDENTITY_KIND_FORMAT = "identity.format"
IDENTITY_KIND_INSTALL = "identity.install"
IDENTITY_KIND_INSTANCE = "identity.instance"
IDENTITY_KIND_SAVE = "identity.save"
IDENTITY_KIND_MANIFEST = "identity.manifest"
IDENTITY_KIND_REPRO_BUNDLE = "identity.repro_bundle"
IDENTITY_KIND_LICENSE_CAPABILITY = "identity.license_capability"

IDENTITY_KINDS = (
    IDENTITY_KIND_BUNDLE,
    IDENTITY_KIND_FORMAT,
    IDENTITY_KIND_INSTALL,
    IDENTITY_KIND_INSTANCE,
    IDENTITY_KIND_LICENSE_CAPABILITY,
    IDENTITY_KIND_MANIFEST,
    IDENTITY_KIND_PACK,
    IDENTITY_KIND_PRODUCT_BINARY,
    IDENTITY_KIND_PROTOCOL,
    IDENTITY_KIND_REPRO_BUNDLE,
    IDENTITY_KIND_SAVE,
    IDENTITY_KIND_SCHEMA,
    IDENTITY_KIND_SUITE_RELEASE,
)

_CONTENT_HASH_REQUIRED_KINDS = {
    IDENTITY_KIND_BUNDLE,
    IDENTITY_KIND_LICENSE_CAPABILITY,
    IDENTITY_KIND_MANIFEST,
    IDENTITY_KIND_PACK,
    IDENTITY_KIND_PRODUCT_BINARY,
    IDENTITY_KIND_REPRO_BUNDLE,
    IDENTITY_KIND_SCHEMA,
    IDENTITY_KIND_SUITE_RELEASE,
}
_KIND_REQUIRED_FIELDS = {
    IDENTITY_KIND_PACK: ("content_hash", "semver"),
    IDENTITY_KIND_PRODUCT_BINARY: ("content_hash", "build_id"),
    IDENTITY_KIND_LICENSE_CAPABILITY: ("content_hash", "schema_version"),
    IDENTITY_KIND_SAVE: ("contract_bundle_hash", "format_version"),
    IDENTITY_KIND_PROTOCOL: ("protocol_range",),
    IDENTITY_KIND_SCHEMA: ("content_hash", "schema_version"),
}
_SCAN_FILENAMES = {
    "release_manifest.json",
    "release_index.json",
    "install.manifest.json",
    "instance.manifest.json",
    "save.manifest.json",
    "pack.compat.json",
    "bundle.manifest.json",
}
_CANDIDATE_PATH_TOKENS = (
    "/locks/",
    "/profiles/bundles/",
    "/negotiation/",
    "/repro/",
    "/diag/",
)
_IDENTITY_ALLOWED_FIELDS = {
    "identity_kind_id",
    "identity_id",
    "content_hash",
    "semver",
    "build_id",
    "format_version",
    "schema_version",
    "protocol_range",
    "contract_bundle_hash",
    "stability_class_id",
    "deterministic_fingerprint",
    "extensions",
}
_IDENTITY_REQUIRED_FIELDS = {
    "identity_kind_id",
    "identity_id",
    "stability_class_id",
    "deterministic_fingerprint",
    "extensions",
}
_HEX64_RE = re.compile(r"^[A-Fa-f0-9]{64}$")


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _norm_rel(path: object) -> str:
    return _token(path).replace("\\", "/")


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(dict(value).items(), key=lambda row: str(row[0]))
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in list(value)]
    if isinstance(value, tuple):
        return [_normalize_tree(item) for item in list(value)]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


def _canonical_protocol_range(value: object) -> dict:
    payload = _as_map(value)
    return {
        str(key): _normalize_tree(item)
        for key, item in sorted(payload.items(), key=lambda row: str(row[0]))
        if str(key).strip()
    }


def _identity_seed(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    seed = {
        "identity_kind_id": _token(item.get("identity_kind_id")),
        "identity_id": _token(item.get("identity_id")),
        "stability_class_id": _token(item.get("stability_class_id")),
        "deterministic_fingerprint": "",
        "extensions": _as_map(_normalize_tree(item.get("extensions"))),
    }
    content_hash = _token(item.get("content_hash")).lower()
    if content_hash:
        seed["content_hash"] = content_hash
    semver = _token(item.get("semver"))
    if semver:
        seed["semver"] = semver
    build_id = _token(item.get("build_id"))
    if build_id:
        seed["build_id"] = build_id
    format_version = _token(item.get("format_version"))
    if format_version:
        seed["format_version"] = format_version
    schema_version = _token(item.get("schema_version"))
    if schema_version:
        seed["schema_version"] = schema_version
    protocol_range = _canonical_protocol_range(item.get("protocol_range"))
    if protocol_range:
        seed["protocol_range"] = protocol_range
    contract_bundle_hash = _token(item.get("contract_bundle_hash")).lower()
    if contract_bundle_hash:
        seed["contract_bundle_hash"] = contract_bundle_hash
    return seed


def universal_identity_block_fingerprint(payload: Mapping[str, object] | None) -> str:
    return canonical_sha256(_identity_seed(payload))


def canonicalize_universal_identity_block(payload: Mapping[str, object] | None) -> dict:
    item = _identity_seed(payload)
    item["deterministic_fingerprint"] = universal_identity_block_fingerprint(item)
    return item


def identity_content_hash_for_payload(payload: Mapping[str, object] | None) -> str:
    body = dict(_as_map(_normalize_tree(payload)))
    body.pop(UNIVERSAL_IDENTITY_FIELD, None)
    if isinstance(body.get("deterministic_fingerprint"), str):
        body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def build_universal_identity_block(
    *,
    identity_kind_id: str,
    identity_id: str,
    stability_class_id: str,
    payload: Mapping[str, object] | None = None,
    content_hash: str = "",
    semver: str = "",
    build_id: str = "",
    format_version: str = "",
    schema_version: str = "",
    protocol_range: Mapping[str, object] | None = None,
    contract_bundle_hash: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    computed_content_hash = _token(content_hash).lower()
    if not computed_content_hash and payload is not None:
        computed_content_hash = identity_content_hash_for_payload(payload)
    return canonicalize_universal_identity_block(
        {
            "identity_kind_id": _token(identity_kind_id),
            "identity_id": _token(identity_id),
            "content_hash": computed_content_hash,
            "semver": _token(semver),
            "build_id": _token(build_id),
            "format_version": _token(format_version),
            "schema_version": _token(schema_version),
            "protocol_range": _canonical_protocol_range(protocol_range),
            "contract_bundle_hash": _token(contract_bundle_hash).lower(),
            "stability_class_id": _token(stability_class_id),
            "extensions": _as_map(_normalize_tree(extensions)),
        }
    )


def _validate_identity_schema(payload: Mapping[str, object] | None, *, path: str = "") -> list[dict]:
    rel_path = _norm_rel(path)
    item = _as_map(payload)
    errors: list[dict] = []
    for field in sorted(_IDENTITY_REQUIRED_FIELDS):
        value = item.get(field)
        present = bool(_token(value)) if field != "extensions" else isinstance(value, Mapping)
        if not present:
            errors.append(
                {
                    "code": "identity_block_schema_invalid",
                    "path": "{}{}.{}".format(rel_path, "." if rel_path else "", field),
                    "message": "missing required field '{}'".format(field),
                }
            )
    for field in sorted(item.keys(), key=lambda value: str(value)):
        key = str(field)
        if key in _IDENTITY_ALLOWED_FIELDS:
            continue
        errors.append(
            {
                "code": "identity_block_schema_invalid",
                "path": "{}{}.{}".format(rel_path, "." if rel_path else "", key),
                "message": "unknown field '{}'".format(key),
            }
        )
    for field in ("identity_kind_id", "identity_id", "semver", "build_id", "format_version", "schema_version", "stability_class_id"):
        if field not in item:
            continue
        if not isinstance(item.get(field), str):
            errors.append(
                {
                    "code": "identity_block_schema_invalid",
                    "path": "{}{}.{}".format(rel_path, "." if rel_path else "", field),
                    "message": "field '{}' must be a string".format(field),
                }
            )
    for field in ("content_hash", "contract_bundle_hash", "deterministic_fingerprint"):
        if field not in item:
            continue
        value = item.get(field)
        if not isinstance(value, str) or not _HEX64_RE.fullmatch(value):
            errors.append(
                {
                    "code": "identity_block_schema_invalid",
                    "path": "{}{}.{}".format(rel_path, "." if rel_path else "", field),
                    "message": "field '{}' must be a 64-character hex sha256".format(field),
                }
            )
    if "protocol_range" in item and not isinstance(item.get("protocol_range"), Mapping):
        errors.append(
            {
                "code": "identity_block_schema_invalid",
                "path": "{}{}.protocol_range".format(rel_path, "." if rel_path else ""),
                "message": "field 'protocol_range' must be an object",
            }
        )
    if "extensions" in item and not isinstance(item.get("extensions"), Mapping):
        errors.append(
            {
                "code": "identity_block_schema_invalid",
                "path": "{}{}.extensions".format(rel_path, "." if rel_path else ""),
                "message": "field 'extensions' must be an object",
            }
        )
    return sorted(errors, key=lambda row: (_token(row.get("path")), _token(row.get("message"))))


def attach_universal_identity_block(
    payload: Mapping[str, object] | None,
    *,
    identity_kind_id: str,
    identity_id: str,
    stability_class_id: str,
    semver: str = "",
    build_id: str = "",
    format_version: str = "",
    schema_version: str = "",
    protocol_range: Mapping[str, object] | None = None,
    contract_bundle_hash: str = "",
    extensions: Mapping[str, object] | None = None,
    content_hash: str = "",
) -> dict:
    body = dict(_as_map(payload))
    body[UNIVERSAL_IDENTITY_FIELD] = build_universal_identity_block(
        identity_kind_id=identity_kind_id,
        identity_id=identity_id,
        stability_class_id=stability_class_id,
        payload=body,
        content_hash=content_hash,
        semver=semver,
        build_id=build_id,
        format_version=format_version,
        schema_version=schema_version,
        protocol_range=protocol_range,
        contract_bundle_hash=contract_bundle_hash,
        extensions=extensions,
    )
    return body


def _namespaced(identity_id: str) -> bool:
    token = _token(identity_id)
    if not token or "." not in token:
        return False
    if any(ch in token for ch in ("/", "\\", " ", "\t", "\r", "\n")):
        return False
    return True


def _infer_identity_kind(rel_path: str, payload: Mapping[str, object] | None) -> str:
    path = _norm_rel(rel_path)
    name = os.path.basename(path)
    item = _as_map(payload)
    if name == "release_manifest.json":
        return IDENTITY_KIND_SUITE_RELEASE
    if name == "release_index.json":
        return IDENTITY_KIND_SUITE_RELEASE
    if name == "install.manifest.json":
        return IDENTITY_KIND_INSTALL
    if name == "instance.manifest.json":
        return IDENTITY_KIND_INSTANCE
    if name == "save.manifest.json":
        return IDENTITY_KIND_SAVE
    if name == "pack.compat.json":
        return IDENTITY_KIND_PACK
    if name == "bundle.manifest.json":
        return IDENTITY_KIND_REPRO_BUNDLE
    if _token(item.get("pack_lock_id")):
        return IDENTITY_KIND_BUNDLE
    if _token(item.get("profile_bundle_id")) or _token(item.get("artifact_kind_id")) == "artifact.profile_bundle":
        return IDENTITY_KIND_BUNDLE
    if _token(item.get("artifact_kind_id")) == "artifact.license_capability":
        return IDENTITY_KIND_LICENSE_CAPABILITY
    if _token(item.get("negotiation_id")):
        return IDENTITY_KIND_MANIFEST
    return IDENTITY_KIND_MANIFEST


def _candidate_identity_json(rel_path: str) -> bool:
    path = _norm_rel(rel_path).lower()
    name = os.path.basename(path)
    if name in _SCAN_FILENAMES:
        return True
    if not name.endswith(".json"):
        return False
    if "pack_lock" in name or "pack_lock" in path:
        return True
    if "profile_bundle" in name or "profile.bundle" in name or "/profiles/bundles/" in path:
        return True
    if "license_capability" in name or "license_capability" in path:
        return True
    if "negotiation" in name or "negotiation_record" in name:
        return True
    return any(token in path for token in _CANDIDATE_PATH_TOKENS)


def _expected_identity_fields(rel_path: str, payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    kind = _infer_identity_kind(rel_path, item)
    basename = os.path.basename(_norm_rel(rel_path))
    extensions = {"official.rel_path": _norm_rel(rel_path)}
    if basename == "release_manifest.json":
        return {
            "identity_kind_id": kind,
            "identity_id": "identity.release.{}".format(_token(item.get("release_id")) or "unknown"),
            "content_hash": identity_content_hash_for_payload(item),
            "semver": _token(_as_map(item.get("extensions")).get("release_semver")),
            "build_id": "",
            "format_version": _token(item.get("manifest_version")),
            "schema_version": _token(item.get("manifest_version")),
            "protocol_range": {},
            "contract_bundle_hash": _token(item.get("semantic_contract_registry_hash")).lower(),
            "stability_class_id": "provisional",
            "extensions": extensions,
        }
    if basename == "release_index.json":
        return {
            "identity_kind_id": kind,
            "identity_id": "identity.release_index.{}".format(_token(_as_map(item.get("extensions")).get("release_id")) or _token(item.get("channel")) or "unknown"),
            "content_hash": identity_content_hash_for_payload(item),
            "semver": "",
            "build_id": "",
            "format_version": "1.0.0",
            "schema_version": "1.0.0",
            "protocol_range": _as_map(item.get("supported_protocol_ranges")),
            "contract_bundle_hash": _token(item.get("semantic_contract_registry_hash")).lower(),
            "stability_class_id": "provisional",
            "extensions": extensions,
        }
    if basename == "install.manifest.json":
        return {
            "identity_kind_id": kind,
            "identity_id": "identity.install.{}".format(_token(item.get("install_id")) or "unknown"),
            "content_hash": identity_content_hash_for_payload(item),
            "semver": _token(item.get("install_version")),
            "build_id": "",
            "format_version": "",
            "schema_version": _token(item.get("schema_version")) or "2.0.0",
            "protocol_range": _as_map(item.get("supported_protocol_versions")),
            "contract_bundle_hash": _token(item.get("semantic_contract_registry_hash")).lower(),
            "stability_class_id": "provisional",
            "extensions": extensions,
        }
    if basename == "instance.manifest.json":
        required_ranges = _as_map(item.get("required_contract_ranges"))
        return {
            "identity_kind_id": kind,
            "identity_id": "identity.instance.{}".format(_token(item.get("instance_id")) or "unknown"),
            "content_hash": identity_content_hash_for_payload(item),
            "semver": "",
            "build_id": "",
            "format_version": "",
            "schema_version": _token(item.get("schema_version")) or "2.1.0",
            "protocol_range": {},
            "contract_bundle_hash": canonical_sha256(required_ranges) if required_ranges else "",
            "stability_class_id": "provisional",
            "extensions": extensions,
        }
    if basename == "save.manifest.json":
        return {
            "identity_kind_id": kind,
            "identity_id": "identity.save.{}".format(_token(item.get("save_id")) or "unknown"),
            "content_hash": identity_content_hash_for_payload(item),
            "semver": "",
            "build_id": _token(item.get("created_by_build_id")),
            "format_version": _token(item.get("save_format_version")) or _token(item.get("format_version")),
            "schema_version": _token(item.get("schema_version")) or "1.1.0",
            "protocol_range": {},
            "contract_bundle_hash": _token(item.get("universe_contract_bundle_hash") or item.get("contract_bundle_hash")).lower(),
            "stability_class_id": "provisional",
            "extensions": extensions,
        }
    if basename == "pack.compat.json":
        return {
            "identity_kind_id": kind,
            "identity_id": "identity.pack.{}".format(_token(item.get("pack_id")) or "unknown"),
            "content_hash": identity_content_hash_for_payload(item),
            "semver": _token(item.get("pack_version")),
            "build_id": "",
            "format_version": "",
            "schema_version": _token(item.get("schema_version")) or "1.0.0",
            "protocol_range": _as_map(item.get("required_protocol_ranges")),
            "contract_bundle_hash": "",
            "stability_class_id": "provisional",
            "extensions": extensions,
        }
    if _token(item.get("pack_lock_id")):
        return {
            "identity_kind_id": IDENTITY_KIND_BUNDLE,
            "identity_id": "identity.bundle.{}".format(_token(item.get("pack_lock_id")) or "unknown"),
            "content_hash": identity_content_hash_for_payload(item),
            "semver": "",
            "build_id": _token(item.get("engine_version_created")),
            "format_version": _token(item.get("format_version")),
            "schema_version": _token(item.get("schema_version")) or "1.0.0",
            "protocol_range": {},
            "contract_bundle_hash": _token(item.get("engine_contract_bundle_hash")).lower(),
            "stability_class_id": "provisional",
            "extensions": extensions,
        }
    if _token(item.get("profile_bundle_id")) or _token(item.get("artifact_kind_id")) == "artifact.profile_bundle":
        return {
            "identity_kind_id": IDENTITY_KIND_BUNDLE,
            "identity_id": "identity.bundle.{}".format(_token(item.get("profile_bundle_id") or item.get("artifact_id")) or "unknown"),
            "content_hash": identity_content_hash_for_payload(item),
            "semver": "",
            "build_id": _token(item.get("engine_version_created")),
            "format_version": _token(item.get("format_version")),
            "schema_version": _token(item.get("schema_version")) or "1.0.0",
            "protocol_range": {},
            "contract_bundle_hash": "",
            "stability_class_id": "provisional",
            "extensions": extensions,
        }
    if _token(item.get("artifact_kind_id")) == "artifact.license_capability":
        return {
            "identity_kind_id": IDENTITY_KIND_LICENSE_CAPABILITY,
            "identity_id": "identity.license_capability.{}".format(
                _token(item.get("artifact_id")) or _token(_as_map(item.get(UNIVERSAL_IDENTITY_FIELD)).get("identity_id")) or "unknown"
            ),
            "content_hash": identity_content_hash_for_payload(item),
            "semver": "",
            "build_id": "",
            "format_version": "",
            "schema_version": _token(item.get("schema_version")) or "1.0.0",
            "protocol_range": {},
            "contract_bundle_hash": "",
            "stability_class_id": "provisional",
            "extensions": extensions,
        }
    if basename == "bundle.manifest.json":
        return {
            "identity_kind_id": IDENTITY_KIND_REPRO_BUNDLE,
            "identity_id": "identity.repro_bundle.{}".format(_token(item.get("session_id")) or _token(item.get("bundle_hash"))[:16] or "unknown"),
            "content_hash": _token(item.get("bundle_hash")).lower() or identity_content_hash_for_payload(item),
            "semver": "",
            "build_id": _token(item.get("build_id")),
            "format_version": _token(item.get("bundle_version")),
            "schema_version": _token(item.get("schema_version")) or "1.0.0",
            "protocol_range": {},
            "contract_bundle_hash": _token(item.get("contract_bundle_hash")).lower(),
            "stability_class_id": "provisional",
            "extensions": extensions,
        }
    if _token(item.get("negotiation_id")):
        return {
            "identity_kind_id": IDENTITY_KIND_MANIFEST,
            "identity_id": "identity.negotiation.{}".format(_token(item.get("negotiation_id")) or "unknown"),
            "content_hash": identity_content_hash_for_payload(item),
            "semver": "",
            "build_id": "",
            "format_version": _token(item.get("schema_version")) or "1.0.0",
            "schema_version": _token(item.get("schema_version")) or "1.0.0",
            "protocol_range": {
                "protocol_id": _token(item.get("chosen_protocol_id")),
                "min_version": _token(item.get("chosen_protocol_version")),
                "max_version": _token(item.get("chosen_protocol_version")),
            },
            "contract_bundle_hash": _token(_as_map(item.get("input_hashes")).get("chosen_contract_bundle_hash")).lower(),
            "stability_class_id": "provisional",
            "extensions": extensions,
        }
    return {
        "identity_kind_id": kind,
        "identity_id": "identity.manifest.{}".format(os.path.basename(_norm_rel(rel_path)) or "unknown"),
        "content_hash": identity_content_hash_for_payload(item),
        "semver": "",
        "build_id": "",
        "format_version": _token(item.get("format_version")),
        "schema_version": _token(item.get("schema_version")),
        "protocol_range": {},
        "contract_bundle_hash": _token(item.get("contract_bundle_hash")).lower(),
        "stability_class_id": "provisional",
        "extensions": extensions,
    }


def validate_identity_block(
    *,
    repo_root: str,
    identity_block: Mapping[str, object] | None,
    expected: Mapping[str, object] | None = None,
    strict_missing: bool = False,
    path: str = "",
) -> dict:
    block = _as_map(identity_block)
    warnings: list[dict] = []
    errors: list[dict] = []
    rel_path = _norm_rel(path)
    if not block:
        if strict_missing:
            errors.append({"code": "identity_block_missing", "path": rel_path, "message": "artifact is missing universal_identity_block"})
        else:
            warnings.append({"code": "identity_block_missing", "path": rel_path, "message": "artifact is missing universal_identity_block"})
        return {"result": "complete" if not errors else "refused", "errors": errors, "warnings": warnings}

    schema_errors = _validate_identity_schema(block, path="{}.{}".format(rel_path, UNIVERSAL_IDENTITY_FIELD) if rel_path else UNIVERSAL_IDENTITY_FIELD)
    if schema_errors:
        errors.extend(schema_errors)
        return {"result": "refused", "errors": errors, "warnings": warnings}

    if _token(block.get("identity_kind_id")) not in IDENTITY_KINDS:
        errors.append({"code": "identity_kind_invalid", "path": "{}.{}".format(rel_path, UNIVERSAL_IDENTITY_FIELD), "message": "identity_kind_id is not declared in the identity kind registry"})
    if not _namespaced(_token(block.get("identity_id"))):
        errors.append({"code": "identity_id_not_namespaced", "path": "{}.{}.identity_id".format(rel_path, UNIVERSAL_IDENTITY_FIELD), "message": "identity_id must be a namespaced token and must not contain path separators"})

    expected_fp = universal_identity_block_fingerprint(block)
    if _token(block.get("deterministic_fingerprint")).lower() != expected_fp:
        errors.append({"code": "identity_block_fingerprint_mismatch", "path": "{}.{}.deterministic_fingerprint".format(rel_path, UNIVERSAL_IDENTITY_FIELD), "message": "universal identity deterministic_fingerprint mismatch"})

    kind = _token(block.get("identity_kind_id"))
    for field in _KIND_REQUIRED_FIELDS.get(kind, ()):
        value = block.get(field)
        present = bool(_token(value)) if not isinstance(value, Mapping) else bool(_as_map(value))
        if not present:
            errors.append({"code": "identity_kind_missing_required_field", "path": "{}.{}.{}".format(rel_path, UNIVERSAL_IDENTITY_FIELD, field), "message": "{} requires '{}'".format(kind, field)})
    if kind in _CONTENT_HASH_REQUIRED_KINDS and not _token(block.get("content_hash")):
        errors.append({"code": "identity_content_hash_missing", "path": "{}.{}.content_hash".format(rel_path, UNIVERSAL_IDENTITY_FIELD), "message": "{} requires content_hash".format(kind)})

    expected_map = _as_map(expected)
    for field in ("identity_kind_id", "identity_id", "content_hash", "semver", "build_id", "format_version", "schema_version", "contract_bundle_hash", "stability_class_id"):
        expected_value = _token(expected_map.get(field))
        if not expected_value:
            continue
        actual_value = _token(block.get(field))
        if actual_value.lower() != expected_value.lower():
            errors.append({"code": "identity_field_mismatch", "path": "{}.{}.{}".format(rel_path, UNIVERSAL_IDENTITY_FIELD, field), "message": "identity field '{}' does not match canonical artifact expectations".format(field)})
    if expected_map.get("protocol_range"):
        actual_protocol = _canonical_protocol_range(block.get("protocol_range"))
        expected_protocol = _canonical_protocol_range(expected_map.get("protocol_range"))
        if actual_protocol != expected_protocol:
            errors.append({"code": "identity_protocol_range_mismatch", "path": "{}.{}.protocol_range".format(rel_path, UNIVERSAL_IDENTITY_FIELD), "message": "protocol_range does not match canonical artifact expectations"})

    return {"result": "complete" if not errors else "refused", "errors": errors, "warnings": warnings}


def validate_identity_path(repo_root: str, rel_path: str, *, strict_missing: bool = False) -> dict:
    abs_path = os.path.normpath(os.path.abspath(os.path.join(repo_root, rel_path.replace("/", os.sep))))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {"result": "refused", "path": _norm_rel(rel_path), "errors": [{"code": "identity_payload_invalid", "path": _norm_rel(rel_path), "message": "unable to load JSON payload"}], "warnings": [], "expected": {}, "identity_block": {}}
    if not isinstance(payload, Mapping):
        return {"result": "refused", "path": _norm_rel(rel_path), "errors": [{"code": "identity_payload_invalid", "path": _norm_rel(rel_path), "message": "JSON root must be an object"}], "warnings": [], "expected": {}, "identity_block": {}}
    expected = _expected_identity_fields(rel_path, payload)
    validation = validate_identity_block(repo_root=repo_root, identity_block=_as_map(payload).get(UNIVERSAL_IDENTITY_FIELD), expected=expected, strict_missing=strict_missing, path=_norm_rel(rel_path))
    return {
        "result": _token(validation.get("result")) or "complete",
        "path": _norm_rel(rel_path),
        "errors": list(validation.get("errors") or []),
        "warnings": list(validation.get("warnings") or []),
        "expected": expected,
        "identity_block": canonicalize_universal_identity_block(_as_map(payload).get(UNIVERSAL_IDENTITY_FIELD)) if _as_map(payload).get(UNIVERSAL_IDENTITY_FIELD) else {},
    }


def validate_identity_repo(repo_root: str, *, strict_missing: bool = False) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    reports: list[dict] = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name not in {".git", "__pycache__", ".pytest_cache", "build"})
        rel_root = os.path.relpath(current_root, root)
        rel_root = "" if rel_root == "." else rel_root
        for name in sorted(filenames):
            rel_path = os.path.join(rel_root, name) if rel_root else name
            rel_norm = _norm_rel(rel_path)
            payload_path = os.path.join(current_root, name)
            if _candidate_identity_json(rel_norm):
                if name in _SCAN_FILENAMES:
                    reports.append(validate_identity_path(root, rel_norm, strict_missing=strict_missing))
                    continue
                try:
                    with open(payload_path, "r", encoding="utf-8") as handle:
                        payload = json.load(handle)
                except (OSError, ValueError):
                    continue
                if not isinstance(payload, Mapping):
                    continue
                if _token(_as_map(payload).get("pack_lock_id")) or _token(_as_map(payload).get("profile_bundle_id")) or _token(_as_map(payload).get("negotiation_id")):
                    reports.append(validate_identity_path(root, rel_norm, strict_missing=strict_missing))
                continue
    reports = sorted(reports, key=lambda row: _token(row.get("path")))
    error_count = sum(len(_as_list(_as_map(row).get("errors"))) for row in reports)
    warning_count = sum(len(_as_list(_as_map(row).get("warnings"))) for row in reports)
    return {
        "result": "complete" if error_count == 0 else "refused",
        "strict_missing": bool(strict_missing),
        "reports": reports,
        "error_count": int(error_count),
        "warning_count": int(warning_count),
        "deterministic_fingerprint": canonical_sha256({"strict_missing": bool(strict_missing), "reports": reports}),
    }
