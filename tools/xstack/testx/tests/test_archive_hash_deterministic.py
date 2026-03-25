"""STRICT test: offline archive hashes remain deterministic across reruns."""

from __future__ import annotations


TEST_ID = "test_archive_hash_deterministic"
TEST_TAGS = ["strict", "omega", "archive", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.offline_archive_testlib import build_and_verify

    first_build, first_verify = build_and_verify(repo_root, "deterministic_a")
    second_build, second_verify = build_and_verify(repo_root, "deterministic_b")
    for field_name in ("archive_bundle_hash", "archive_record_hash", "archive_projection_hash"):
        if str(first_build.get(field_name, "")).strip() != str(second_build.get(field_name, "")).strip():
            return {"status": "fail", "message": "offline archive {} drifted across identical reruns".format(field_name)}
    if str(first_verify.get("deterministic_fingerprint", "")).strip() != str(second_verify.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "offline archive verify fingerprint drifted across identical reruns"}
    return {"status": "pass", "message": "offline archive hashes are deterministic across reruns"}
