"""FAST test: virtual path listing is sorted deterministically."""

from __future__ import annotations

import os
import tempfile


TEST_ID = "test_vpath_list_sorted"
TEST_TAGS = ["fast", "appshell", "paths", "ordering"]


def run(repo_root: str):
    from tools.xstack.testx.tests.repo_layout0_testlib import load_vpath_module

    vpaths = load_vpath_module(repo_root)
    with tempfile.TemporaryDirectory(prefix="repo_layout0_list_") as temp_root:
        for name in ("zeta.json", "alpha.json", "mid.json"):
            with open(os.path.join(temp_root, name), "w", encoding="utf-8", newline="\n") as handle:
                handle.write("{}\n")
        context = {
            "result": "complete",
            "roots": {"VROOT_PACKS": temp_root},
            "search_roots": {"VROOT_PACKS": [temp_root]},
        }
        rows = vpaths.vpath_list("VROOT_PACKS", "", context)
    if rows != ["alpha.json", "mid.json", "zeta.json"]:
        return {"status": "fail", "message": "vpath_list ordering drifted"}
    return {"status": "pass", "message": "vpath_list ordering is deterministic"}
