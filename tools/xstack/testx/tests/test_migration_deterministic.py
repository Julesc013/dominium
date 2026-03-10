"""FAST test: repeated migration runs produce identical payloads and event logs."""

from __future__ import annotations


TEST_ID = "test_migration_deterministic"
TEST_TAGS = ["fast", "compat", "pack_compat2", "migration"]


def run(repo_root: str):
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.testx.tests.pack_compat2_testlib import (
        cleanup_temp_dir,
        ensure_repo_on_path,
        legacy_save_payload,
        load_fixture,
        make_temp_dir,
        write_fixture,
    )

    ensure_repo_on_path(repo_root)
    temp_dir = make_temp_dir()
    try:
        path = write_fixture(temp_dir, "save.legacy.json", legacy_save_payload())
        first_loaded, first_meta, first_error = load_fixture(repo_root, "save_file", path, contract_hash="e" * 64)
        second_loaded, second_meta, second_error = load_fixture(repo_root, "save_file", path, contract_hash="e" * 64)
        if first_error or second_error:
            return {"status": "fail", "message": "migration replay refused unexpectedly"}
        if canonical_sha256(first_loaded) != canonical_sha256(second_loaded):
            return {"status": "fail", "message": "migrated payload hash drifted across identical runs"}
        if canonical_sha256(dict(first_meta)) != canonical_sha256(dict(second_meta)):
            return {"status": "fail", "message": "migration metadata drifted across identical runs"}
    finally:
        cleanup_temp_dir(temp_dir)
    return {"status": "pass", "message": "migration runs are deterministic"}
