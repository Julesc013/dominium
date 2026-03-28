"""FAST test: trust verification always requires a canonical hash."""

from __future__ import annotations


TEST_ID = "test_hash_verification_always_required"
TEST_TAGS = ["fast", "security", "trust", "hash"]


def run(repo_root: str):
    from security.trust import REFUSAL_TRUST_HASH_MISSING
    from tools.xstack.testx.tests.trust_model_testlib import trust_policy
    from security.trust import verify_artifact_trust, ARTIFACT_KIND_RELEASE_MANIFEST, DEFAULT_TRUST_POLICY_ID

    result = verify_artifact_trust(
        artifact_kind=ARTIFACT_KIND_RELEASE_MANIFEST,
        content_hash="",
        trust_policy_id=DEFAULT_TRUST_POLICY_ID,
        trust_policy=trust_policy(repo_root, DEFAULT_TRUST_POLICY_ID),
    )
    if str(result.get("refusal_code", "")).strip() != REFUSAL_TRUST_HASH_MISSING:
        return {"status": "fail", "message": "missing content hash must refuse with refusal.trust.hash_missing"}
    return {"status": "pass", "message": "hash verification is mandatory"}
