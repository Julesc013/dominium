"""FAST test: current-version persistent artifacts load without migration."""

from __future__ import annotations


TEST_ID = "test_load_current_version"
TEST_TAGS = ["fast", "compat", "pack_compat2", "formats"]


def run(repo_root: str):
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
        path = write_fixture(temp_dir, "save.current.json", current_save_payload(repo_root))
        loaded, meta, error = load_fixture(repo_root, "save_file", path, contract_hash="b" * 64)
        if error:
            return {"status": "fail", "message": "current save refused unexpectedly"}
        if str(loaded.get("format_version", "")).strip() != "2.0.0":
            return {"status": "fail", "message": "current save format_version mismatch"}
        if list(meta.get("migration_events") or []):
            return {"status": "fail", "message": "current save triggered unexpected migrations"}
        if bool(meta.get("read_only_mode", False)):
            return {"status": "fail", "message": "current save opened in read-only mode unexpectedly"}
    finally:
        cleanup_temp_dir(temp_dir)
    return {"status": "pass", "message": "current-version save artifact loads without migration"}
