"""FAST test: DIST-2 forbidden file scan detects development payload."""

from __future__ import annotations

import os


TEST_ID = "test_forbidden_file_scan"
TEST_TAGS = ["fast", "dist", "release", "audit"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist2_testlib import scan_forbidden_distribution_files, temp_bundle_fixture

    with temp_bundle_fixture(repo_root) as root:
        target = os.path.join(root, "legacy_source.py")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("print('legacy')\n")
        rows = scan_forbidden_distribution_files(root)
    if not rows:
        return {"status": "fail", "message": "forbidden file scan missed a legacy source payload"}
    if str(rows[0].get("path", "")).strip() != "legacy_source.py":
        return {"status": "fail", "message": "forbidden file scan returned unstable ordering"}
    return {"status": "pass", "message": "forbidden file scan detects development payload deterministically"}
