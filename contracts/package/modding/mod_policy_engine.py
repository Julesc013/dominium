"""Deterministic mod trust and capability policy helpers."""

from __future__ import annotations

import json
import os
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from meta.extensions.extensions_engine import extensions_get, load_extension_interpretation_registry
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance


PACK_TRUST_DESCRIPTOR_NAME = "pack.trust.json"
PACK_CAPABILITIES_NAME = "pack.capabilities.json"
DEFAULT_MOD_POLICY_ID = "mod_policy.lab"

PACK_TRUST_DESCRIPTOR_SCHEMA_NAME = "pack_trust_descriptor"
PACK_CAPABILITIES_SCHEMA_NAME = "pack_capabilities"
MOD_POLICY_PROFILE_SCHEMA_NAME = "mod_policy_profile"

MOD_POLICY_REGISTRY_REL = os.path.join("data", "registries", "mod_policy_registry.json")
CAPABILITY_REGISTRY_REL = os.path.join("data", "registries", "capability_registry.json")

REFUSAL_MOD_TRUST_DENIED = "refusal.mod.trust_denied"
REFUSAL_MOD_CAPABILITY_DENIED = "refusal.mod.capability_denied"
REFUSAL_MOD_NONDETERMINISM_FORBIDDEN = "refusal.mod.nondeterminism_forbidden"
REFUSAL_MOD_DESCRIPTOR_MISSING = "refusal.mod.descriptor_missing"
REFUSAL_MOD_POLICY_MISMATCH = "refusal.mod.policy_mismatch"

_PROFILE_CONTRIBUTION_TYPES = {"experience_profile", "law_profile"}
_NOISE_EXTENSION_KEY = "official.requests_nondeterministic_allowance"


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _error(path: str, message: str, *, code: str) -> dict:
    return {
        "code": str(code),
        "path": str(path),
        "message": str(message),
    }


def _refusal(code: str, message: str, remediation: str, details: Mapping[str, object] | None = None, path: str = "$") -> dict:
    error_row = _error(path, message, code=code)
    return {
        "result": "refused",
        "refusal_code": str(code),
        "message": str(message),
        "remediation": str(remediation),
        "details": dict(details or {}),
        "errors": [error_row],
    }


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _registry_rows(payload: Mapping[str, object] | None, key: str) -> List[dict]:
    body = _as_map(payload)
    rows = body.get(key)
    if isinstance(rows, list):
        return [dict(item) for item in rows if isinstance(item, Mapping)]
    record = _as_map(body.get("record"))
    rows = record.get(key)
    if isinstance(rows, list):
        return [dict(item) for item in rows if isinstance(item, Mapping)]
    return []


def _validate_schema_payload(repo_root: str, schema_name: str, payload: dict) -> List[dict]:
    report = validate_instance(repo_root=repo_root, schema_name=schema_name, payload=payload, strict_top_level=True)
    if bool(report.get("valid", False)):
        return []
    rows: List[dict] = []
    for err in report.get("errors") or []:
        if not isinstance(err, Mapping):
            continue
        rows.append(
            {
                "code": str(err.get("code", "schema_invalid")),
                "path": str(err.get("path", "$")),
                "message": str(err.get("message", "")),
            }
        )
    return rows


def _deterministic_fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(payload)
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _profile_exception_requested(payload: Mapping[str, object] | None) -> bool:
    row = _as_map(payload)
    if _as_map(row.get("overrides")):
        return True
    if _sorted_tokens(row.get("profile_override_allowed_rule_ids")):
        return True
    ext = _as_map(row.get("extensions"))
    if _sorted_tokens(ext.get("profile_override_allowed_rule_ids")):
        return True
    return False


