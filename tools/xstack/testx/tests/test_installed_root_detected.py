"""FAST test: installed registry root detection resolves governed virtual roots."""

from __future__ import annotations

import os
import tempfile


TEST_ID = "test_installed_root_detected"
TEST_TAGS = ["fast", "appshell", "paths", "installed"]


def run(repo_root: str):
    from tools.xstack.testx.tests.repo_layout0_testlib import make_installed_context

    with tempfile.TemporaryDirectory(prefix="repo_layout0_installed_") as temp_root:
        context = make_installed_context(repo_root, temp_root)
        install_root = os.path.join(temp_root, "installs", "primary")
        store_root = os.path.join(temp_root, "installs", "store")
    if str(context.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "installed vpath context did not resolve cleanly"}
    if str(context.get("resolution_source", "")).strip() not in {"cli_install_id", "installed_registry_match", "installed_registry_single"}:
        return {"status": "fail", "message": "installed vpath context did not use registry-backed install discovery"}
    roots = dict(context.get("roots") or {})
    if os.path.normcase(os.path.normpath(str(roots.get("VROOT_INSTALL", "")))) != os.path.normcase(os.path.normpath(install_root)):
        return {"status": "fail", "message": "installed install root drifted"}
    if os.path.normcase(os.path.normpath(str(roots.get("VROOT_STORE", "")))) != os.path.normcase(os.path.normpath(store_root)):
        return {"status": "fail", "message": "installed store root did not respect store_root_ref"}
    return {"status": "pass", "message": "installed root detection is governed by the install registry"}
