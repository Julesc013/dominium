"""FAST test: DIAG-0 bundles strip secret-like fields deterministically."""

from __future__ import annotations

import os


TEST_ID = "test_no_secrets_in_bundle"
TEST_TAGS = ["fast", "diag", "appshell"]


def run(repo_root: str):
    from tools.xstack.testx.tests.diag0_testlib import cleanup_temp_dir, capture_bundle, list_bundle_files, make_temp_dir

    temp_dir = make_temp_dir("diag0_secrets_")
    forbidden_tokens = (
        "super-secret-token",
        "top-secret-password",
        "credential-hidden",
        "machine-id-private",
        "private-signing-key",
        "private-key-material",
    )
    try:
        capture_bundle(repo_root, out_dir=temp_dir, include_views=True, inject_secret=True)
        for rel_path in list_bundle_files(temp_dir):
            abs_path = os.path.join(temp_dir, rel_path.replace("/", os.sep))
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
                text = handle.read()
            for token in forbidden_tokens:
                if token in text:
                    return {
                        "status": "fail",
                        "message": "bundle leaked a secret-like token via {}".format(rel_path),
                    }
    finally:
        cleanup_temp_dir(temp_dir)
    return {"status": "pass", "message": "repro bundle strips secret-like fields"}