def load_mod_policy_registry(repo_root: str, schema_repo_root: str = "") -> Tuple[dict, List[dict]]:
    schema_root = os.path.abspath(schema_repo_root) if str(schema_repo_root).strip() else repo_root
    path = os.path.join(repo_root, MOD_POLICY_REGISTRY_REL)
    if not os.path.isfile(path) and schema_root != repo_root:
        path = os.path.join(schema_root, MOD_POLICY_REGISTRY_REL)
    payload, error = _read_json(path)
    if error:
        return {}, [_error("$.mod_policy_registry", "unable to load mod policy registry", code="mod_policy_registry_invalid")]
    rows = _registry_rows(payload, "mod_policies")
    errors: List[dict] = []
    normalized_rows: List[dict] = []
    for row in sorted(rows, key=lambda item: str(item.get("mod_policy_id", ""))):
        normalized = {
            "schema_version": str(row.get("schema_version", "1.0.0")).strip() or "1.0.0",
            "mod_policy_id": str(row.get("mod_policy_id", "")).strip(),
            "allowed_trust_levels": _sorted_tokens(row.get("allowed_trust_levels")),
            "allowed_capabilities": _sorted_tokens(row.get("allowed_capabilities")),
            "conflict_policy_id": str(row.get("conflict_policy_id", "")).strip(),
            "forbid_nondeterminism": bool(row.get("forbid_nondeterminism", False)),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": {
                str(key): value
                for key, value in sorted(_as_map(row.get("extensions")).items(), key=lambda item: str(item[0]))
            },
        }
        schema_errors = _validate_schema_payload(schema_root, MOD_POLICY_PROFILE_SCHEMA_NAME, normalized)
        if schema_errors:
            errors.extend(schema_errors)
            continue
        expected = _deterministic_fingerprint(normalized)
        if normalized["deterministic_fingerprint"] != expected:
            errors.append(
                _error(
                    "$.mod_policies.{}".format(normalized["mod_policy_id"] or "<missing>"),
                    "mod policy deterministic_fingerprint mismatch",
                    code="mod_policy_fingerprint_mismatch",
                )
            )
            continue
        normalized_rows.append(normalized)
    if errors:
        return {}, sorted(errors, key=lambda row: (row["code"], row["path"], row["message"]))
    return {
        "schema_id": str(payload.get("schema_id", "")).strip(),
        "schema_version": str(payload.get("schema_version", "")).strip(),
        "record": {
            "registry_id": str(_as_map(payload.get("record")).get("registry_id", "")).strip(),
            "registry_version": str(_as_map(payload.get("record")).get("registry_version", "")).strip(),
            "mod_policies": normalized_rows,
            "extensions": {
                str(key): value
                for key, value in sorted(_as_map(_as_map(payload.get("record")).get("extensions")).items(), key=lambda item: str(item[0]))
            },
        },
    }, []


def mod_policy_registry_hash(payload: Mapping[str, object] | None) -> str:
    return canonical_sha256(_as_map(payload))


def mod_policy_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    rows = _registry_rows(payload, "mod_policies")
    out: Dict[str, dict] = {}
    for row in sorted(rows, key=lambda item: str(item.get("mod_policy_id", ""))):
        mod_policy_id = str(row.get("mod_policy_id", "")).strip()
        if mod_policy_id:
            out[mod_policy_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def load_capability_registry(payload_path: str) -> Tuple[dict, str]:
    return _read_json(payload_path)


def _normalize_trust_descriptor(repo_root: str, payload: Mapping[str, object]) -> Tuple[dict, List[dict]]:
    row = {
        "schema_version": str(payload.get("schema_version", "1.0.0")).strip() or "1.0.0",
        "pack_id": str(payload.get("pack_id", "")).strip(),
        "trust_level_id": str(payload.get("trust_level_id", "")).strip(),
        "signature_hash": payload.get("signature_hash"),
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(payload.get("extensions")).items(), key=lambda item: str(item[0]))
        },
    }
    errors = _validate_schema_payload(repo_root, PACK_TRUST_DESCRIPTOR_SCHEMA_NAME, row)
    if errors:
        return {}, errors
    expected = _deterministic_fingerprint(row)
    if row["deterministic_fingerprint"] != expected:
        return {}, [
            _error(
                "$.deterministic_fingerprint",
                "pack trust descriptor deterministic_fingerprint mismatch",
                code="pack_trust_descriptor_fingerprint_mismatch",
            )
        ]
    return row, []


def _normalize_capabilities_descriptor(repo_root: str, payload: Mapping[str, object]) -> Tuple[dict, List[dict]]:
    row = {
        "schema_version": str(payload.get("schema_version", "1.0.0")).strip() or "1.0.0",
        "pack_id": str(payload.get("pack_id", "")).strip(),
        "capability_ids": _sorted_tokens(payload.get("capability_ids")),
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(payload.get("extensions")).items(), key=lambda item: str(item[0]))
        },
    }
    errors = _validate_schema_payload(repo_root, PACK_CAPABILITIES_SCHEMA_NAME, row)
    if errors:
        return {}, errors
    expected = _deterministic_fingerprint(row)
    if row["deterministic_fingerprint"] != expected:
        return {}, [
            _error(
                "$.deterministic_fingerprint",
                "pack capabilities deterministic_fingerprint mismatch",
                code="pack_capabilities_fingerprint_mismatch",
            )
        ]
    return row, []


