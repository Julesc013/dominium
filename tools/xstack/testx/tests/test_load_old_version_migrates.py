"""FAST test: legacy artifacts migrate deterministically to current format."""

from __future__ import annotations


TEST_ID = "test_load_old_version_migrates"
TEST_TAGS = ["fast", "compat", "pack_compat2", "migration"]


def run(repo_root: str):
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
        loaded, meta, error = load_fixture(repo_root, "save_file", path, contract_hash="c" * 64)
        if error:
            return {"status": "fail", "message": "legacy save migration refused unexpectedly"}
        if str(loaded.get("format_version", "")).strip() != "2.0.0":
            return {"status": "fail", "message": "legacy save did not migrate to format_version 2.0.0"}
        if str(loaded.get("semantic_contract_bundle_hash", "")).strip() != "c" * 64:
            return {"status": "fail", "message": "migrated save missing semantic_contract_bundle_hash"}
        if not list(meta.get("migration_events") or []):
            return {"status": "fail", "message": "migration events were not logged"}
        if not list(loaded.get("migration_history") or []):
            return {"status": "fail", "message": "migration_history missing on migrated save"}
    finally:
        cleanup_temp_dir(temp_dir)
    return {"status": "pass", "message": "legacy save migrates deterministically"}
