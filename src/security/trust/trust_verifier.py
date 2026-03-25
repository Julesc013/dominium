"""Offline-first trust policy and signature verification helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


DEFAULT_TRUST_POLICY_REGISTRY_REL = os.path.join("data", "registries", "trust_policy_registry.json")
DEFAULT_TRUST_ROOT_REGISTRY_REL = os.path.join("data", "registries", "trust_root_registry.json")
DEFAULT_LOCAL_TRUST_ROOT_REGISTRY_REL = os.path.join("manifests", "trust_root_registry.local.json")
DEFAULT_TRUST_POLICY_ID = "trust.default_mock"
TRUST_POLICY_STRICT = "trust.strict_ranked"
TRUST_POLICY_ANARCHY = "trust.anarchy"

DEFAULT_SIGNATURE_SCHEME_ID = "signature.mock_detached_hash.v1"

ARTIFACT_KIND_RELEASE_INDEX = "artifact.release_index"
ARTIFACT_KIND_RELEASE_MANIFEST = "artifact.release_manifest"
ARTIFACT_KIND_PACK = "artifact.pack"
ARTIFACT_KIND_PACK_COMPAT = "artifact.pack_compat"
ARTIFACT_KIND_LICENSE_CAPABILITY = "artifact.license_capability"

TRUST_LEVEL_OFFICIAL_SIGNED = "trust.official_signed"
TRUST_LEVEL_THIRDPARTY_SIGNED = "trust.thirdparty_signed"
TRUST_LEVEL_UNSIGNED = "trust.unsigned"
TRUST_LEVEL_LOCAL_DEV = "trust.local_dev"

SIGNATURE_STATUS_MISSING = "signature_missing"
SIGNATURE_STATUS_INVALID = "signature_invalid"
SIGNATURE_STATUS_VERIFIED = "verified"

REFUSAL_TRUST_HASH_MISSING = "refusal.trust.hash_missing"
REFUSAL_TRUST_SIGNATURE_MISSING = "refusal.trust.signature_missing"
REFUSAL_TRUST_SIGNATURE_INVALID = "refusal.trust.signature_invalid"
REFUSAL_TRUST_ROOT_NOT_TRUSTED = "refusal.trust.root_not_trusted"
REFUSAL_TRUST_POLICY_MISSING = "refusal.trust.policy_missing"


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: object) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: object) -> list[str]:
    return sorted({str(item).strip() for item in _as_list(values) if str(item).strip()})


def deterministic_fingerprint(payload: Mapping[str, object] | None) -> str:
    body = dict(payload or {})
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _read_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return target


def _is_sha256_hex(token: str) -> bool:
    value = _token(token).lower()
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _mock_signature_bytes(*, signature_id: str, signer_id: str, signed_hash: str) -> str:
    return canonical_sha256(
        {
            "scheme_id": DEFAULT_SIGNATURE_SCHEME_ID,
            "signature_id": _token(signature_id),
            "signer_id": _token(signer_id),
            "signed_hash": _token(signed_hash).lower(),
        }
    )


def canonicalize_signature_record(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "signature_id": _token(item.get("signature_id"))
        or "signature.{}.{}".format(
            _token(item.get("signer_id")).replace(" ", "_") or "anonymous",
            _token(item.get("signed_hash")).lower()[:16] or "unsigned",
        ),
        "signer_id": _token(item.get("signer_id")),
        "signed_hash": _token(item.get("signed_hash")).lower(),
        "signature_bytes": _token(item.get("signature_bytes")),
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(item.get("extensions")).items(), key=lambda pair: str(pair[0]))
        },
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def verify_signature_records(signed_hash: str, signatures: Sequence[Mapping[str, object]] | None) -> dict:
    signed_hash_token = _token(signed_hash).lower()
    rows = sorted(
        (
            canonicalize_signature_record(row)
            for row in list(signatures or [])
            if _token(_as_map(row).get("signer_id")) and _token(_as_map(row).get("signed_hash"))
        ),
        key=lambda row: (
            _token(row.get("signed_hash")),
            _token(row.get("signer_id")),
            _token(row.get("signature_id")),
            _token(row.get("signature_bytes")),
        ),
    )
    if not rows:
        return {
            "status": SIGNATURE_STATUS_MISSING,
            "verified_count": 0,
            "verified_signer_ids": [],
            "errors": [],
        }
    errors: list[dict[str, str]] = []
    verified_signer_ids: set[str] = set()
    verified_count = 0
    for row in rows:
        scheme_id = _token(_as_map(row.get("extensions")).get("scheme_id")) or DEFAULT_SIGNATURE_SCHEME_ID
        if _token(row.get("signed_hash")).lower() != signed_hash_token:
            errors.append(
                {
                    "code": "signature_signed_hash_mismatch",
                    "signature_id": _token(row.get("signature_id")),
                    "message": "signature signed_hash does not match the expected artifact hash",
                }
            )
            continue
        if scheme_id != DEFAULT_SIGNATURE_SCHEME_ID:
            errors.append(
                {
                    "code": "signature_unknown_scheme",
                    "signature_id": _token(row.get("signature_id")),
                    "message": "unsupported signature scheme '{}'".format(scheme_id),
                }
            )
            continue
        expected_bytes = _mock_signature_bytes(
            signature_id=_token(row.get("signature_id")),
            signer_id=_token(row.get("signer_id")),
            signed_hash=signed_hash_token,
        )
        if _token(row.get("signature_bytes")) != expected_bytes:
            errors.append(
                {
                    "code": "signature_bytes_mismatch",
                    "signature_id": _token(row.get("signature_id")),
                    "message": "signature bytes do not match the deterministic mock signature hook",
                }
            )
            continue
        verified_count += 1
        verified_signer_ids.add(_token(row.get("signer_id")))
    return {
        "status": SIGNATURE_STATUS_VERIFIED if not errors else SIGNATURE_STATUS_INVALID,
        "verified_count": verified_count,
        "verified_signer_ids": sorted(verified_signer_ids),
        "errors": errors,
    }


def _canonicalize_trust_root(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "signer_id": _token(item.get("signer_id")),
        "public_key_bytes": _token(item.get("public_key_bytes")),
        "trust_level_id": _token(item.get("trust_level_id")),
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(item.get("extensions")).items(), key=lambda pair: str(pair[0]))
        },
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def _canonicalize_trust_policy(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    normalized = {
        "trust_policy_id": _token(item.get("trust_policy_id")),
        "require_signatures_for": _sorted_tokens(item.get("require_signatures_for")),
        "allow_unsigned_for": _sorted_tokens(item.get("allow_unsigned_for")),
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(item.get("extensions")).items(), key=lambda pair: str(pair[0]))
        },
    }
    normalized["deterministic_fingerprint"] = deterministic_fingerprint(normalized)
    return normalized


def load_trust_policy_registry(repo_root: str = "", registry_path: str = "") -> dict:
    path = _token(registry_path)
    if not path:
        if not _token(repo_root):
            return {}
        path = os.path.join(_norm(repo_root), DEFAULT_TRUST_POLICY_REGISTRY_REL)
    payload = _read_json(path)
    record = _as_map(payload.get("record"))
    rows = [
        _canonicalize_trust_policy(row)
        for row in list(record.get("trust_policies") or [])
        if _token(_as_map(row).get("trust_policy_id"))
    ]
    return {
        "schema_id": _token(payload.get("schema_id")),
        "schema_version": _token(payload.get("schema_version")),
        "record": {
            "registry_id": _token(record.get("registry_id")),
            "registry_version": _token(record.get("registry_version")),
            "trust_policies": sorted(rows, key=lambda row: _token(row.get("trust_policy_id"))),
            "extensions": dict(record.get("extensions") or {}),
        },
    }


def _trust_root_paths(repo_root: str = "", install_root: str = "", trust_root_registry_path: str = "") -> list[str]:
    paths: list[str] = []
    explicit = _token(trust_root_registry_path)
    if explicit:
        paths.append(_norm(explicit))
    elif _token(repo_root):
        paths.append(os.path.join(_norm(repo_root), DEFAULT_TRUST_ROOT_REGISTRY_REL))
    if _token(install_root):
        local_path = os.path.join(_norm(install_root), DEFAULT_LOCAL_TRUST_ROOT_REGISTRY_REL)
        if local_path not in paths:
            paths.append(local_path)
    return paths


def load_trust_root_registry(repo_root: str = "", *, install_root: str = "", registry_path: str = "") -> dict:
    merged_rows: dict[str, dict] = {}
    schema_id = "dominium.registry.security.trust_root_registry"
    schema_version = "1.0.0"
    registry_id = "dominium.registry.security.trust_root_registry"
    registry_version = "1.0.0"
    extensions: dict[str, object] = {}
    for path in _trust_root_paths(repo_root=repo_root, install_root=install_root, trust_root_registry_path=registry_path):
        if not os.path.isfile(path):
            continue
        payload = _read_json(path)
        record = _as_map(payload.get("record"))
        schema_id = _token(payload.get("schema_id")) or schema_id
        schema_version = _token(payload.get("schema_version")) or schema_version
        registry_id = _token(record.get("registry_id")) or registry_id
        registry_version = _token(record.get("registry_version")) or registry_version
        extensions.update(_as_map(record.get("extensions")))
        for row in list(record.get("trust_roots") or []):
            root_row = _canonicalize_trust_root(row)
            signer_id = _token(root_row.get("signer_id"))
            if signer_id:
                merged_rows[signer_id] = root_row
    return {
        "schema_id": schema_id,
        "schema_version": schema_version,
        "record": {
            "registry_id": registry_id,
            "registry_version": registry_version,
            "trust_roots": [merged_rows[key] for key in sorted(merged_rows.keys())],
            "extensions": dict((key, extensions[key]) for key in sorted(extensions.keys())),
        },
    }


def write_trust_root_registry(path: str, roots: Sequence[Mapping[str, object]]) -> str:
    payload = {
        "schema_id": "dominium.registry.security.trust_root_registry",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.security.trust_root_registry",
            "registry_version": "1.0.0",
            "trust_roots": sorted(
                (_canonicalize_trust_root(row) for row in list(roots or []) if _token(_as_map(row).get("signer_id"))),
                key=lambda row: _token(row.get("signer_id")),
            ),
            "extensions": {
                "official.source": "TRUST-MODEL0-4",
            },
        },
    }
    return _write_json(path, payload)


def select_trust_policy(registry_payload: Mapping[str, object] | None, trust_policy_id: str = "") -> dict:
    target = _token(trust_policy_id) or DEFAULT_TRUST_POLICY_ID
    rows = list(_as_map(registry_payload).get("record", {}).get("trust_policies") or [])
    for row in rows:
        item = _canonicalize_trust_policy(row)
        if _token(item.get("trust_policy_id")) == target:
            return item
    return {}


def _trust_policy_from_mod_policy(mod_policy_id: str) -> str:
    token = _token(mod_policy_id)
    if token == "mod_policy.strict":
        return TRUST_POLICY_STRICT
    if token == "mod_policy.anarchy":
        return TRUST_POLICY_ANARCHY
    return DEFAULT_TRUST_POLICY_ID


def effective_trust_policy_id(
    *,
    requested_trust_policy_id: str = "",
    install_manifest: Mapping[str, object] | None = None,
    mod_policy_id: str = "",
    server_config: Mapping[str, object] | None = None,
) -> str:
    if _token(requested_trust_policy_id):
        return _token(requested_trust_policy_id)
    install_extensions = _as_map(_as_map(install_manifest).get("extensions"))
    if _token(install_extensions.get("official.trust_policy_id")):
        return _token(install_extensions.get("official.trust_policy_id"))
    server_extensions = _as_map(_as_map(server_config).get("extensions"))
    if _token(server_extensions.get("official.trust_policy_id")):
        return _token(server_extensions.get("official.trust_policy_id"))
    install_default_mod = _token(_as_map(install_manifest).get("default_mod_policy_id"))
    return _trust_policy_from_mod_policy(_token(mod_policy_id) or install_default_mod)


def _warning(code: str, message: str, *, artifact_kind: str = "", remediation_hint: str = "") -> dict:
    return {
        "code": _token(code),
        "message": _token(message),
        "artifact_kind": _token(artifact_kind),
        "remediation_hint": _token(remediation_hint),
    }


def verify_artifact_trust(
    *,
    artifact_kind: str,
    content_hash: str,
    signatures: Sequence[Mapping[str, object]] | None = None,
    trust_policy_id: str = "",
    trust_policy: Mapping[str, object] | None = None,
    trust_roots: Sequence[Mapping[str, object]] | None = None,
    repo_root: str = "",
    install_root: str = "",
    trust_policy_registry_path: str = "",
    trust_root_registry_path: str = "",
    trust_level_id: str = "",
    signature_status_hint: str = "",
    verified_signer_ids_hint: Sequence[object] | None = None,
) -> dict:
    artifact_kind_token = _token(artifact_kind)
    hash_token = _token(content_hash).lower()
    if not _is_sha256_hex(hash_token):
        payload = {
            "result": "refused",
            "artifact_kind": artifact_kind_token,
            "content_hash": hash_token,
            "trust_policy_id": _token(trust_policy_id) or DEFAULT_TRUST_POLICY_ID,
            "trust_level_id": _token(trust_level_id),
            "signature_status": SIGNATURE_STATUS_MISSING,
            "verified_signature_count": 0,
            "verified_signer_ids": [],
            "trusted_signer_ids": [],
            "refusal_code": REFUSAL_TRUST_HASH_MISSING,
            "reason": "artifact content hash is missing or invalid",
            "remediation_hint": "Regenerate the artifact manifest or verification input so a canonical SHA-256 content hash is present.",
            "warnings": [],
            "errors": [{"code": REFUSAL_TRUST_HASH_MISSING, "message": "artifact content hash is missing or invalid"}],
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
        return payload

    policy_registry = load_trust_policy_registry(repo_root=repo_root, registry_path=trust_policy_registry_path)
    policy = _canonicalize_trust_policy(trust_policy) if _token(_as_map(trust_policy).get("trust_policy_id")) else select_trust_policy(policy_registry, trust_policy_id=trust_policy_id)
    if not policy:
        payload = {
            "result": "refused",
            "artifact_kind": artifact_kind_token,
            "content_hash": hash_token,
            "trust_policy_id": _token(trust_policy_id) or DEFAULT_TRUST_POLICY_ID,
            "trust_level_id": _token(trust_level_id),
            "signature_status": SIGNATURE_STATUS_MISSING,
            "verified_signature_count": 0,
            "verified_signer_ids": [],
            "trusted_signer_ids": [],
            "refusal_code": REFUSAL_TRUST_POLICY_MISSING,
            "reason": "trust policy is missing or undeclared",
            "remediation_hint": "Declare the requested trust policy in data/registries/trust_policy_registry.json or choose a supported trust policy id.",
            "warnings": [],
            "errors": [{"code": REFUSAL_TRUST_POLICY_MISSING, "message": "trust policy is missing or undeclared"}],
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
        return payload

    signature_status = _token(signature_status_hint)
    verified_signer_ids = sorted({str(item).strip() for item in list(verified_signer_ids_hint or []) if str(item).strip()})
    verified_count = len(verified_signer_ids)
    signature_errors: list[dict] = []
    if not signature_status:
        signature_report = verify_signature_records(hash_token, signatures)
        signature_status = _token(signature_report.get("status")) or SIGNATURE_STATUS_MISSING
        verified_signer_ids = [str(item).strip() for item in list(signature_report.get("verified_signer_ids") or []) if str(item).strip()]
        verified_count = int(signature_report.get("verified_count") or 0)
        signature_errors = list(signature_report.get("errors") or [])

    root_registry = (
        {
            "schema_id": "dominium.registry.security.trust_root_registry",
            "schema_version": "1.0.0",
            "record": {
                "registry_id": "dominium.registry.security.trust_root_registry",
                "registry_version": "1.0.0",
                "trust_roots": [
                    _canonicalize_trust_root(row)
                    for row in list(trust_roots or [])
                    if _token(_as_map(row).get("signer_id"))
                ],
                "extensions": {},
            },
        }
        if trust_roots is not None
        else load_trust_root_registry(repo_root=repo_root, install_root=install_root, registry_path=trust_root_registry_path)
    )
    trusted_root_rows = {
        _token(_as_map(row).get("signer_id")): _canonicalize_trust_root(row)
        for row in list(_as_map(root_registry).get("record", {}).get("trust_roots") or [])
        if _token(_as_map(row).get("signer_id"))
    }
    trusted_signers = sorted([token for token in verified_signer_ids if token in trusted_root_rows])

    require_signatures_for = _sorted_tokens(policy.get("require_signatures_for"))
    allow_unsigned_for = _sorted_tokens(policy.get("allow_unsigned_for"))
    policy_extensions = _as_map(policy.get("extensions"))
    warn_unsigned_for = _sorted_tokens(policy_extensions.get("warn_unsigned_for"))
    signed_bridge_levels = _sorted_tokens(policy_extensions.get("allow_signed_bridge_trust_levels"))
    untrusted_root_behavior = _token(policy_extensions.get("untrusted_root_behavior")) or "warn"

    warnings: list[dict] = []
    refusal_code = ""
    reason = ""
    remediation_hint = ""
    result = "complete"
    effective_signature_status = signature_status

    if signature_status == SIGNATURE_STATUS_INVALID:
        refusal_code = REFUSAL_TRUST_SIGNATURE_INVALID
        reason = "signature verification failed"
        remediation_hint = "Regenerate or replace the invalid signature records, or switch to a policy that accepts unsigned artifacts only if signatures are intentionally omitted."
        result = "refused"
    elif signature_status == SIGNATURE_STATUS_MISSING:
        bridge_applies = artifact_kind_token in {ARTIFACT_KIND_PACK, ARTIFACT_KIND_PACK_COMPAT} and _token(trust_level_id) in signed_bridge_levels
        if bridge_applies:
            effective_signature_status = "declared_signed_bridge"
            warnings.append(
                _warning(
                    "warn.trust.pack_signed_bridge",
                    "pack trust_level_id satisfies the MVP signed-pack bridge without detached signatures",
                    artifact_kind=artifact_kind_token,
                    remediation_hint="Add detached signatures for pack artifacts when signed pack manifests become first-class governed artifacts.",
                )
            )
        elif artifact_kind_token in require_signatures_for:
            refusal_code = REFUSAL_TRUST_SIGNATURE_MISSING
            reason = "signatures are required by the selected trust policy"
            remediation_hint = "Provide detached or inline signatures for the artifact, or select a trust policy that explicitly allows unsigned artifacts."
            result = "refused"
        elif artifact_kind_token in allow_unsigned_for:
            if artifact_kind_token in warn_unsigned_for:
                result = "warn"
                warnings.append(
                    _warning(
                        "warn.trust.signature_missing",
                        "artifact is unsigned but the selected trust policy allows it",
                        artifact_kind=artifact_kind_token,
                        remediation_hint="Sign the artifact or choose a stricter trust policy for ranked or release environments.",
                    )
                )
        else:
            refusal_code = REFUSAL_TRUST_SIGNATURE_MISSING
            reason = "artifact is unsigned and the selected trust policy does not allow unsigned acceptance"
            remediation_hint = "Provide a valid signature or choose a trust policy that explicitly allows unsigned artifacts for this artifact kind."
            result = "refused"
    elif signature_status == SIGNATURE_STATUS_VERIFIED and not trusted_signers:
        if untrusted_root_behavior == "refuse":
            refusal_code = REFUSAL_TRUST_ROOT_NOT_TRUSTED
            reason = "artifact was signed by an untrusted signer"
            remediation_hint = "Import the signer public key into the local trust root registry or choose a trust policy that only warns on untrusted roots."
            result = "refused"
        else:
            result = "warn"
            warnings.append(
                _warning(
                    "warn.trust.root_not_trusted",
                    "artifact signature verified, but no matching trusted root is installed",
                    artifact_kind=artifact_kind_token,
                    remediation_hint="Import the signer into the trust root registry if this signer should be trusted offline.",
                )
            )

    payload = {
        "result": result,
        "artifact_kind": artifact_kind_token,
        "content_hash": hash_token,
        "trust_policy_id": _token(policy.get("trust_policy_id")) or DEFAULT_TRUST_POLICY_ID,
        "trust_level_id": _token(trust_level_id),
        "signature_status": effective_signature_status or SIGNATURE_STATUS_MISSING,
        "verified_signature_count": verified_count,
        "verified_signer_ids": sorted(verified_signer_ids),
        "trusted_signer_ids": trusted_signers,
        "refusal_code": refusal_code,
        "reason": reason,
        "remediation_hint": remediation_hint,
        "warnings": warnings,
        "errors": signature_errors,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = deterministic_fingerprint(payload)
    return payload
