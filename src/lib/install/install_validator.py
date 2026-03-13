"""Deterministic install manifest normalization, validation, and registry helpers."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from src.appshell.paths import VROOT_INSTALL, get_current_virtual_paths, vpath_resolve_existing
from src.meta_extensions_engine import normalize_extensions_map, normalize_extensions_tree
from tools.xstack.compatx.canonical_json import canonical_sha256


DEFAULT_INSTALL_REGISTRY_REL = os.path.join("data", "registries", "install_registry.json")

REFUSAL_INSTALL_MISSING_BINARY = "refusal.install.missing_binary"
REFUSAL_INSTALL_HASH_MISMATCH = "refusal.install.hash_mismatch"
REFUSAL_INSTALL_CONTRACT_REGISTRY_MISMATCH = "refusal.install.contract_registry_mismatch"
PATH_LIKE_KEYS = {
    "binary_ref",
    "descriptor_ref",
    "manifest_ref",
    "path",
    "root_path",
}


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _norm(path: object) -> str:
    return str(path or "").replace("\\", "/")


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, _norm(path)
    if not isinstance(payload, dict):
        return {}, _norm(path)
    return _normalize_value(normalize_extensions_tree(payload)), ""


def _normalize_value(value: object, key: str = "") -> object:
    if isinstance(value, Mapping):
        return {
            str(name): _normalize_value(item, str(name))
            for name, item in sorted(dict(value).items(), key=lambda row: str(row[0]))
        }
    if isinstance(value, list):
        return [_normalize_value(item) for item in list(value)]
    if isinstance(value, str):
        if key in PATH_LIKE_KEYS or key.endswith(("_path", "_ref", "_root")):
            return _norm(value)
        return value
    return value


def write_json(path: str, payload: Mapping[str, object]) -> str:
    target = os.path.abspath(str(path or "").strip())
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(_normalize_value(normalize_extensions_tree(dict(payload or {}))), handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")
    return target


def deterministic_fingerprint(payload: Mapping[str, object]) -> str:
    body = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    if isinstance(body, dict):
        body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def sha256_file(path: str) -> str:
    import hashlib

    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_install_id(seed_payload: Mapping[str, object]) -> str:
    return "install.{}".format(canonical_sha256(_normalize_value(normalize_extensions_tree(dict(seed_payload or {}))))[:24])


def _semver_tuple(value: object) -> Tuple[int, int, int]:
    token = str(value or "").strip()
    parts = token.split(".")
    if len(parts) != 3:
        return (0, 0, 0)
    out = []
    for item in parts:
        try:
            out.append(int(item))
        except ValueError:
            out.append(0)
    return (out[0], out[1], out[2])


def _semver_min(left: str, right: str) -> str:
    if not left:
        return right
    if not right:
        return left
    return left if _semver_tuple(left) <= _semver_tuple(right) else right


def _semver_max(left: str, right: str) -> str:
    if not left:
        return right
    if not right:
        return left
    return left if _semver_tuple(left) >= _semver_tuple(right) else right


def _stable_relpath(base_root: str, target_path: str) -> str:
    try:
        rel = os.path.relpath(os.path.abspath(target_path), os.path.abspath(base_root))
    except ValueError:
        return ""
    return _norm(rel)


def normalize_protocol_range(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    out = {
        "schema_version": str(payload.get("schema_version", "1.0.0")).strip() or "1.0.0",
        "protocol_id": str(payload.get("protocol_id", "")).strip() or "protocol.unknown",
        "min_version": str(payload.get("min_version", "0.0.0")).strip() or "0.0.0",
        "max_version": str(payload.get("max_version", "0.0.0")).strip() or "0.0.0",
        "deterministic_fingerprint": "",
        "extensions": normalize_extensions_map(_as_map(payload.get("extensions"))),
    }
    if _semver_tuple(out["max_version"]) < _semver_tuple(out["min_version"]):
        out["max_version"] = out["min_version"]
    out["deterministic_fingerprint"] = deterministic_fingerprint(out)
    return out


def normalize_contract_range(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    min_version = int(payload.get("min_version", 1) or 1)
    max_version = int(payload.get("max_version", min_version) or min_version)
    if max_version < min_version:
        max_version = min_version
    out = {
        "schema_version": str(payload.get("schema_version", "1.0.0")).strip() or "1.0.0",
        "contract_category_id": str(payload.get("contract_category_id", "")).strip(),
        "min_version": min_version,
        "max_version": max_version,
        "deterministic_fingerprint": "",
        "extensions": normalize_extensions_map(_as_map(payload.get("extensions"))),
    }
    out["deterministic_fingerprint"] = deterministic_fingerprint(out)
    return out


def merge_protocol_ranges(rows: Sequence[Mapping[str, object]] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in list(rows or []):
        normalized = normalize_protocol_range(row)
        protocol_id = str(normalized.get("protocol_id", "")).strip()
        current = dict(out.get(protocol_id) or {})
        if not current:
            out[protocol_id] = normalized
            continue
        current["min_version"] = _semver_min(str(current.get("min_version", "")), str(normalized.get("min_version", "")))
        current["max_version"] = _semver_max(str(current.get("max_version", "")), str(normalized.get("max_version", "")))
        current["deterministic_fingerprint"] = deterministic_fingerprint(current)
        out[protocol_id] = current
    return dict((key, out[key]) for key in sorted(out.keys()))


def merge_contract_ranges(rows: Sequence[Mapping[str, object]] | None) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in list(rows or []):
        normalized = normalize_contract_range(row)
        contract_id = str(normalized.get("contract_category_id", "")).strip()
        if not contract_id:
            continue
        current = dict(out.get(contract_id) or {})
        if not current:
            out[contract_id] = normalized
            continue
        current["min_version"] = min(int(current.get("min_version", 1) or 1), int(normalized.get("min_version", 1) or 1))
        current["max_version"] = max(int(current.get("max_version", 1) or 1), int(normalized.get("max_version", 1) or 1))
        current["deterministic_fingerprint"] = deterministic_fingerprint(current)
        out[contract_id] = current
    return dict((key, out[key]) for key in sorted(out.keys()))


def build_product_build_descriptor(
    *,
    product_id: str,
    build_id: str,
    binary_hash: str,
    endpoint_descriptor_hash: str,
    binary_ref: str = "",
    descriptor_ref: str = "",
    product_version: str = "",
) -> dict:
    payload = {
        "product_id": str(product_id or "").strip(),
        "build_id": str(build_id or "").strip(),
        "binary_hash": str(binary_hash or "").strip(),
        "endpoint_descriptor_hash": str(endpoint_descriptor_hash or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": normalize_extensions_map(
            {
                "official.binary_ref": _norm(binary_ref),
                "official.descriptor_ref": _norm(descriptor_ref),
                "official.product_version": str(product_version or "").strip(),
            }
        ),
    }
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    return payload


def collect_manifest_product_descriptors(manifest_payload: Mapping[str, object]) -> Dict[str, dict]:
    manifest = _normalize_value(normalize_extensions_tree(dict(manifest_payload or {})))
    explicit = _as_map(manifest.get("product_build_descriptors"))
    if explicit:
        out = {}
        for product_id, row in sorted(explicit.items(), key=lambda item: str(item[0])):
            payload = _as_map(row)
            extensions = _as_map(payload.get("extensions"))
            descriptor = build_product_build_descriptor(
                product_id=str(payload.get("product_id", product_id)).strip(),
                build_id=str(payload.get("build_id", "")).strip(),
                binary_hash=str(payload.get("binary_hash", "")).strip(),
                endpoint_descriptor_hash=str(payload.get("endpoint_descriptor_hash", "")).strip(),
                binary_ref=str(extensions.get("official.binary_ref", "")).strip(),
                descriptor_ref=str(extensions.get("official.descriptor_ref", "")).strip(),
                product_version=str(extensions.get("official.product_version", "")).strip(),
            )
            out[str(descriptor.get("product_id", product_id)).strip()] = descriptor
        return dict((key, out[key]) for key in sorted(out.keys()))

    binaries = _as_map(manifest.get("binaries"))
    out = {}
    for product_id, row in sorted(binaries.items(), key=lambda item: str(item[0])):
        payload = _as_map(row)
        extensions = _as_map(payload.get("extensions"))
        descriptor = build_product_build_descriptor(
            product_id=str(payload.get("product_id", product_id)).strip() or str(product_id).strip(),
            build_id=str(payload.get("build_id", "")).strip(),
            binary_hash=str(payload.get("binary_hash", "")).strip(),
            endpoint_descriptor_hash=str(payload.get("endpoint_descriptor_hash", "")).strip(),
            binary_ref=str(payload.get("binary_ref", "")).strip() or str(extensions.get("official.binary_ref", "")).strip(),
            descriptor_ref=str(payload.get("descriptor_ref", "")).strip() or str(extensions.get("official.descriptor_ref", "")).strip(),
            product_version=str(payload.get("product_version", "")).strip(),
        )
        if descriptor["build_id"] or descriptor["binary_hash"] or descriptor["endpoint_descriptor_hash"]:
            out[str(descriptor.get("product_id", product_id)).strip()] = descriptor
    return dict((key, out[key]) for key in sorted(out.keys()))


def normalize_install_manifest(payload: Mapping[str, object]) -> dict:
    manifest = _normalize_value(normalize_extensions_tree(dict(payload or {})))
    product_builds = {
        str(key): str(value).strip()
        for key, value in sorted(_as_map(manifest.get("product_builds") or manifest.get("product_build_ids")).items(), key=lambda item: str(item[0]))
        if str(key).strip() and str(value).strip()
    }
    protocol_ranges = merge_protocol_ranges(_as_map(manifest.get("supported_protocol_versions")).values())
    contract_ranges = merge_contract_ranges(_as_map(manifest.get("supported_contract_ranges")).values())
    store_root_ref = _as_map(manifest.get("store_root_ref"))
    normalized = dict(manifest)
    normalized["install_id"] = str(manifest.get("install_id", "")).strip()
    normalized["install_version"] = str(manifest.get("install_version", "0.0.0")).strip() or "0.0.0"
    normalized["product_builds"] = product_builds
    normalized["semantic_contract_registry_hash"] = str(manifest.get("semantic_contract_registry_hash", "")).strip()
    normalized["supported_protocol_versions"] = dict((key, protocol_ranges[key]) for key in sorted(protocol_ranges.keys()))
    normalized["supported_contract_ranges"] = dict((key, contract_ranges[key]) for key in sorted(contract_ranges.keys()))
    normalized["default_mod_policy_id"] = str(manifest.get("default_mod_policy_id", "mod.policy.default")).strip() or "mod.policy.default"
    normalized["store_root_ref"] = {
        "store_id": str(store_root_ref.get("store_id", "")).strip(),
        "root_path": _norm(store_root_ref.get("root_path", "")),
        "manifest_ref": _norm(store_root_ref.get("manifest_ref", "")),
    }
    normalized["mode"] = str(manifest.get("mode", "portable")).strip() or "portable"
    normalized["extensions"] = normalize_extensions_map(_as_map(manifest.get("extensions")))
    normalized["product_build_descriptors"] = collect_manifest_product_descriptors(normalized)
    normalized["deterministic_fingerprint"] = str(manifest.get("deterministic_fingerprint", "")).strip()
    return normalized


def _manifest_required_fields(manifest: Mapping[str, object]) -> List[str]:
    required = [
        "install_id",
        "install_version",
        "product_builds",
        "semantic_contract_registry_hash",
        "supported_protocol_versions",
        "supported_contract_ranges",
        "default_mod_policy_id",
        "store_root_ref",
        "mode",
        "deterministic_fingerprint",
        "extensions",
    ]
    missing = []
    for field in required:
        value = manifest.get(field)
        if isinstance(value, str) and value.strip():
            continue
        if isinstance(value, dict):
            if field in {"product_builds", "supported_protocol_versions", "supported_contract_ranges", "store_root_ref", "extensions"}:
                continue
            if value:
                continue
        missing.append(field)
    return missing


def _registry_path_from_manifest(install_root: str, manifest: Mapping[str, object]) -> str:
    extensions = _as_map(manifest.get("extensions"))
    ref = str(extensions.get("official.semantic_contract_registry_ref", "")).strip()
    if ref:
        return os.path.join(install_root, ref.replace("/", os.sep))
    return os.path.join(install_root, "semantic_contract_registry.json")


def _run_descriptor_command(command: str, cwd: str) -> Tuple[dict, str]:
    try:
        proc = subprocess.run(
            [item for item in str(command or "").split(" ") if item] + ["--descriptor"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError:
        return {}, "invoke_failed"
    if int(proc.returncode or 0) != 0:
        return {}, "invoke_failed"
    stdout = str(proc.stdout or "").strip()
    if not stdout:
        return {}, "empty_descriptor"
    try:
        payload = json.loads(stdout)
    except ValueError:
        return {}, "invalid_descriptor"
    descriptor = _as_map(payload.get("descriptor")) if isinstance(payload, dict) else {}
    if descriptor:
        return descriptor, ""
    if isinstance(payload, dict) and payload.get("product_id"):
        return payload, ""
    return {}, "invalid_descriptor"


def compare_required_product_builds(
    install_manifest: Mapping[str, object],
    required_product_builds: Mapping[str, object] | None,
) -> List[dict]:
    actual = {
        str(key): str(value).strip()
        for key, value in sorted(_as_map(install_manifest.get("product_builds")).items(), key=lambda item: str(item[0]))
    }
    required = {
        str(key): str(value).strip()
        for key, value in sorted(_as_map(required_product_builds).items(), key=lambda item: str(item[0]))
        if str(key).strip() and str(value).strip()
    }
    mismatches = []
    for product_id, expected_build_id in sorted(required.items()):
        actual_build_id = actual.get(product_id, "")
        if actual_build_id == expected_build_id:
            continue
        mismatches.append(
            {
                "product_id": product_id,
                "required_build_id": expected_build_id,
                "actual_build_id": actual_build_id,
                "present": bool(actual_build_id),
            }
        )
    return mismatches


def compare_required_contract_ranges(
    install_manifest: Mapping[str, object],
    required_contract_ranges: Mapping[str, object] | None,
) -> List[dict]:
    supported = {
        str(key): normalize_contract_range(value)
        for key, value in sorted(_as_map(install_manifest.get("supported_contract_ranges")).items(), key=lambda item: str(item[0]))
    }
    required = {
        str(key): normalize_contract_range(value)
        for key, value in sorted(_as_map(required_contract_ranges).items(), key=lambda item: str(item[0]))
        if str(key).strip()
    }
    mismatches = []
    for contract_id, expected in sorted(required.items()):
        current = dict(supported.get(contract_id) or {})
        if not current:
            mismatches.append(
                {
                    "contract_category_id": contract_id,
                    "reason": "missing",
                    "required_range": expected,
                    "supported_range": {},
                }
            )
            continue
        if int(current.get("min_version", 1) or 1) > int(expected.get("min_version", 1) or 1):
            mismatches.append(
                {
                    "contract_category_id": contract_id,
                    "reason": "min_version",
                    "required_range": expected,
                    "supported_range": current,
                }
            )
            continue
        if int(current.get("max_version", 1) or 1) < int(expected.get("max_version", 1) or 1):
            mismatches.append(
                {
                    "contract_category_id": contract_id,
                    "reason": "max_version",
                    "required_range": expected,
                    "supported_range": current,
                }
            )
    return mismatches


def validate_install_manifest(
    *,
    repo_root: str,
    install_manifest_path: str,
    manifest_payload: Mapping[str, object] | None = None,
) -> Dict[str, object]:
    del repo_root
    manifest_path = os.path.abspath(str(install_manifest_path or "").strip())
    install_root = os.path.dirname(manifest_path)
    manifest, error = (_read_json(manifest_path) if manifest_payload is None else (_normalize_value(normalize_extensions_tree(dict(manifest_payload or {}))), ""))
    if error:
        return {
            "result": "refused",
            "refusal_code": REFUSAL_INSTALL_HASH_MISMATCH,
            "errors": [{"code": "install_manifest_invalid", "path": "$", "message": "unable to load install manifest"}],
            "warnings": [],
            "install_manifest": {},
        }

    normalized = normalize_install_manifest(manifest)
    errors: List[dict] = []
    warnings: List[dict] = []

    for field in _manifest_required_fields(normalized):
        errors.append({"code": "install_manifest_missing_field", "path": "$.{}".format(field), "message": "missing required field '{}'".format(field)})

    if str(normalized.get("mode", "")).strip() not in {"linked", "portable"}:
        errors.append({"code": "install_manifest_invalid_mode", "path": "$.mode", "message": "mode must be 'linked' or 'portable'"})

    store_root_ref = _as_map(normalized.get("store_root_ref"))
    for field in ("root_path", "manifest_ref"):
        token = str(store_root_ref.get(field, "")).strip()
        if token and os.path.isabs(token):
            errors.append({"code": "install_manifest_absolute_path", "path": "$.store_root_ref.{}".format(field), "message": "install manifest must not require absolute path refs"})

    expected_fingerprint = deterministic_fingerprint(normalized)
    if str(normalized.get("deterministic_fingerprint", "")).strip() != expected_fingerprint:
        errors.append({"code": "install_manifest_fingerprint_mismatch", "path": "$.deterministic_fingerprint", "message": "deterministic_fingerprint mismatch"})

    descriptors = collect_manifest_product_descriptors(normalized)
    for product_id, build_id in sorted(_as_map(normalized.get("product_builds")).items(), key=lambda item: str(item[0])):
        descriptor = dict(descriptors.get(str(product_id)) or {})
        if not descriptor:
            errors.append({"code": "product_build_descriptor_missing", "path": "$.product_build_descriptors.{}".format(product_id), "message": "missing product build descriptor for '{}'".format(product_id)})
            continue
        if str(descriptor.get("build_id", "")).strip() != str(build_id).strip():
            errors.append({"code": "product_build_descriptor_mismatch", "path": "$.product_build_descriptors.{}.build_id".format(product_id), "message": "build_id mismatch for '{}'".format(product_id)})
            continue

        descriptor_extensions = _as_map(descriptor.get("extensions"))
        binary_ref = str(descriptor_extensions.get("official.binary_ref", "")).strip()
        descriptor_ref = str(descriptor_extensions.get("official.descriptor_ref", "")).strip()
        descriptor_command = str(descriptor_extensions.get("official.descriptor_command", "")).strip()
        binary_path = os.path.join(install_root, binary_ref.replace("/", os.sep)) if binary_ref else ""
        descriptor_path = os.path.join(install_root, descriptor_ref.replace("/", os.sep)) if descriptor_ref else ""

        if not binary_path or not os.path.isfile(binary_path):
            errors.append({"code": REFUSAL_INSTALL_MISSING_BINARY, "path": "$.product_build_descriptors.{}.extensions.official.binary_ref".format(product_id), "message": "binary missing for '{}'".format(product_id)})
            continue
        if sha256_file(binary_path) != str(descriptor.get("binary_hash", "")).strip():
            errors.append({"code": REFUSAL_INSTALL_HASH_MISMATCH, "path": "$.product_build_descriptors.{}.binary_hash".format(product_id), "message": "binary_hash mismatch for '{}'".format(product_id)})

        emitted_descriptor = {}
        if descriptor_command:
            emitted_descriptor, emit_error = _run_descriptor_command(descriptor_command, install_root)
            if emit_error:
                warnings.append({"code": "descriptor_command_unavailable", "path": "$.product_build_descriptors.{}.extensions.official.descriptor_command".format(product_id), "message": "descriptor command unavailable for '{}'".format(product_id)})
                emitted_descriptor = {}
        if emitted_descriptor:
            actual_descriptor_hash = canonical_sha256(emitted_descriptor)
            if actual_descriptor_hash != str(descriptor.get("endpoint_descriptor_hash", "")).strip():
                errors.append({"code": REFUSAL_INSTALL_HASH_MISMATCH, "path": "$.product_build_descriptors.{}.endpoint_descriptor_hash".format(product_id), "message": "emitted descriptor hash mismatch for '{}'".format(product_id)})
        elif descriptor_path and os.path.isfile(descriptor_path):
            descriptor_payload, descriptor_error = _read_json(descriptor_path)
            if descriptor_error:
                errors.append({"code": REFUSAL_INSTALL_HASH_MISMATCH, "path": "$.product_build_descriptors.{}.extensions.official.descriptor_ref".format(product_id), "message": "descriptor file invalid for '{}'".format(product_id)})
            elif canonical_sha256(descriptor_payload) != str(descriptor.get("endpoint_descriptor_hash", "")).strip():
                errors.append({"code": REFUSAL_INSTALL_HASH_MISMATCH, "path": "$.product_build_descriptors.{}.endpoint_descriptor_hash".format(product_id), "message": "descriptor hash mismatch for '{}'".format(product_id)})
        else:
            errors.append({"code": REFUSAL_INSTALL_HASH_MISMATCH, "path": "$.product_build_descriptors.{}.extensions.official.descriptor_ref".format(product_id), "message": "descriptor missing for '{}'".format(product_id)})

    contract_registry_path = _registry_path_from_manifest(install_root, normalized)
    expected_contract_hash = str(normalized.get("semantic_contract_registry_hash", "")).strip()
    if not os.path.isfile(contract_registry_path):
        errors.append({"code": REFUSAL_INSTALL_CONTRACT_REGISTRY_MISMATCH, "path": "$.extensions.official.semantic_contract_registry_ref", "message": "bundled semantic contract registry missing"})
    else:
        registry_payload, registry_error = _read_json(contract_registry_path)
        if registry_error:
            errors.append({"code": REFUSAL_INSTALL_CONTRACT_REGISTRY_MISMATCH, "path": "$.extensions.official.semantic_contract_registry_ref", "message": "bundled semantic contract registry invalid"})
        elif canonical_sha256(registry_payload) != expected_contract_hash:
            errors.append({"code": REFUSAL_INSTALL_CONTRACT_REGISTRY_MISMATCH, "path": "$.semantic_contract_registry_hash", "message": "semantic contract registry hash mismatch"})

    result = "complete" if not errors else "refused"
    refusal_code = str(errors[0].get("code", "")).strip() if errors else ""
    return {
        "result": result,
        "refusal_code": refusal_code,
        "errors": sorted(errors, key=lambda row: (str(row.get("path", "")), str(row.get("code", "")), str(row.get("message", "")))),
        "warnings": sorted(warnings, key=lambda row: (str(row.get("path", "")), str(row.get("code", "")), str(row.get("message", "")))),
        "install_manifest": normalized,
    }


def default_install_registry_path(repo_root: str) -> str:
    context = get_current_virtual_paths()
    if context is not None and str(context.get("result", "")).strip() == "complete":
        candidate = vpath_resolve_existing(VROOT_INSTALL, "data/registries/install_registry.json", context)
        if candidate:
            return candidate
    return os.path.join(os.path.abspath(repo_root), DEFAULT_INSTALL_REGISTRY_REL)


def _empty_install_registry() -> dict:
    return {
        "schema_id": "dominium.registry.install_registry",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.install_registry",
            "registry_version": "1.0.0",
            "installs": [],
        },
    }


def load_install_registry(path: str) -> dict:
    registry_path = os.path.abspath(str(path or "").strip())
    if not os.path.isfile(registry_path):
        return _empty_install_registry()
    payload, error = _read_json(registry_path)
    if error:
        return _empty_install_registry()
    record = _as_map(payload.get("record"))
    installs = []
    for row in _as_list(record.get("installs")):
        entry = _as_map(row)
        installs.append(
            {
                "install_id": str(entry.get("install_id", "")).strip(),
                "path": _norm(entry.get("path", "")),
                "version": str(entry.get("version", "")).strip(),
                "semantic_contract_registry_hash": str(entry.get("semantic_contract_registry_hash", "")).strip(),
            }
        )
    payload["record"] = {
        "registry_id": str(record.get("registry_id", "dominium.registry.install_registry")).strip() or "dominium.registry.install_registry",
        "registry_version": str(record.get("registry_version", "1.0.0")).strip() or "1.0.0",
        "installs": sorted(installs, key=lambda row: (row["install_id"], row["path"])),
    }
    return payload


def save_install_registry(path: str, payload: Mapping[str, object]) -> str:
    registry = load_install_registry(path)
    record = _as_map(dict(payload or {}).get("record")) if isinstance(payload, Mapping) else {}
    if record:
        installs = []
        for row in _as_list(record.get("installs")):
            entry = _as_map(row)
            installs.append(
                {
                    "install_id": str(entry.get("install_id", "")).strip(),
                    "path": _norm(entry.get("path", "")),
                    "version": str(entry.get("version", "")).strip(),
                    "semantic_contract_registry_hash": str(entry.get("semantic_contract_registry_hash", "")).strip(),
                }
            )
        registry["record"]["installs"] = sorted(installs, key=lambda row: (row["install_id"], row["path"]))
    return write_json(path, registry)


def build_install_registry_entry(
    *,
    registry_path: str,
    install_manifest_path: str,
    install_manifest: Mapping[str, object],
) -> dict:
    path_token = _stable_relpath(os.path.dirname(os.path.abspath(registry_path)), os.path.dirname(os.path.abspath(install_manifest_path)))
    if not path_token:
        path_token = _norm(os.path.abspath(os.path.dirname(os.path.abspath(install_manifest_path))))
    return {
        "install_id": str(install_manifest.get("install_id", "")).strip(),
        "path": path_token,
        "version": str(install_manifest.get("install_version", "")).strip(),
        "semantic_contract_registry_hash": str(install_manifest.get("semantic_contract_registry_hash", "")).strip(),
    }


def registry_add_install(
    *,
    repo_root: str,
    registry_path: str,
    install_manifest_path: str,
) -> Dict[str, object]:
    validation = validate_install_manifest(repo_root=repo_root, install_manifest_path=install_manifest_path)
    if validation.get("result") != "complete":
        return validation
    registry = load_install_registry(registry_path)
    entry = build_install_registry_entry(
        registry_path=registry_path,
        install_manifest_path=install_manifest_path,
        install_manifest=validation.get("install_manifest") or {},
    )
    installs = list(_as_map(registry.get("record")).get("installs") or [])
    for row in installs:
        current = _as_map(row)
        if str(current.get("install_id", "")).strip() == entry["install_id"]:
            if _norm(current.get("path", "")) == entry["path"]:
                save_install_registry(registry_path, registry)
                return {
                    "result": "complete",
                    "install_manifest": validation.get("install_manifest") or {},
                    "registry_entry": entry,
                    "registry_path": _norm(registry_path),
                    "created": False,
                }
            return {
                "result": "refused",
                "refusal_code": "refusal.install.id_collision",
                "errors": [{"code": "install_id_collision", "path": "$.record.installs", "message": "install_id already registered at a different path"}],
                "warnings": [],
                "install_manifest": validation.get("install_manifest") or {},
            }
    installs.append(entry)
    registry["record"]["installs"] = sorted(
        [_as_map(item) for item in installs],
        key=lambda row: (str(row.get("install_id", "")), str(row.get("path", ""))),
    )
    save_install_registry(registry_path, registry)
    return {
        "result": "complete",
        "install_manifest": validation.get("install_manifest") or {},
        "registry_entry": entry,
        "registry_path": _norm(registry_path),
        "created": True,
    }


def registry_remove_install(*, registry_path: str, install_id: str) -> Dict[str, object]:
    registry = load_install_registry(registry_path)
    installs = list(_as_map(registry.get("record")).get("installs") or [])
    kept = [row for row in installs if str(_as_map(row).get("install_id", "")).strip() != str(install_id or "").strip()]
    registry["record"]["installs"] = sorted(
        [_as_map(item) for item in kept],
        key=lambda row: (str(row.get("install_id", "")), str(row.get("path", ""))),
    )
    save_install_registry(registry_path, registry)
    return {
        "result": "complete",
        "removed": len(kept) != len(installs),
        "registry_path": _norm(registry_path),
        "install_id": str(install_id or "").strip(),
    }


def verify_install_registry(*, repo_root: str, registry_path: str) -> Dict[str, object]:
    registry = load_install_registry(registry_path)
    registry_root = os.path.dirname(os.path.abspath(registry_path))
    installs = []
    overall = "complete"
    for row in list(_as_map(registry.get("record")).get("installs") or []):
        entry = _as_map(row)
        path_token = str(entry.get("path", "")).strip()
        install_root = os.path.abspath(path_token if os.path.isabs(path_token) else os.path.join(registry_root, path_token))
        manifest_path = os.path.join(install_root, "install.manifest.json")
        validation = validate_install_manifest(repo_root=repo_root, install_manifest_path=manifest_path)
        if validation.get("result") != "complete":
            overall = "refused"
        installs.append(
            {
                "install_id": str(entry.get("install_id", "")).strip(),
                "path": _norm(path_token),
                "result": str(validation.get("result", "refused")).strip() or "refused",
                "refusal_code": str(validation.get("refusal_code", "")).strip(),
                "errors": list(validation.get("errors") or []),
                "warnings": list(validation.get("warnings") or []),
            }
        )
    return {
        "result": overall,
        "registry_path": _norm(registry_path),
        "installs": sorted(installs, key=lambda row: (row["install_id"], row["path"])),
    }


__all__ = [
    "DEFAULT_INSTALL_REGISTRY_REL",
    "REFUSAL_INSTALL_CONTRACT_REGISTRY_MISMATCH",
    "REFUSAL_INSTALL_HASH_MISMATCH",
    "REFUSAL_INSTALL_MISSING_BINARY",
    "build_install_registry_entry",
    "build_product_build_descriptor",
    "collect_manifest_product_descriptors",
    "compare_required_contract_ranges",
    "compare_required_product_builds",
    "default_install_registry_path",
    "deterministic_fingerprint",
    "load_install_registry",
    "merge_contract_ranges",
    "merge_protocol_ranges",
    "normalize_contract_range",
    "normalize_install_manifest",
    "normalize_protocol_range",
    "registry_add_install",
    "registry_remove_install",
    "save_install_registry",
    "sha256_file",
    "stable_install_id",
    "validate_install_manifest",
    "verify_install_registry",
    "write_json",
]
