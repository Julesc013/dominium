"""Deterministic CAP-NEG-1 endpoint descriptor emission engine."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Dict, Iterable, List, Mapping, Tuple

from src.compat.capability_negotiation import (
    build_endpoint_descriptor,
    load_product_registry,
    product_default_degrade_ladders,
    semantic_contract_rows_by_category,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


PRODUCT_CAPABILITY_DEFAULTS_REL = os.path.join("data", "registries", "product_capability_defaults.json")
SEMANTIC_CONTRACT_REGISTRY_REL = os.path.join("data", "registries", "semantic_contract_registry.json")
DEFAULT_PRODUCT_SEMVER = "0.0.0"
DEFAULT_BUILD_NUMBER = "0"


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, path.replace("\\", "/")
    if not isinstance(payload, dict):
        return {}, path.replace("\\", "/")
    return dict(payload), ""


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def load_product_capability_defaults(repo_root: str) -> Tuple[dict, str]:
    return _read_json(os.path.join(repo_root, PRODUCT_CAPABILITY_DEFAULTS_REL))


def product_capability_default_rows_by_id(repo_root: str) -> Tuple[Dict[str, dict], str]:
    payload, error = load_product_capability_defaults(repo_root)
    if error:
        return {}, error
    rows = _as_list(_as_map(payload.get("record")).get("defaults"))
    out: Dict[str, dict] = {}
    for row in rows:
        row_map = _as_map(row)
        product_id = str(row_map.get("product_id", "")).strip()
        if product_id:
            out[product_id] = row_map
    return dict((key, out[key]) for key in sorted(out.keys())), ""


def _product_rows_by_id(repo_root: str) -> Tuple[Dict[str, dict], str]:
    payload, error = load_product_registry(repo_root)
    if error:
        return {}, error
    rows = _as_list(_as_map(payload.get("record")).get("products"))
    out: Dict[str, dict] = {}
    for row in rows:
        row_map = _as_map(row)
        product_id = str(row_map.get("product_id", "")).strip()
        if product_id:
            out[product_id] = row_map
    return dict((key, out[key]) for key in sorted(out.keys())), ""


def _semantic_contract_ranges(repo_root: str) -> List[dict]:
    rows_by_category, _error = semantic_contract_rows_by_category(repo_root)
    out = []
    for category_id in sorted(rows_by_category.keys()):
        row = dict(rows_by_category.get(category_id) or {})
        version = int(row.get("version", 1) or 1)
        out.append(
            {
                "schema_version": "1.0.0",
                "contract_category_id": str(category_id),
                "min_version": version,
                "max_version": version,
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        )
    return out


def _semantic_contract_registry_hash(repo_root: str) -> str:
    payload, error = _read_json(os.path.join(repo_root, SEMANTIC_CONTRACT_REGISTRY_REL))
    if error:
        return ""
    return canonical_sha256(payload)


def _git_commit_hash(repo_root: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", repo_root, "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError:
        return ""
    if int(result.returncode or 0) != 0:
        return ""
    return str(result.stdout or "").strip()


def _compilation_options_payload(product_id: str, defaults_row: Mapping[str, object]) -> dict:
    return {
        "descriptor_schema_version": "1.0.0",
        "product_id": str(product_id or "").strip(),
        "runtime_family": "python.portable",
        "protocol_ids": _sorted_tokens(
            _as_map(row).get("protocol_id", "")
            for row in _as_list(_as_map(defaults_row).get("protocol_versions_supported"))
            if isinstance(row, Mapping)
        ),
        "feature_capabilities": _sorted_tokens(_as_map(defaults_row).get("feature_capabilities")),
        "source": str(_as_map(defaults_row).get("extensions", {}).get("official.source", "CAP-NEG-1")).strip() or "CAP-NEG-1",
    }


def build_product_build_metadata(repo_root: str, product_id: str) -> dict:
    defaults_rows, _error = product_capability_default_rows_by_id(repo_root)
    defaults_row = dict(defaults_rows.get(str(product_id).strip()) or {})
    contract_hash = _semantic_contract_registry_hash(repo_root)
    git_hash = _git_commit_hash(repo_root)
    fallback_build_number = str(os.environ.get("DOMINIUM_FIXED_BUILD_NUMBER", DEFAULT_BUILD_NUMBER)).strip() or DEFAULT_BUILD_NUMBER
    compilation_options = _compilation_options_payload(str(product_id), defaults_row)
    compilation_options_hash = canonical_sha256(compilation_options)
    build_seed = {
        "product_id": str(product_id).strip(),
        "git_commit_hash": str(git_hash).strip(),
        "fallback_build_number": fallback_build_number,
        "semantic_contract_registry_hash": contract_hash,
        "compilation_options_hash": compilation_options_hash,
    }
    build_id = "build.{}".format(canonical_sha256(build_seed)[:16])
    return {
        "product_id": str(product_id).strip(),
        "build_id": build_id,
        "git_commit_hash": str(git_hash).strip(),
        "semantic_contract_registry_hash": contract_hash,
        "compilation_options_hash": compilation_options_hash,
        "fallback_build_number": fallback_build_number,
        "deterministic_fingerprint": canonical_sha256(
            {
                "product_id": str(product_id).strip(),
                "build_id": build_id,
                "git_commit_hash": str(git_hash).strip(),
                "semantic_contract_registry_hash": contract_hash,
                "compilation_options_hash": compilation_options_hash,
                "fallback_build_number": fallback_build_number,
            }
        ),
    }


def _default_semver(product_row: Mapping[str, object]) -> str:
    extensions = _as_map(_as_map(product_row).get("extensions"))
    token = str(extensions.get("official.default_semver", DEFAULT_PRODUCT_SEMVER)).strip()
    return token or DEFAULT_PRODUCT_SEMVER


def product_descriptor_bin_names(repo_root: str) -> List[str]:
    rows_by_id, _error = _product_rows_by_id(repo_root)
    out: List[str] = []
    for product_id in sorted(rows_by_id.keys()):
        row = dict(rows_by_id.get(product_id) or {})
        names = _as_map(row.get("extensions")).get("official.dist_bin_names", [])
        for item in _sorted_tokens(names):
            out.append(item)
    return sorted(set(out))


def build_product_descriptor(repo_root: str, *, product_id: str, product_version: str = "") -> dict:
    product_rows, error = _product_rows_by_id(repo_root)
    if error:
        raise ValueError("product registry missing: {}".format(error))
    defaults_rows, defaults_error = product_capability_default_rows_by_id(repo_root)
    if defaults_error:
        raise ValueError("product capability defaults missing: {}".format(defaults_error))
    product_row = dict(product_rows.get(str(product_id).strip()) or {})
    defaults_row = dict(defaults_rows.get(str(product_id).strip()) or {})
    if not product_row:
        raise ValueError("unknown product_id '{}'".format(str(product_id).strip()))
    if not defaults_row:
        raise ValueError("missing capability defaults for product_id '{}'".format(str(product_id).strip()))

    build_meta = build_product_build_metadata(repo_root, str(product_id).strip())
    resolved_version = str(product_version or "").strip()
    if not resolved_version:
        resolved_version = "{}+{}".format(_default_semver(product_row), str(build_meta.get("build_id", "")).strip())

    product_extensions = _as_map(product_row.get("extensions"))
    defaults_extensions = _as_map(defaults_row.get("extensions"))
    descriptor_extensions = dict(product_extensions)
    descriptor_extensions.update(defaults_extensions)
    descriptor_extensions.update(
        {
            "official.build_id": str(build_meta.get("build_id", "")).strip(),
            "official.git_commit_hash": str(build_meta.get("git_commit_hash", "")).strip(),
            "official.semantic_contract_registry_hash": str(build_meta.get("semantic_contract_registry_hash", "")).strip(),
            "official.compilation_options_hash": str(build_meta.get("compilation_options_hash", "")).strip(),
            "official.product_capability_defaults_hash": canonical_sha256(defaults_row),
            "official.product_registry_row_hash": canonical_sha256(product_row),
        }
    )

    contract_ranges = list(_as_list(defaults_row.get("semantic_contract_versions_supported")))
    if not contract_ranges:
        contract_ranges = _semantic_contract_ranges(repo_root)

    return build_endpoint_descriptor(
        product_id=str(product_id).strip(),
        product_version=resolved_version,
        protocol_versions_supported=_as_list(defaults_row.get("protocol_versions_supported")),
        semantic_contract_versions_supported=contract_ranges,
        feature_capabilities=_as_list(defaults_row.get("feature_capabilities")),
        required_capabilities=_as_list(defaults_row.get("required_capabilities")),
        optional_capabilities=_as_list(defaults_row.get("optional_capabilities")),
        degrade_ladders=product_default_degrade_ladders(repo_root, str(product_id).strip()) or _as_list(defaults_row.get("degrade_ladders")),
        extensions=descriptor_extensions,
    )


def descriptor_json_text(descriptor: Mapping[str, object]) -> str:
    return canonical_json_text(dict(descriptor or {}))


def write_descriptor_file(path: str, descriptor: Mapping[str, object]) -> str:
    output_path = os.path.normpath(os.path.abspath(str(path or "").strip()))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(descriptor_json_text(descriptor))
        handle.write("\n")
    return output_path


def emit_product_descriptor(repo_root: str, *, product_id: str, descriptor_file: str = "", product_version: str = "") -> dict:
    descriptor = build_product_descriptor(repo_root, product_id=str(product_id).strip(), product_version=str(product_version).strip())
    output_path = ""
    if str(descriptor_file or "").strip():
        output_path = write_descriptor_file(str(descriptor_file), descriptor)
    return {
        "result": "complete",
        "product_id": str(product_id).strip(),
        "descriptor": descriptor,
        "descriptor_hash": canonical_sha256(descriptor),
        "descriptor_file": output_path.replace("\\", "/") if output_path else "",
    }


__all__ = [
    "PRODUCT_CAPABILITY_DEFAULTS_REL",
    "build_product_build_metadata",
    "build_product_descriptor",
    "descriptor_json_text",
    "emit_product_descriptor",
    "load_product_capability_defaults",
    "product_capability_default_rows_by_id",
    "product_descriptor_bin_names",
    "write_descriptor_file",
]
