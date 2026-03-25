"""Deterministic license-capability trust helpers."""

from __future__ import annotations

from typing import Mapping, Sequence

from src.meta.identity import (
    UNIVERSAL_IDENTITY_FIELD,
    build_universal_identity_block,
    canonicalize_universal_identity_block,
    validate_identity_block,
)
from tools.xstack.compatx.canonical_json import canonical_sha256

from .trust_verifier import (
    ARTIFACT_KIND_LICENSE_CAPABILITY,
    TRUST_POLICY_STRICT,
    canonicalize_signature_record,
    deterministic_fingerprint,
    load_trust_policy_registry,
    select_trust_policy,
    verify_artifact_trust,
)


LICENSE_CAPABILITY_SCHEMA_ID = "dominium.schema.security.license_capability_artifact"
LICENSE_CAPABILITY_SCHEMA_VERSION = "1.0.0"
LICENSE_CAPABILITY_IDENTITY_KIND = "identity.license_capability"
LICENSE_CAPABILITY_EXTENSION_SIGNATURES_KEY = "fixture_signature_records"
LICENSE_CAPABILITY_EXTENSION_REQUESTED_KEY = "official.requested_capability_ids"


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: object) -> list[str]:
    return sorted({str(item).strip() for item in _as_list(values) if str(item).strip()})


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(dict(value).items(), key=lambda row: str(row[0]))
            if str(key).strip()
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in list(value)]
    if isinstance(value, tuple):
        return [_normalize_tree(item) for item in list(value)]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


def license_capability_signature_rows(payload: Mapping[str, object] | None) -> list[dict]:
    extensions = _as_map(_as_map(payload).get("extensions"))
    rows = [
        canonicalize_signature_record(row)
        for row in _as_list(extensions.get(LICENSE_CAPABILITY_EXTENSION_SIGNATURES_KEY))
        if _token(_as_map(row).get("signer_id")) and _token(_as_map(row).get("signed_hash"))
    ]
    return sorted(
        rows,
        key=lambda row: (
            _token(row.get("signed_hash")),
            _token(row.get("signer_id")),
            _token(row.get("signature_id")),
        ),
    )


def _normalized_extensions(payload: Mapping[str, object] | None, *, include_signatures: bool) -> dict:
    extensions = dict(_as_map(_as_map(payload).get("extensions")))
    if include_signatures:
        extensions[LICENSE_CAPABILITY_EXTENSION_SIGNATURES_KEY] = [
            dict(row) for row in license_capability_signature_rows(payload)
        ]
    else:
        extensions.pop(LICENSE_CAPABILITY_EXTENSION_SIGNATURES_KEY, None)
    return {
        str(key): _normalize_tree(value)
        for key, value in sorted(extensions.items(), key=lambda row: str(row[0]))
        if str(key).strip()
    }


def license_capability_signed_hash(payload: Mapping[str, object] | None) -> str:
    item = dict(_as_map(payload))
    item.pop(UNIVERSAL_IDENTITY_FIELD, None)
    item["schema_id"] = _token(item.get("schema_id")) or LICENSE_CAPABILITY_SCHEMA_ID
    item["schema_version"] = _token(item.get("schema_version")) or LICENSE_CAPABILITY_SCHEMA_VERSION
    item["artifact_kind_id"] = ARTIFACT_KIND_LICENSE_CAPABILITY
    item["enabled_capabilities"] = _sorted_tokens(item.get("enabled_capabilities"))
    item["valid_from_release"] = _token(item.get("valid_from_release"))
    item["valid_to_release"] = _token(item.get("valid_to_release"))
    item["deterministic_fingerprint"] = ""
    item["extensions"] = _normalized_extensions(payload, include_signatures=False)
    return canonical_sha256(_normalize_tree(item))


def canonicalize_license_capability_artifact(payload: Mapping[str, object] | None) -> dict:
    item = dict(_as_map(payload))
    item["schema_id"] = _token(item.get("schema_id")) or LICENSE_CAPABILITY_SCHEMA_ID
    item["schema_version"] = _token(item.get("schema_version")) or LICENSE_CAPABILITY_SCHEMA_VERSION
    item["artifact_kind_id"] = ARTIFACT_KIND_LICENSE_CAPABILITY
    item["enabled_capabilities"] = _sorted_tokens(item.get("enabled_capabilities"))
    item["valid_from_release"] = _token(item.get("valid_from_release"))
    item["valid_to_release"] = _token(item.get("valid_to_release"))
    item["extensions"] = _normalized_extensions(item, include_signatures=True)
    if _as_map(item.get(UNIVERSAL_IDENTITY_FIELD)):
        item[UNIVERSAL_IDENTITY_FIELD] = canonicalize_universal_identity_block(item.get(UNIVERSAL_IDENTITY_FIELD))
    item["deterministic_fingerprint"] = ""
    item["deterministic_fingerprint"] = deterministic_fingerprint(item)
    return item


