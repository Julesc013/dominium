"""FAST test: UNIVERSAL-ID0 canonical serialization is stable across key orderings."""

from __future__ import annotations


TEST_ID = "test_identity_serialization_canonical"
TEST_TAGS = ["fast", "meta", "identity", "determinism"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.identity_testlib import canonical_serialization_pair

    left, right, left_text, right_text = canonical_serialization_pair()
    if left != right:
        return {"status": "fail", "message": "canonicalized universal identity blocks drifted across equivalent inputs"}
    if left_text != right_text:
        return {"status": "fail", "message": "canonical JSON serialization drifted across equivalent universal identity inputs"}
    if str(left.get("deterministic_fingerprint", "")).strip() != str(right.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "universal identity deterministic_fingerprint drifted across equivalent inputs"}
    return {"status": "pass", "message": "universal identity serialization is canonical and deterministic"}
