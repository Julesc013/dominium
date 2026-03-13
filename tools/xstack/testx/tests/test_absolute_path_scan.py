"""FAST test: DIST-2 absolute path scan detects host-path leaks."""

from __future__ import annotations

import os


TEST_ID = "test_absolute_path_scan"
TEST_TAGS = ["fast", "dist", "release", "audit"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist2_testlib import (
        scan_distribution_absolute_path_leaks,
        temp_bundle_fixture,
        write_json,
    )

    with temp_bundle_fixture(repo_root) as root:
        write_json(
            os.path.join(root, "install.manifest.json"),
            {"install_root": "C:/Users/Jules/Dominium"},
        )
        rows = scan_distribution_absolute_path_leaks(root)
    if not rows:
        return {"status": "fail", "message": "absolute path scan missed a Windows absolute path leak"}
    if str(rows[0].get("path", "")).strip() != "install.manifest.json":
        return {"status": "fail", "message": "absolute path scan returned unstable ordering"}
    return {"status": "pass", "message": "absolute path scan detects host-path leaks deterministically"}
