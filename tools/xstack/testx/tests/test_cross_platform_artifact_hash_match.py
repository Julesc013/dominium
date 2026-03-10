"""FAST test: fixed-format artifact hash remains stable across platforms."""

from __future__ import annotations


TEST_ID = "test_cross_platform_artifact_hash_match"
TEST_TAGS = ["fast", "compat", "pack_compat2", "cross_platform"]
EXPECTED_HASH = "f8de7baa2e95306dfa33fc6f835ffd5f48d07a3e410356d5e1fe7d6bec0b2eb9"


def run(repo_root: str):
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.testx.tests.pack_compat2_testlib import (
        cleanup_temp_dir,
        current_save_payload,
        ensure_repo_on_path,
        load_fixture,
        make_temp_dir,
        write_fixture,
    )

    ensure_repo_on_path(repo_root)
    temp_dir = make_temp_dir()
    try:
        payload = current_save_payload(
            repo_root,
            contract_hash="f" * 64,
            engine_version_created="0.0.0+build.cross_platform_fixture",
        )
        path = write_fixture(temp_dir, "save.current.cross_platform.json", payload)
        loaded, _meta, error = load_fixture(repo_root, "save_file", path, contract_hash="f" * 64)
        if error:
            return {"status": "fail", "message": "fixed-format save fixture refused unexpectedly"}
        actual_hash = canonical_sha256(loaded)
        if actual_hash != EXPECTED_HASH:
            return {
                "status": "fail",
                "message": "artifact hash mismatch: expected {} got {}".format(EXPECTED_HASH, actual_hash),
            }
    finally:
        cleanup_temp_dir(temp_dir)
    return {"status": "pass", "message": "fixed-format artifact hash matches canonical baseline"}
