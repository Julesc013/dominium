"""FAST test: disaster cleanup removes readonly schema files on Windows-safe paths."""

from __future__ import annotations

import os
import stat
import sys


TEST_ID = "test_disaster_cleanup_removes_readonly_schema"
TEST_TAGS = ["fast", "omega", "disaster", "cleanup"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.disaster_suite_common import _safe_rmtree

    output_root_abs = os.path.join(
        repo_root,
        "build",
        "tmp",
        "testx_disaster_cleanup_readonly_schema",
    )
    schema_root = os.path.join(output_root_abs, "fixture", "dist", "schema", "control")
    os.makedirs(schema_root, exist_ok=True)
    schema_path = os.path.join(schema_root, "budget_allocation_record.schema")
    with open(schema_path, "wb") as handle:
        handle.write(b"dominium-test-schema")
    try:
        os.chmod(schema_path, stat.S_IREAD)
    except OSError:
        pass
    _safe_rmtree(output_root_abs)
    if os.path.exists(output_root_abs):
        return {
            "status": "fail",
            "message": "disaster cleanup left readonly schema fixture behind",
        }
    return {
        "status": "pass",
        "message": "disaster cleanup removed readonly schema fixture successfully",
    }
