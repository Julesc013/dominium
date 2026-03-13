"""FAST test: virtual path resolution normalizes mixed separators deterministically."""

from __future__ import annotations

import os
import tempfile


TEST_ID = "test_vpath_resolve_normalizes_separators"
TEST_TAGS = ["fast", "appshell", "paths", "normalization"]


def run(repo_root: str):
    from tools.xstack.testx.tests.repo_layout0_testlib import load_vpath_module

    vpaths = load_vpath_module(repo_root)
    with tempfile.TemporaryDirectory(prefix="repo_layout0_normalize_") as temp_root:
        context = {
            "result": "complete",
            "roots": {"VROOT_PACKS": temp_root},
            "search_roots": {"VROOT_PACKS": [temp_root]},
        }
        resolved = vpaths.vpath_resolve("VROOT_PACKS", "nested\\child/more.json", context)
        expected = os.path.normpath(os.path.join(temp_root, "nested", "child", "more.json"))
    if os.path.normcase(resolved) != os.path.normcase(expected):
        return {"status": "fail", "message": "vpath_resolve did not normalize mixed separators"}
    return {"status": "pass", "message": "vpath_resolve normalizes separators deterministically"}
