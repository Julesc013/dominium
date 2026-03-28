"""FAST test: future-format artifacts open in read-only mode when explicitly allowed."""

from __future__ import annotations


TEST_ID = "test_load_future_version_read_only"
TEST_TAGS = ["fast", "compat", "pack_compat2", "readonly"]


def run(repo_root: str):
    from compat import READ_ONLY_LAW_PROFILE_ID
    from tools.xstack.testx.tests.pack_compat2_testlib import (
        cleanup_temp_dir,
        ensure_repo_on_path,
        future_save_payload,
        load_fixture,
        make_temp_dir,
        write_fixture,
    )

    ensure_repo_on_path(repo_root)
    temp_dir = make_temp_dir()
    try:
        path = write_fixture(temp_dir, "save.future.json", future_save_payload(repo_root, contract_hash="d" * 64))
        loaded, meta, error = load_fixture(
            repo_root,
            "save_file",
            path,
            contract_hash="d" * 64,
            allow_read_only=True,
        )
        if error:
            return {"status": "fail", "message": "future save did not open in read-only mode"}
        if not bool(meta.get("read_only_applied", False)):
            return {"status": "fail", "message": "future save did not negotiate read-only mode"}
        if str(meta.get("law_profile_id_override", "")).strip() != READ_ONLY_LAW_PROFILE_ID:
            return {"status": "fail", "message": "read-only law profile override missing"}
        if str(loaded.get("format_version", "")).strip() != "9.0.0":
            return {"status": "fail", "message": "future save format_version changed unexpectedly"}
    finally:
        cleanup_temp_dir(temp_dir)
    return {"status": "pass", "message": "future save falls back to read-only mode deterministically"}