def load_pack_policy_descriptors(repo_root: str, pack_row: Mapping[str, object], schema_repo_root: str = "") -> Tuple[dict, List[dict]]:
    schema_root = os.path.abspath(schema_repo_root) if str(schema_repo_root).strip() else repo_root
    pack_dir = str(pack_row.get("pack_dir", "")).strip()
    pack_id = str(pack_row.get("pack_id", "")).strip()
    trust_path = os.path.join(pack_dir, PACK_TRUST_DESCRIPTOR_NAME)
    capabilities_path = os.path.join(pack_dir, PACK_CAPABILITIES_NAME)
    errors: List[dict] = []
    if not os.path.isfile(trust_path):
        errors.append(_error("$.pack.trust", "missing pack.trust.json for '{}'".format(pack_id), code="pack_trust_missing"))
    if not os.path.isfile(capabilities_path):
        errors.append(
            _error(
                "$.pack.capabilities",
                "missing pack.capabilities.json for '{}'".format(pack_id),
                code="pack_capabilities_missing",
            )
        )
    if errors:
        return {}, errors

    trust_payload, trust_error = _read_json(trust_path)
    if trust_error:
        errors.append(_error("$.pack.trust", "invalid trust descriptor for '{}'".format(pack_id), code="pack_trust_invalid"))
    capabilities_payload, capabilities_error = _read_json(capabilities_path)
    if capabilities_error:
        errors.append(
            _error(
                "$.pack.capabilities",
                "invalid capabilities descriptor for '{}'".format(pack_id),
                code="pack_capabilities_invalid",
            )
        )
    if errors:
        return {}, errors

    trust_row, trust_schema_errors = _normalize_trust_descriptor(schema_root, trust_payload)
    capability_row, capability_schema_errors = _normalize_capabilities_descriptor(schema_root, capabilities_payload)
    errors.extend(trust_schema_errors)
    errors.extend(capability_schema_errors)
    if errors:
        return {}, sorted(errors, key=lambda row: (row["code"], row["path"], row["message"]))
    if str(trust_row.get("pack_id", "")).strip() != pack_id:
        errors.append(_error("$.pack_id", "trust descriptor pack_id mismatch for '{}'".format(pack_id), code="pack_trust_pack_id_mismatch"))
    if str(capability_row.get("pack_id", "")).strip() != pack_id:
        errors.append(
            _error("$.pack_id", "capabilities descriptor pack_id mismatch for '{}'".format(pack_id), code="pack_capabilities_pack_id_mismatch")
        )
    if errors:
        return {}, sorted(errors, key=lambda row: (row["code"], row["path"], row["message"]))

    extension_registry, _extension_registry_error = load_extension_interpretation_registry(repo_root)
    nondeterministic_allowance = bool(
        extensions_get(
            repo_root=repo_root,
            owner_schema_id="pack_capabilities",
            extensions=_as_map(capability_row.get("extensions")),
            key=_NOISE_EXTENSION_KEY,
            registry_payload=extension_registry,
            default=False,
        )
    )
    return {
        "trust_descriptor": trust_row,
        "capabilities_descriptor": capability_row,
        "trust_level_id": str(trust_row.get("trust_level_id", "")).strip(),
        "capability_ids": _sorted_tokens(capability_row.get("capability_ids")),
        "trust_descriptor_hash": canonical_sha256(trust_row),
        "capabilities_hash": canonical_sha256(capability_row),
        "requests_nondeterministic_allowance": bool(nondeterministic_allowance),
        "trust_descriptor_path": _norm(os.path.relpath(trust_path, repo_root)),
        "capabilities_descriptor_path": _norm(os.path.relpath(capabilities_path, repo_root)),
    }, []


def attach_pack_policy_descriptors(repo_root: str, pack_row: Mapping[str, object], schema_repo_root: str = "") -> Tuple[dict, List[dict]]:
    attached = dict(pack_row)
    loaded, errors = load_pack_policy_descriptors(repo_root, pack_row, schema_repo_root=schema_repo_root)
    if errors:
        return {}, errors
    attached.update(loaded)
    return attached, []


