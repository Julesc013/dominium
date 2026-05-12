"""Universe identity contract-bundle construction helpers."""

from __future__ import annotations

from typing import Dict, Mapping, Tuple

from tools.compatx.core.semantic_contract_validator import (
    build_default_universe_contract_bundle,
    build_semantic_contract_proof_bundle,
    bundle_hash,
    load_semantic_contract_registry,
    validate_semantic_contract_registry,
    validate_universe_contract_bundle,
)
from tools.xstack.sessionx.common import identity_hash_for_payload


def build_universe_contract_bundle_payload(
    repo_root: str,
    *,
    explicit_bundle_payload: Mapping[str, object] | None = None,
) -> Tuple[dict, dict, dict, list[str]]:
    registry_payload, registry_error = load_semantic_contract_registry(repo_root)
    if registry_error:
        return {}, {}, {}, ["refuse.semantic_contract_registry_missing"]
    registry_errors = validate_semantic_contract_registry(registry_payload)
    if registry_errors:
        return {}, {}, {}, sorted(set(registry_errors))

    bundle_payload = (
        dict(explicit_bundle_payload)
        if isinstance(explicit_bundle_payload, Mapping)
        else build_default_universe_contract_bundle(registry_payload)
    )
    bundle_errors = validate_universe_contract_bundle(
        repo_root=repo_root,
        payload=bundle_payload,
        registry_payload=registry_payload,
    )
    if bundle_errors:
        return {}, {}, {}, sorted(set(bundle_errors))
    proof_bundle = build_semantic_contract_proof_bundle(registry_payload, bundle_payload)
    return dict(bundle_payload), dict(registry_payload), dict(proof_bundle), []


def pin_contract_bundle_metadata(
    identity_payload: Mapping[str, object],
    *,
    bundle_ref: str,
    bundle_payload: Mapping[str, object],
) -> dict:
    payload = dict(identity_payload or {})
    payload["universe_contract_bundle_ref"] = str(bundle_ref).strip()
    payload["universe_contract_bundle_hash"] = bundle_hash(bundle_payload)
    payload["identity_hash"] = identity_hash_for_payload(payload)
    return payload


def validate_pinned_contract_bundle_metadata(
    identity_payload: Mapping[str, object] | None,
    *,
    bundle_ref: str,
    bundle_payload: Mapping[str, object] | None,
) -> list[str]:
    payload = dict(identity_payload or {})
    errors: list[str] = []
    expected_ref = str(bundle_ref).strip()
    actual_ref = str(payload.get("universe_contract_bundle_ref", "")).strip()
    actual_hash = str(payload.get("universe_contract_bundle_hash", "")).strip()
    expected_hash = bundle_hash(bundle_payload or {})
    if actual_ref != expected_ref:
        errors.append("refuse.contract.missing_bundle")
    if not actual_hash:
        errors.append("refuse.contract.missing_bundle")
    elif actual_hash != expected_hash:
        errors.append("refuse.contract.mismatch")
    expected_identity_hash = identity_hash_for_payload(payload)
    if str(payload.get("identity_hash", "")).strip() != expected_identity_hash:
        errors.append("refuse.universe_identity_hash_mismatch")
    return sorted(set(errors))
