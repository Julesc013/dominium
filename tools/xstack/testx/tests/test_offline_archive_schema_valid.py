"""FAST test: committed offline archive surfaces expose the expected schema ids and hashes."""

from __future__ import annotations


TEST_ID = "test_offline_archive_schema_valid"
TEST_TAGS = ["fast", "omega", "archive", "release"]


def run(repo_root: str):
    from tools.release.offline_archive_common import (
        OFFLINE_ARCHIVE_BASELINE_SCHEMA_ID,
        OFFLINE_ARCHIVE_REQUIRED_TAG,
        OFFLINE_ARCHIVE_VERIFY_SCHEMA_ID,
    )
    from tools.xstack.testx.tests.offline_archive_testlib import committed_baseline, committed_verify

    verify_payload = committed_verify(repo_root)
    baseline_payload = committed_baseline(repo_root)
    if str(verify_payload.get("schema_id", "")).strip() != OFFLINE_ARCHIVE_VERIFY_SCHEMA_ID:
        return {"status": "fail", "message": "offline archive verify schema_id drifted"}
    if str(baseline_payload.get("schema_id", "")).strip() != OFFLINE_ARCHIVE_BASELINE_SCHEMA_ID:
        return {"status": "fail", "message": "offline archive baseline schema_id drifted"}
    if str(baseline_payload.get("required_update_tag", "")).strip() != OFFLINE_ARCHIVE_REQUIRED_TAG:
        return {"status": "fail", "message": "offline archive baseline missing required update tag"}
    for field_name in ("archive_bundle_hash", "archive_record_hash", "archive_projection_hash", "deterministic_fingerprint"):
        if len(str(verify_payload.get(field_name, "")).strip()) != 64:
            return {"status": "fail", "message": "offline archive verify missing {}".format(field_name)}
    return {"status": "pass", "message": "offline archive committed surfaces expose the expected schemas and hashes"}