def infer_required_capabilities(pack_row: Mapping[str, object], contributions: Sequence[Mapping[str, object]] | None) -> List[str]:
    pack_id = str(pack_row.get("pack_id", "")).strip()
    rows = [
        dict(item)
        for item in list(contributions or [])
        if isinstance(item, Mapping) and str(item.get("pack_id", "")).strip() == pack_id
    ]
    required = set()
    manifest = _as_map(pack_row.get("manifest"))
    for token in _sorted_tokens(manifest.get("contribution_types")):
        if token in _PROFILE_CONTRIBUTION_TYPES:
            required.add("cap.add_profiles")
    for row in rows:
        contrib_type = str(row.get("contrib_type", "")).strip()
        contrib_id = str(row.get("id", "")).strip().lower()
        contrib_path = str(row.get("path", "")).strip().lower()
        haystack = " ".join(token for token in (contrib_type.lower(), contrib_id, contrib_path) if token)
        if contrib_type in _PROFILE_CONTRIBUTION_TYPES:
            required.add("cap.add_profiles")
            if _profile_exception_requested(_as_map(row.get("payload"))):
                required.add("cap.allow_exception_profiles")
        if "overlay" in haystack:
            required.add("cap.overlay_patch")
        if "template" in haystack:
            required.add("cap.add_templates")
        if "logic" in haystack:
            required.add("cap.add_logic_elements")
        if "process" in haystack:
            required.add("cap.add_processes")
        if "contract" in haystack:
            required.add("cap.add_contracts")
    return sorted(required)


