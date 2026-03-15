"""Shared TRUST-MODEL-0 TestX helpers."""

from __future__ import annotations

from src.security.trust import (
    ARTIFACT_KIND_PACK,
    ARTIFACT_KIND_RELEASE_MANIFEST,
    DEFAULT_TRUST_POLICY_ID,
    TRUST_POLICY_STRICT,
    canonicalize_signature_record,
    load_trust_policy_registry,
    select_trust_policy,
    verify_artifact_trust,
)
from tools.security.trust_model_common import build_trust_model_report
from tools.xstack.compatx.canonical_json import canonical_sha256


def fixture_hash() -> str:
    return canonical_sha256({"artifact": "trust-model-fixture"})


def trusted_root(signer_id: str = "signer.fixture.official") -> dict:
    return {
        "signer_id": str(signer_id).strip(),
        "public_key_bytes": "mock-public-key:{}".format(str(signer_id).strip()),
        "trust_level_id": "official",
        "deterministic_fingerprint": "",
        "extensions": {"official.source": "TRUST-MODEL0-6"},
    }


def signature_row(*, signer_id: str = "signer.fixture.official", signed_hash: str = "", valid: bool = True) -> dict:
    artifact_hash = str(signed_hash or fixture_hash()).strip().lower()
    signature_id = "signature.{}.{}".format(str(signer_id).strip().replace(" ", "_") or "anonymous", artifact_hash[:16] or "unsigned")
    signature_bytes = canonical_sha256(
        {
            "scheme_id": "signature.mock_detached_hash.v1",
            "signature_id": signature_id,
            "signer_id": str(signer_id).strip(),
            "signed_hash": artifact_hash,
        }
    )
    return canonicalize_signature_record(
        {
            "signature_id": signature_id,
            "signer_id": str(signer_id).strip(),
            "signed_hash": artifact_hash,
            "signature_bytes": signature_bytes if valid else "invalid-signature-bytes",
            "extensions": {"scheme_id": "signature.mock_detached_hash.v1"},
        }
    )


def trust_policy(repo_root: str, trust_policy_id: str) -> dict:
    registry = load_trust_policy_registry(repo_root=repo_root)
    return select_trust_policy(registry, trust_policy_id=trust_policy_id)


def verify_with_policy(
    repo_root: str,
    *,
    artifact_kind: str = ARTIFACT_KIND_RELEASE_MANIFEST,
    content_hash: str = "",
    trust_policy_id: str = DEFAULT_TRUST_POLICY_ID,
    signatures: list[dict] | None = None,
    trust_roots: list[dict] | None = None,
) -> dict:
    policy = trust_policy(repo_root, trust_policy_id)
    return verify_artifact_trust(
        artifact_kind=artifact_kind,
        content_hash=str(content_hash or fixture_hash()).strip(),
        signatures=list(signatures or []),
        trust_policy_id=trust_policy_id,
        trust_policy=policy,
        trust_roots=list(trust_roots) if trust_roots is not None else None,
    )


def strict_unsigned(repo_root: str) -> dict:
    return verify_with_policy(repo_root, artifact_kind=ARTIFACT_KIND_PACK, trust_policy_id=TRUST_POLICY_STRICT, signatures=[], trust_roots=[trusted_root()])


def default_unsigned(repo_root: str) -> dict:
    return verify_with_policy(repo_root, artifact_kind=ARTIFACT_KIND_PACK, trust_policy_id=DEFAULT_TRUST_POLICY_ID, signatures=[], trust_roots=[trusted_root()])


def invalid_signature(repo_root: str) -> dict:
    payload_hash = fixture_hash()
    return verify_with_policy(
        repo_root,
        artifact_kind=ARTIFACT_KIND_RELEASE_MANIFEST,
        content_hash=payload_hash,
        trust_policy_id=TRUST_POLICY_STRICT,
        signatures=[signature_row(signed_hash=payload_hash, valid=False)],
        trust_roots=[trusted_root()],
    )


def build_report(repo_root: str) -> dict:
    return build_trust_model_report(repo_root)


__all__ = [
    "build_report",
    "default_unsigned",
    "fixture_hash",
    "invalid_signature",
    "signature_row",
    "strict_unsigned",
    "trust_policy",
    "trusted_root",
    "verify_with_policy",
]
