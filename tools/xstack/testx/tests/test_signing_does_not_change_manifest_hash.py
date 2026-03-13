"""FAST test: optional signatures must not perturb manifest identity fields."""

from __future__ import annotations


TEST_ID = "test_signing_does_not_change_manifest_hash"
TEST_TAGS = ["fast", "release", "signing"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.release2_testlib import build_manifest_payload, release_fixture, signed_manifest_payload

    with release_fixture() as dist_root:
        unsigned = build_manifest_payload(dist_root)
        signed = signed_manifest_payload(dist_root)
    if str(unsigned.get("manifest_hash", "")) != str(signed.get("manifest_hash", "")):
        return {"status": "fail", "message": "manifest_hash changed when signatures were added"}
    if str(unsigned.get("deterministic_fingerprint", "")) != str(signed.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "deterministic_fingerprint changed when signatures were added"}
    return {"status": "pass", "message": "optional signatures do not change manifest identity fields"}
