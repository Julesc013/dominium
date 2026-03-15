"""FAST test: trust verification fingerprints are stable across target labels for identical inputs."""

from __future__ import annotations


TEST_ID = "test_cross_platform_trust_verification_consistent"
TEST_TAGS = ["fast", "security", "trust", "cross-platform"]


def run(repo_root: str):
    from tools.xstack.testx.tests.trust_model_testlib import (
        fixture_hash,
        signature_row,
        trusted_root,
        verify_with_policy,
    )

    artifact_hash = fixture_hash()
    signature = signature_row(signed_hash=artifact_hash, valid=True)
    roots = [trusted_root()]
    results = []
    for _platform_tag in ("win64", "linux-x86_64", "macos-universal"):
        result = verify_with_policy(
            repo_root,
            content_hash=artifact_hash,
            trust_policy_id="trust.strict_ranked",
            signatures=[signature],
            trust_roots=roots,
        )
        results.append(str(result.get("deterministic_fingerprint", "")).strip())
    if len(set(results)) != 1:
        return {"status": "fail", "message": "trust verification fingerprint changed across identical platform-labeled runs"}
    return {"status": "pass", "message": "trust verification fingerprint is stable for identical inputs"}
