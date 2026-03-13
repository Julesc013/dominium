"""Deterministic release build identity helpers."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Dict, Iterable, List, Mapping, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


PRODUCT_CAPABILITY_DEFAULTS_REL = os.path.join("data", "registries", "product_capability_defaults.json")
SEMANTIC_CONTRACT_REGISTRY_REL = os.path.join("data", "registries", "semantic_contract_registry.json")
DEFAULT_PRODUCT_SEMVER = "0.0.0"
DEFAULT_BUILD_NUMBER = "0"
DEFAULT_BUILD_CONFIGURATION = "release"


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


def semantic_contract_registry_hash(repo_root: str) -> str:
    payload, error = _read_json(os.path.join(repo_root, SEMANTIC_CONTRACT_REGISTRY_REL))
    if error:
        return ""
    return canonical_sha256(payload)


def source_revision_id(repo_root: str) -> str:
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


def build_compilation_options_payload(
    product_id: str,
    defaults_row: Mapping[str, object] | None,
    *,
    compilation_options_override: Mapping[str, object] | None = None,
    build_configuration: str = DEFAULT_BUILD_CONFIGURATION,
) -> dict:
    if isinstance(compilation_options_override, Mapping):
        payload = dict(compilation_options_override)
        payload.setdefault("product_id", str(product_id or "").strip())
        payload.setdefault("descriptor_schema_version", "1.0.0")
        payload.setdefault("build_configuration", str(build_configuration or "").strip() or DEFAULT_BUILD_CONFIGURATION)
        return payload
    row = _as_map(defaults_row)
    return {
        "descriptor_schema_version": "1.0.0",
        "product_id": str(product_id or "").strip(),
        "runtime_family": "python.portable",
        "build_configuration": str(build_configuration or "").strip() or DEFAULT_BUILD_CONFIGURATION,
        "protocol_ids": _sorted_tokens(
            _as_map(item).get("protocol_id", "")
            for item in _as_list(row.get("protocol_versions_supported"))
            if isinstance(item, Mapping)
        ),
        "feature_capabilities": _sorted_tokens(row.get("feature_capabilities")),
        "source": str(_as_map(row.get("extensions")).get("official.source", "RELEASE0")).strip() or "RELEASE0",
    }


def build_build_id_input_payload(
    *,
    product_id: str,
    semantic_contract_registry_hash: str,
    compilation_options_hash: str,
    source_revision_id_value: str = "",
    explicit_build_number: str = "",
    platform_tag: str = "",
) -> dict:
    resolved_source_revision = str(source_revision_id_value or "").strip()
    resolved_build_number = "" if resolved_source_revision else (str(explicit_build_number or "").strip() or DEFAULT_BUILD_NUMBER)
    return {
        "product_id": str(product_id or "").strip(),
        "semantic_contract_registry_hash": str(semantic_contract_registry_hash or "").strip().lower(),
        "compilation_options_hash": str(compilation_options_hash or "").strip().lower(),
        "source_revision_id": resolved_source_revision,
        "explicit_build_number": resolved_build_number,
        "platform_tag": str(platform_tag or "").strip(),
    }


def build_id_identity_from_input_payload(input_payload: Mapping[str, object]) -> dict:
    normalized_payload = build_build_id_input_payload(
        product_id=str(input_payload.get("product_id", "")).strip(),
        semantic_contract_registry_hash=str(input_payload.get("semantic_contract_registry_hash", "")).strip(),
        compilation_options_hash=str(input_payload.get("compilation_options_hash", "")).strip(),
        source_revision_id_value=str(input_payload.get("source_revision_id", "")).strip(),
        explicit_build_number=str(input_payload.get("explicit_build_number", "")).strip(),
        platform_tag=str(input_payload.get("platform_tag", "")).strip(),
    )
    inputs_hash = canonical_sha256(normalized_payload)
    return {
        "inputs_hash": inputs_hash,
        "build_id": "build.{}".format(inputs_hash[:16]),
        "input_payload": normalized_payload,
    }


def build_product_build_metadata(
    repo_root: str,
    product_id: str,
    *,
    compilation_options_override: Mapping[str, object] | None = None,
    source_revision_id_override: str = "",
    explicit_build_number: str = "",
    platform_tag: str = "",
    build_configuration: str = DEFAULT_BUILD_CONFIGURATION,
) -> dict:
    defaults_rows, _error = product_capability_default_rows_by_id(repo_root)
    defaults_row = dict(defaults_rows.get(str(product_id).strip()) or {})
    contract_hash = semantic_contract_registry_hash(repo_root)
    resolved_source_revision = str(source_revision_id_override or "").strip() or source_revision_id(repo_root)
    resolved_build_number = (
        ""
        if resolved_source_revision
        else str(explicit_build_number or os.environ.get("DOMINIUM_FIXED_BUILD_NUMBER", DEFAULT_BUILD_NUMBER)).strip()
        or DEFAULT_BUILD_NUMBER
    )
    compilation_options = build_compilation_options_payload(
        str(product_id).strip(),
        defaults_row,
        compilation_options_override=compilation_options_override,
        build_configuration=build_configuration,
    )
    compilation_options_hash = canonical_sha256(compilation_options)
    build_identity = build_id_identity_from_input_payload(
        build_build_id_input_payload(
            product_id=str(product_id).strip(),
            semantic_contract_registry_hash=contract_hash,
            compilation_options_hash=compilation_options_hash,
            source_revision_id_value=resolved_source_revision,
            explicit_build_number=resolved_build_number,
            platform_tag=str(platform_tag or "").strip(),
        )
    )
    inputs_hash = str(build_identity.get("inputs_hash", "")).strip()
    build_id = str(build_identity.get("build_id", "")).strip()
    payload = {
        "schema_version": "1.0.0",
        "product_id": str(product_id).strip(),
        "build_id": build_id,
        "inputs_hash": inputs_hash,
        "semantic_contract_registry_hash": contract_hash,
        "compilation_options_hash": compilation_options_hash,
        "source_revision_id": resolved_source_revision,
        "explicit_build_number": resolved_build_number,
        "platform_tag": str(platform_tag or "").strip(),
        "build_configuration": str(compilation_options.get("build_configuration", "")).strip() or DEFAULT_BUILD_CONFIGURATION,
        "git_commit_hash": resolved_source_revision,
        "fallback_build_number": resolved_build_number,
        "deterministic_fingerprint": "",
        "extensions": {
            "official.build_input_selection": "source_revision_id" if resolved_source_revision else "explicit_build_number",
            "official.compilation_options": compilation_options,
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "DEFAULT_BUILD_NUMBER",
    "DEFAULT_BUILD_CONFIGURATION",
    "DEFAULT_PRODUCT_SEMVER",
    "PRODUCT_CAPABILITY_DEFAULTS_REL",
    "SEMANTIC_CONTRACT_REGISTRY_REL",
    "build_build_id_input_payload",
    "build_compilation_options_payload",
    "build_id_identity_from_input_payload",
    "build_product_build_metadata",
    "load_product_capability_defaults",
    "product_capability_default_rows_by_id",
    "semantic_contract_registry_hash",
    "source_revision_id",
]