def build_license_capability_artifact(
    *,
    artifact_id: str,
    enabled_capabilities: Sequence[object],
    valid_from_release: str = "",
    valid_to_release: str = "",
    extensions: Mapping[str, object] | None = None,
    signature_records: Sequence[Mapping[str, object]] | None = None,
    stability_class_id: str = "provisional",
) -> dict:
    payload = canonicalize_license_capability_artifact(
        {
            "schema_id": LICENSE_CAPABILITY_SCHEMA_ID,
            "schema_version": LICENSE_CAPABILITY_SCHEMA_VERSION,
            "artifact_kind_id": ARTIFACT_KIND_LICENSE_CAPABILITY,
            "enabled_capabilities": list(enabled_capabilities or []),
            "valid_from_release": _token(valid_from_release),
            "valid_to_release": _token(valid_to_release),
            "extensions": dict(_as_map(extensions)),
        }
    )
    ext = dict(_as_map(payload.get("extensions")))
    ext[LICENSE_CAPABILITY_EXTENSION_SIGNATURES_KEY] = [
        dict(row)
        for row in sorted(
            (canonicalize_signature_record(row) for row in list(signature_records or [])),
            key=lambda row: (
                _token(row.get("signed_hash")),
                _token(row.get("signer_id")),
                _token(row.get("signature_id")),
            ),
        )
    ]
    payload["extensions"] = ext
    payload[UNIVERSAL_IDENTITY_FIELD] = build_universal_identity_block(
        identity_kind_id=LICENSE_CAPABILITY_IDENTITY_KIND,
        identity_id=_token(artifact_id),
        stability_class_id=_token(stability_class_id) or "provisional",
        content_hash=license_capability_signed_hash(payload),
        schema_version=LICENSE_CAPABILITY_SCHEMA_VERSION,
        extensions={"official.artifact_kind_id": ARTIFACT_KIND_LICENSE_CAPABILITY},
    )
    return canonicalize_license_capability_artifact(payload)


def _match_requested_capability(enabled_capability: str, requested_capability: str) -> bool:
    enabled = _token(enabled_capability)
    requested = _token(requested_capability)
    if not enabled or not requested:
        return False
    if enabled == requested:
        return True
    if enabled.endswith("*"):
        return requested.startswith(enabled[:-1])
    if requested.endswith("*"):
        return enabled.startswith(requested[:-1])
    return False


