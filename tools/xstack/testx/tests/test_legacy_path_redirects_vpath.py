"""FAST test: legacy path redirects route through the virtual path layer."""

from __future__ import annotations

import os


TEST_ID = "test_legacy_path_redirects_vpath"
TEST_TAGS = ["fast", "paths", "vpath", "shims"]


def run(repo_root: str):
    from tools.xstack.testx.tests.repo_layout1_testlib import redirect_legacy

    legacy_pack_path = "data/packs/org.dominium.base.topology"
    redirected = redirect_legacy(repo_root, legacy_pack_path)
    if not bool(redirected.get("shim_applied", False)):
        return {"status": "fail", "message": "legacy data/packs path did not trigger the path shim"}
    if str(redirected.get("vroot_id", "")).strip() != "VROOT_PACKS":
        return {"status": "fail", "message": "legacy data/packs path did not resolve through VROOT_PACKS"}
    rewritten = str(redirected.get("rewritten_path", "")).replace("\\", "/")
    expected_path = os.path.join(repo_root, legacy_pack_path).replace("\\", "/")
    if rewritten != expected_path:
        return {"status": "fail", "message": "legacy data/packs path did not prefer the existing repo-local fallback"}
    if not os.path.isdir(str(redirected.get("rewritten_path", ""))):
        return {"status": "fail", "message": "legacy data/packs path did not resolve to an existing directory"}
    return {"status": "pass", "message": "legacy path redirects route through the governed virtual path layer"}
