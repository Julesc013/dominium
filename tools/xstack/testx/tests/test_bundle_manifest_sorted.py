"""FAST test: DIAG-0 bundle manifests keep a deterministic artifact order."""

from __future__ import annotations


TEST_ID = "test_bundle_manifest_sorted"
TEST_TAGS = ["fast", "diag", "appshell"]


def run(repo_root: str):
    from tools.xstack.testx.tests.diag0_testlib import cleanup_temp_dir, capture_bundle, load_json, make_temp_dir

    temp_dir = make_temp_dir("diag0_manifest_sorted_")
    try:
        capture = capture_bundle(repo_root, out_dir=temp_dir, include_views=True)
        manifest = load_json(str(capture.get("manifest_path", "")))
        included = list(manifest.get("included_artifacts") or [])
        if included != sorted(included):
            return {"status": "fail", "message": "included_artifacts is not sorted deterministically"}
        if len(included) != len(set(included)):
            return {"status": "fail", "message": "included_artifacts contains duplicate entries"}
    finally:
        cleanup_temp_dir(temp_dir)
    return {"status": "pass", "message": "repro bundle manifest ordering is deterministic"}