def license_capability_enabled_view(
    *,
    requested_capability_ids: Sequence[object],
    enabled_capability_ids: Sequence[object],
) -> dict:
    requested = _sorted_tokens(requested_capability_ids)
    enabled = _sorted_tokens(enabled_capability_ids)
    available: list[str] = []
    degraded: list[str] = []
    for capability_id in requested:
        if any(_match_requested_capability(candidate, capability_id) for candidate in enabled):
            available.append(capability_id)
        else:
            degraded.append(capability_id)
    payload = {
        "requested_capability_ids": requested,
        "enabled_capability_ids": enabled,
        "available_capability_ids": available,
        "degraded_capability_ids": degraded,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    return payload


def verify_license_capability_artifact(
    payload: Mapping[str, object] | None,
    *,
    repo_root: str = "",
    trust_roots: Sequence[Mapping[str, object]] | None = None,
    requested_capability_ids: Sequence[object] | None = None,
) -> dict:
    artifact = canonicalize_license_capability_artifact(payload)
    signed_hash = license_capability_signed_hash(artifact)
    errors: list[dict] = []
    warnings: list[dict] = []
    required_fields = (
        "schema_id",
        "schema_version",
        "artifact_kind_id",
        "enabled_capabilities",
        "deterministic_fingerprint",
        "extensions",
    )
    for field in required_fields:
        value = artifact.get(field)
        if field == "extensions":
            present = isinstance(value, Mapping)
        elif field == "enabled_capabilities":
            present = bool(_as_list(value))
        else:
            present = bool(_token(value))
        if present:
            continue
        errors.append(
            {
                "code": "license_capability_schema_invalid",
                "path": "$.{}".format(field),
                "message": "missing required field '{}'".format(field),
            }
        )
    if _token(artifact.get("schema_id")) != LICENSE_CAPABILITY_SCHEMA_ID:
        errors.append(
            {
                "code": "license_capability_schema_invalid",
                "path": "$.schema_id",
                "message": "schema_id must equal '{}'".format(LICENSE_CAPABILITY_SCHEMA_ID),
            }
        )
    if _token(artifact.get("schema_version")) != LICENSE_CAPABILITY_SCHEMA_VERSION:
        errors.append(
            {
                "code": "license_capability_schema_invalid",
                "path": "$.schema_version",
                "message": "schema_version must equal '{}'".format(LICENSE_CAPABILITY_SCHEMA_VERSION),
            }
        )
    if _token(artifact.get("artifact_kind_id")) != ARTIFACT_KIND_LICENSE_CAPABILITY:
        errors.append(
            {
                "code": "license_capability_schema_invalid",
                "path": "$.artifact_kind_id",
                "message": "artifact_kind_id must equal '{}'".format(ARTIFACT_KIND_LICENSE_CAPABILITY),
            }
        )
    if _token(artifact.get("deterministic_fingerprint")) != deterministic_fingerprint(artifact):
        errors.append(
            {
                "code": "license_capability_fingerprint_mismatch",
                "path": "$.deterministic_fingerprint",
                "message": "deterministic_fingerprint mismatch",
            }
        )
    expected_identity = build_universal_identity_block(
        identity_kind_id=LICENSE_CAPABILITY_IDENTITY_KIND,
        identity_id=_token(_as_map(artifact.get(UNIVERSAL_IDENTITY_FIELD)).get("identity_id")),
        stability_class_id=_token(_as_map(artifact.get(UNIVERSAL_IDENTITY_FIELD)).get("stability_class_id")) or "provisional",
        content_hash=signed_hash,
        schema_version=LICENSE_CAPABILITY_SCHEMA_VERSION,
        extensions={"official.artifact_kind_id": ARTIFACT_KIND_LICENSE_CAPABILITY},
    )
    identity_report = validate_identity_block(
        repo_root=repo_root or ".",
        identity_block=_as_map(artifact.get(UNIVERSAL_IDENTITY_FIELD)),
        expected=expected_identity,
        strict_missing=True,
        path="license_capability",
    )
    errors.extend(list(identity_report.get("errors") or []))
    warnings.extend(list(identity_report.get("warnings") or []))
    trust_policy = select_trust_policy(load_trust_policy_registry(repo_root=repo_root), trust_policy_id=TRUST_POLICY_STRICT)
    trust_report = verify_artifact_trust(
        artifact_kind=ARTIFACT_KIND_LICENSE_CAPABILITY,
        content_hash=signed_hash,
        signatures=license_capability_signature_rows(artifact),
        trust_policy_id=TRUST_POLICY_STRICT,
        trust_policy=trust_policy,
        trust_roots=trust_roots,
    )
    result = "complete"
    refusal_code = ""
    remediation_hint = ""
    if errors:
        result = "refused"
        refusal_code = "refusal.license_capability.schema_invalid"
        remediation_hint = "Rebuild the license capability artifact so it satisfies the canonical schema and identity rules."
    elif _token(trust_report.get("result")) == "refused":
        result = "refused"
        refusal_code = _token(trust_report.get("refusal_code"))
        remediation_hint = _token(trust_report.get("remediation_hint"))
    display = license_capability_enabled_view(
        requested_capability_ids=requested_capability_ids or _as_map(artifact.get("extensions")).get(LICENSE_CAPABILITY_EXTENSION_REQUESTED_KEY) or [],
        enabled_capability_ids=_as_list(artifact.get("enabled_capabilities")) if result == "complete" else [],
    )
    payload_out = {
        "result": result,
        "refusal_code": refusal_code,
        "remediation_hint": remediation_hint,
        "artifact_kind_id": ARTIFACT_KIND_LICENSE_CAPABILITY,
        "content_hash": signed_hash,
        "enabled_capabilities": _sorted_tokens(artifact.get("enabled_capabilities")) if result == "complete" else [],
        "display": display,
        "trust_result": trust_report,
        "errors": errors,
        "warnings": warnings,
        "deterministic_fingerprint": "",
    }
    payload_out["deterministic_fingerprint"] = deterministic_fingerprint(payload_out)
    return payload_out


__all__ = [
    "LICENSE_CAPABILITY_EXTENSION_REQUESTED_KEY",
    "LICENSE_CAPABILITY_EXTENSION_SIGNATURES_KEY",
    "LICENSE_CAPABILITY_IDENTITY_KIND",
    "LICENSE_CAPABILITY_SCHEMA_ID",
    "LICENSE_CAPABILITY_SCHEMA_VERSION",
    "build_license_capability_artifact",
    "canonicalize_license_capability_artifact",
    "license_capability_enabled_view",
    "license_capability_signature_rows",
    "license_capability_signed_hash",
    "verify_license_capability_artifact",
]
