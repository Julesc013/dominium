"""FAST test: portable install root detection resolves governed virtual roots."""

from __future__ import annotations

import os
import tempfile


TEST_ID = "test_portable_root_detected"
TEST_TAGS = ["fast", "appshell", "paths", "portable"]


def run(repo_root: str):
    from tools.xstack.testx.tests.repo_layout0_testlib import make_portable_context

    with tempfile.TemporaryDirectory(prefix="repo_layout0_portable_") as temp_root:
        context = make_portable_context(repo_root, temp_root)
    install_root = os.path.join(temp_root, "portable")
    if str(context.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "portable vpath context did not resolve cleanly"}
    if str(context.get("resolution_source", "")).strip() != "portable_manifest":
        return {"status": "fail", "message": "portable vpath context did not use install.manifest adjacency"}
    roots = dict(context.get("roots") or {})
    if os.path.normcase(os.path.normpath(str(roots.get("VROOT_INSTALL", "")))) != os.path.normcase(os.path.normpath(install_root)):
        return {"status": "fail", "message": "portable install root drifted"}
    if os.path.normcase(os.path.normpath(str(roots.get("VROOT_PACKS", "")))) != os.path.normcase(os.path.normpath(os.path.join(install_root, "packs"))):
        return {"status": "fail", "message": "portable packs root did not derive from the install root"}
    return {"status": "pass", "message": "portable install root detection is governed by virtual paths"}