def evaluate_mod_policy(
    *,
    repo_root: str,
    ordered_packs: Sequence[Mapping[str, object]],
    contributions: Sequence[Mapping[str, object]] | None,
    mod_policy_id: str = DEFAULT_MOD_POLICY_ID,
    schema_repo_root: str = "",
) -> dict:
    policy_registry, policy_registry_errors = load_mod_policy_registry(repo_root, schema_repo_root=schema_repo_root)
    if policy_registry_errors:
        return _refusal(
            REFUSAL_MOD_CAPABILITY_DENIED,
            "mod policy registry failed validation",
            "Repair data/registries/mod_policy_registry.json and retry bundle compilation or boot.",
            {"errors": policy_registry_errors},
            "$.mod_policy_registry",
        )
    policy_rows = mod_policy_rows_by_id(policy_registry)
    policy_token = str(mod_policy_id or DEFAULT_MOD_POLICY_ID).strip() or DEFAULT_MOD_POLICY_ID
    policy_row = dict(policy_rows.get(policy_token) or {})
    if not policy_row:
        return _refusal(
            REFUSAL_MOD_CAPABILITY_DENIED,
            "mod_policy_id '{}' is not declared".format(policy_token),
            "Select a declared mod_policy_id from data/registries/mod_policy_registry.json.",
            {"mod_policy_id": policy_token},
            "$.mod_policy_id",
        )

    evaluated_rows: List[dict] = []
    capability_errors: List[dict] = []
    for raw_pack in sorted(ordered_packs or [], key=lambda row: str(row.get("pack_id", ""))):
        pack_row = dict(raw_pack)
        if "trust_level_id" not in pack_row or "capability_ids" not in pack_row:
            pack_row, load_errors = attach_pack_policy_descriptors(
                repo_root=repo_root,
                pack_row=pack_row,
                schema_repo_root=schema_repo_root,
            )
            if load_errors:
                capability_errors.extend(load_errors)
                continue
        declared_capabilities = _sorted_tokens(pack_row.get("capability_ids"))
        required_capabilities = infer_required_capabilities(pack_row, contributions)
        missing_declared = sorted(token for token in required_capabilities if token not in set(declared_capabilities))
        if missing_declared:
            capability_errors.append(
                _error(
                    "$.packs.{}".format(str(pack_row.get("pack_id", ""))),
                    "pack '{}' is missing declared capabilities: {}".format(
                        str(pack_row.get("pack_id", "")),
                        ",".join(missing_declared),
                    ),
                    code=REFUSAL_MOD_CAPABILITY_DENIED,
                )
            )
            continue
        trust_level_id = str(pack_row.get("trust_level_id", "")).strip()
        if trust_level_id not in set(_sorted_tokens(policy_row.get("allowed_trust_levels"))):
            return _refusal(
                REFUSAL_MOD_TRUST_DENIED,
                "pack '{}' trust level '{}' is denied by policy '{}'".format(
                    str(pack_row.get("pack_id", "")),
                    trust_level_id or "<empty>",
                    policy_token,
                ),
                "Select a mod policy that allows this trust level or replace the pack with an allowed trust category.",
                {
                    "pack_id": str(pack_row.get("pack_id", "")),
                    "trust_level_id": trust_level_id,
                    "mod_policy_id": policy_token,
                },
                "$.trust_level_id",
            )
        denied_capabilities = sorted(
            token
            for token in declared_capabilities
            if token not in set(_sorted_tokens(policy_row.get("allowed_capabilities")))
        )
        if denied_capabilities:
            return _refusal(
                REFUSAL_MOD_CAPABILITY_DENIED,
                "pack '{}' declares denied capabilities under policy '{}'".format(
                    str(pack_row.get("pack_id", "")),
                    policy_token,
                ),
                "Remove the denied capabilities or switch to a policy that explicitly allows them.",
                {
                    "pack_id": str(pack_row.get("pack_id", "")),
                    "capability_ids": denied_capabilities,
                    "mod_policy_id": policy_token,
                },
                "$.capability_ids",
            )
        if bool(pack_row.get("requests_nondeterministic_allowance", False)) and bool(policy_row.get("forbid_nondeterminism", False)):
            return _refusal(
                REFUSAL_MOD_NONDETERMINISM_FORBIDDEN,
                "pack '{}' requests nondeterministic allowances forbidden by policy '{}'".format(
                    str(pack_row.get("pack_id", "")),
                    policy_token,
                ),
                "Use a policy that permits explicit nondeterministic allowances or remove the request from pack metadata.",
                {
                    "pack_id": str(pack_row.get("pack_id", "")),
                    "mod_policy_id": policy_token,
                },
                "$.extensions.{}".format(_NOISE_EXTENSION_KEY),
            )
        evaluated_rows.append(
            {
                "pack_id": str(pack_row.get("pack_id", "")).strip(),
                "version": str(pack_row.get("version", "")).strip(),
                "trust_level_id": trust_level_id,
                "capability_ids": declared_capabilities,
                "required_capabilities": required_capabilities,
                "trust_descriptor_hash": str(pack_row.get("trust_descriptor_hash", "")).strip(),
                "capabilities_hash": str(pack_row.get("capabilities_hash", "")).strip(),
                "compat_manifest_hash": str(pack_row.get("compat_manifest_hash", "")).strip(),
                "pack_degrade_mode_id": str(pack_row.get("pack_degrade_mode_id", "")).strip(),
                "requests_nondeterministic_allowance": bool(pack_row.get("requests_nondeterministic_allowance", False)),
            }
        )

    if capability_errors:
        return {
            "result": "refused",
            "refusal_code": REFUSAL_MOD_CAPABILITY_DENIED,
            "message": "pack capability declarations are incomplete or invalid",
            "remediation": "Declare all required pack capabilities and trust descriptors before compile or boot.",
            "details": {"mod_policy_id": policy_token},
            "errors": sorted(capability_errors, key=lambda row: (row["code"], row["path"], row["message"])),
        }

    proof_bundle = {
        "mod_policy_id": policy_token,
        "mod_policy_registry_hash": mod_policy_registry_hash(policy_registry),
        "overlay_conflict_policy_id": str(policy_row.get("conflict_policy_id", "")).strip(),
        "forbid_nondeterminism": bool(policy_row.get("forbid_nondeterminism", False)),
        "loaded_packs": evaluated_rows,
    }
    proof_bundle["mod_policy_proof_hash"] = canonical_sha256(dict(proof_bundle))
    return {
        "result": "complete",
        "mod_policy_id": policy_token,
        "overlay_conflict_policy_id": str(policy_row.get("conflict_policy_id", "")).strip(),
        "mod_policy_registry_hash": mod_policy_registry_hash(policy_registry),
        "proof_bundle": proof_bundle,
    }


