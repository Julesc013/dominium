"""FAST test: disaster cleanup removes readonly Python bytecode on Windows-safe paths."""

from __future__ import annotations

import os
import stat
import sys


TEST_ID = "test_disaster_cleanup_removes_readonly_bytecode"
TEST_TAGS = ["fast", "omega", "disaster", "cleanup"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.mvp.disaster_suite_common import _safe_rmtree

    output_root_abs = os.path.join(
        repo_root,
        "build",
        "tmp",
        "testx_disaster_cleanup_readonly_bytecode",
    )
    pycache_root = os.path.join(output_root_abs, "fixture", "dist", "tools", "xstack", "packagingx", "__pycache__")
    os.makedirs(pycache_root, exist_ok=True)
    pyc_path = os.path.join(pycache_root, "__init__.cpython-313.pyc")
    with open(pyc_path, "wb") as handle:
        handle.write(b"dominium-test-bytecode")
    try:
        os.chmod(pyc_path, stat.S_IREAD)
    except OSError:
        pass
    _safe_rmtree(output_root_abs)
    if os.path.exists(output_root_abs):
        return {
            "status": "fail",
            "message": "disaster cleanup left readonly bytecode fixture behind",
        }
    return {
        "status": "pass",
        "message": "disaster cleanup removed readonly bytecode fixture successfully",
    }
