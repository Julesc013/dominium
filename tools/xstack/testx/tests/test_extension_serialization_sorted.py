"""FAST test: canonical serialization sorts extension keys deterministically."""

from __future__ import annotations


TEST_ID = "test_extension_serialization_sorted"
TEST_TAGS = ["fast", "compat", "extensions"]


def run(repo_root: str):
    from tools.xstack.testx.tests.compat_sem2_testlib import ensure_repo_on_path

    ensure_repo_on_path(repo_root)

    from tools.xstack.compatx.canonical_json import canonical_json_text

    payload = {
        "extensions": {
            "official.test.z_key": 1,
            "official.test.a_key": 2,
        },
        "schema_version": "1.0.0",
    }
    text = canonical_json_text(payload)
    if text.find('"official.test.a_key"') > text.find('"official.test.z_key"'):
        return {"status": "fail", "message": "extension keys were not serialized in sorted order"}
    return {"status": "pass", "message": "canonical serialization sorts extension keys deterministically"}