def validate_saved_mod_policy(
    *,
    expected_mod_policy_id: str,
    expected_registry_hash: str,
    actual_proof_bundle: Mapping[str, object] | None,
) -> dict:
    bundle = dict(actual_proof_bundle or {})
    actual_policy_id = str(bundle.get("mod_policy_id", "")).strip()
    actual_registry_hash = str(bundle.get("mod_policy_registry_hash", "")).strip()
    if expected_mod_policy_id and not actual_policy_id:
        return _refusal(
            REFUSAL_MOD_POLICY_MISMATCH,
            "runtime mod policy proof bundle is missing mod_policy_id",
            "Rebuild the lockfile or proof surfaces under the pinned mod policy before load or replay.",
            {"expected_mod_policy_id": expected_mod_policy_id},
            "$.mod_policy_id",
        )
    if expected_registry_hash and not actual_registry_hash:
        return _refusal(
            REFUSAL_MOD_POLICY_MISMATCH,
            "runtime mod policy proof bundle is missing mod_policy_registry_hash",
            "Rebuild the lockfile or proof surfaces under the pinned mod policy before load or replay.",
            {"expected_mod_policy_registry_hash": expected_registry_hash},
            "$.mod_policy_registry_hash",
        )
    if expected_mod_policy_id and actual_policy_id and expected_mod_policy_id != actual_policy_id:
        return _refusal(
            REFUSAL_MOD_POLICY_MISMATCH,
            "saved mod_policy_id '{}' does not match runtime policy '{}'".format(expected_mod_policy_id, actual_policy_id),
            "Replay or resume with the original mod policy, or recreate the save under the new policy.",
            {
                "expected_mod_policy_id": expected_mod_policy_id,
                "actual_mod_policy_id": actual_policy_id,
            },
            "$.mod_policy_id",
        )
    if expected_registry_hash and actual_registry_hash and expected_registry_hash != actual_registry_hash:
        return _refusal(
            REFUSAL_MOD_POLICY_MISMATCH,
            "saved mod policy registry hash does not match runtime proof bundle",
            "Use the same mod policy registry revision or rebuild the save under the current policy set.",
            {
                "expected_mod_policy_registry_hash": expected_registry_hash,
                "actual_mod_policy_registry_hash": actual_registry_hash,
            },
            "$.mod_policy_registry_hash",
        )
    return {"result": "complete"}


def proof_bundle_from_lockfile(lockfile_payload: Mapping[str, object] | None) -> dict:
    payload = dict(lockfile_payload or {})
    bundle = {
        "mod_policy_id": str(payload.get("mod_policy_id", "")).strip(),
        "mod_policy_registry_hash": str(payload.get("mod_policy_registry_hash", "")).strip(),
        "overlay_conflict_policy_id": str(payload.get("overlay_conflict_policy_id", "")).strip(),
        "mod_policy_proof_hash": str(payload.get("mod_policy_proof_hash", "")).strip(),
        "loaded_packs": [
            {
                "pack_id": str(row.get("pack_id", "")),
                "version": str(row.get("version", "")),
                "trust_level_id": str(row.get("trust_level_id", "")),
                "capability_ids": _sorted_tokens(row.get("capability_ids")),
                "trust_descriptor_hash": str(row.get("trust_descriptor_hash", "")),
                "capabilities_hash": str(row.get("capabilities_hash", "")),
                "compat_manifest_hash": str(row.get("compat_manifest_hash", "")),
                "pack_degrade_mode_id": str(row.get("pack_degrade_mode_id", "")),
            }
            for row in list(payload.get("resolved_packs") or [])
            if isinstance(row, Mapping)
        ],
    }
    if (not bundle["mod_policy_proof_hash"]) and bundle["mod_policy_id"]:
        bundle["mod_policy_proof_hash"] = canonical_sha256(dict(bundle))
    return bundle


__all__ = [
    "DEFAULT_MOD_POLICY_ID",
    "PACK_CAPABILITIES_NAME",
    "PACK_TRUST_DESCRIPTOR_NAME",
    "REFUSAL_MOD_CAPABILITY_DENIED",
    "REFUSAL_MOD_NONDETERMINISM_FORBIDDEN",
    "REFUSAL_MOD_POLICY_MISMATCH",
    "REFUSAL_MOD_TRUST_DENIED",
    "attach_pack_policy_descriptors",
    "evaluate_mod_policy",
    "infer_required_capabilities",
    "load_mod_policy_registry",
    "load_pack_policy_descriptors",
    "mod_policy_registry_hash",
    "proof_bundle_from_lockfile",
    "mod_policy_rows_by_id",
    "validate_saved_mod_policy",
]
