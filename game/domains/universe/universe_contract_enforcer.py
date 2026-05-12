"""Universe semantic-contract load and replay enforcement."""

from __future__ import annotations

import os
from typing import Mapping

from tools.compatx.core.semantic_contract_validator import (
    build_semantic_contract_proof_bundle,
    bundle_hash,
    load_semantic_contract_registry,
    validate_semantic_contract_registry,
    validate_universe_contract_bundle,
)
from tools.xstack.sessionx.common import norm, read_json_object, refusal


DEFAULT_UNIVERSE_CONTRACT_BUNDLE_REF = "universe_contract_bundle.json"
REFUSAL_CONTRACT_MISSING_BUNDLE = "refusal.contract.missing_bundle"
REFUSAL_CONTRACT_MISMATCH = "refusal.contract.mismatch"


def refusal_contract_missing_bundle(message: str, *, relevant_ids: dict | None = None, path: str = "$") -> dict:
    return refusal(
        REFUSAL_CONTRACT_MISSING_BUNDLE,
        message,
        "Run the CompatX migration tool or recreate the universe so it writes a pinned universe contract bundle.",
        relevant_ids or {},
        path,
    )


def refusal_contract_mismatch(message: str, *, relevant_ids: dict | None = None, path: str = "$") -> dict:
    return refusal(
        REFUSAL_CONTRACT_MISMATCH,
        message,
        "Run the explicit CompatX migration tool for this universe lineage or use a universe created under matching semantic contracts.",
        relevant_ids or {},
        path,
    )


def _bundle_path(identity_path: str, bundle_ref: str) -> str:
    token = str(bundle_ref or "").strip()
    if not token:
        return ""
    if os.path.isabs(token):
        return os.path.normpath(token)
    return os.path.normpath(os.path.join(os.path.dirname(identity_path), token))


def enforce_session_contract_bundle(
    *,
    repo_root: str,
    session_spec: Mapping[str, object] | None,
    universe_identity: Mapping[str, object] | None,
    identity_path: str,
    replay_mode: bool = False,
) -> dict:
    spec = dict(session_spec or {})
    identity = dict(universe_identity or {})
    save_id = str(spec.get("save_id", "")).strip()
    bundle_ref = str(identity.get("universe_contract_bundle_ref", "")).strip()
    bundle_hash_expected = str(identity.get("universe_contract_bundle_hash", "")).strip()
    session_bundle_hash = str(spec.get("contract_bundle_hash", "")).strip()

    if not bundle_ref or not bundle_hash_expected:
        return refusal_contract_missing_bundle(
            "UniverseIdentity is missing pinned universe contract bundle metadata",
            relevant_ids={"save_id": save_id, "universe_id": str(identity.get("universe_id", ""))},
            path="$.universe_identity",
        )
    if not session_bundle_hash:
        return refusal_contract_missing_bundle(
            "SessionSpec is missing contract_bundle_hash",
            relevant_ids={"save_id": save_id, "universe_id": str(spec.get("universe_id", ""))},
            path="$.contract_bundle_hash",
        )

    bundle_abs = _bundle_path(identity_path, bundle_ref)
    if not bundle_abs or not os.path.isfile(bundle_abs):
        return refusal_contract_missing_bundle(
            "Universe contract bundle sidecar is missing",
            relevant_ids={"save_id": save_id, "bundle_ref": norm(bundle_ref)},
            path="$.universe_identity.universe_contract_bundle_ref",
        )
    bundle_payload, bundle_error = read_json_object(bundle_abs)
    if bundle_error:
        return refusal_contract_missing_bundle(
            "Universe contract bundle sidecar is unreadable",
            relevant_ids={"save_id": save_id, "bundle_ref": norm(bundle_ref)},
            path="$.universe_identity.universe_contract_bundle_ref",
        )

    registry_payload, registry_error = load_semantic_contract_registry(repo_root)
    if registry_error:
        return refusal_contract_mismatch(
            "Semantic contract registry is missing or unreadable at runtime",
            relevant_ids={"registry_id": "dominium.registry.semantic_contracts"},
            path="$.semantic_contract_registry",
        )
    registry_errors = validate_semantic_contract_registry(registry_payload)
    if registry_errors:
        return refusal_contract_mismatch(
            "Semantic contract registry failed validation",
            relevant_ids={"registry_id": "dominium.registry.semantic_contracts"},
            path="$.semantic_contract_registry",
        )
    bundle_errors = validate_universe_contract_bundle(
        repo_root=repo_root,
        payload=bundle_payload,
        registry_payload=registry_payload,
    )
    if bundle_errors:
        return refusal_contract_mismatch(
            "Universe contract bundle does not match current semantic contract registry",
            relevant_ids={"save_id": save_id, "bundle_ref": norm(bundle_ref)},
            path="$.universe_contract_bundle",
        )

    actual_bundle_hash = bundle_hash(bundle_payload)
    if bundle_hash_expected != actual_bundle_hash or session_bundle_hash != actual_bundle_hash:
        return refusal_contract_mismatch(
            "Pinned universe contract bundle hash does not match identity/session metadata",
            relevant_ids={"save_id": save_id, "bundle_ref": norm(bundle_ref)},
            path="$.contract_bundle_hash",
        )

    proof_bundle = build_semantic_contract_proof_bundle(registry_payload, bundle_payload)
    session_registry_hash = str(spec.get("semantic_contract_registry_hash", "")).strip()
    proof_registry_hash = str(proof_bundle.get("semantic_contract_registry_hash", "")).strip()
    if replay_mode and not session_registry_hash:
        return refusal_contract_missing_bundle(
            "Replay requires SessionSpec.semantic_contract_registry_hash",
            relevant_ids={"save_id": save_id, "bundle_ref": norm(bundle_ref)},
            path="$.semantic_contract_registry_hash",
        )
    if session_registry_hash and session_registry_hash != proof_registry_hash:
        return refusal_contract_mismatch(
            "SessionSpec semantic contract registry hash does not match current runtime registry",
            relevant_ids={"save_id": save_id, "bundle_ref": norm(bundle_ref)},
            path="$.semantic_contract_registry_hash",
        )
    if replay_mode and session_registry_hash != proof_registry_hash:
        return refusal_contract_mismatch(
            "Replay refuses when semantic contract registry hash does not match the pinned universe contract bundle",
            relevant_ids={"save_id": save_id, "bundle_ref": norm(bundle_ref)},
            path="$.semantic_contract_registry_hash",
        )

    return {
        "result": "complete",
        "bundle_path": norm(os.path.relpath(bundle_abs, repo_root)),
        "universe_contract_bundle": dict(bundle_payload),
        "semantic_contract_registry": dict(registry_payload),
        "proof_bundle": dict(proof_bundle),
        "contract_bundle_hash": actual_bundle_hash,
        "semantic_contract_registry_hash": proof_registry_hash,
    }
