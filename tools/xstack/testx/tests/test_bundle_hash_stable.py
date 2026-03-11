"""FAST test: DIAG-0 capture emits a stable bundle hash across repeated runs."""

from __future__ import annotations


TEST_ID = "test_bundle_hash_stable"
TEST_TAGS = ["fast", "diag", "appshell"]


def run(repo_root: str):
    from tools.xstack.testx.tests.diag0_testlib import cleanup_temp_dir, capture_bundle, load_json, make_temp_dir

    first_dir = make_temp_dir("diag0_hash_a_")
    second_dir = make_temp_dir("diag0_hash_b_")
    try:
        first = capture_bundle(repo_root, out_dir=first_dir, include_views=True)
        second = capture_bundle(repo_root, out_dir=second_dir, include_views=True)
        if str(first.get("bundle_hash", "")) != str(second.get("bundle_hash", "")):
            return {"status": "fail", "message": "bundle hash drifted across identical captures"}
        first_index = load_json(str(first.get("bundle_index_path", "")))
        second_index = load_json(str(second.get("bundle_index_path", "")))
        if list(first_index.get("files") or []) != list(second_index.get("files") or []):
            return {"status": "fail", "message": "bundle index file rows drifted across identical captures"}
    finally:
        cleanup_temp_dir(first_dir)
        cleanup_temp_dir(second_dir)
    return {"status": "pass", "message": "repro bundle hash is stable across repeated captures"}
