"""FAST test: AppShell wrapper outputs are stable across repeated runs."""

from __future__ import annotations


TEST_ID = "test_cross_platform_appshel_hash_match"
TEST_TAGS = ["fast", "appshell", "hash"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell0_testlib import appshell_surface_fingerprint

    first = appshell_surface_fingerprint(repo_root)
    second = appshell_surface_fingerprint(repo_root)
    if str(first.get("appshell_hash", "")) != str(second.get("appshell_hash", "")):
        return {"status": "fail", "message": "AppShell wrapper fingerprint drifted across repeated runs"}
    if list(first.get("rows") or []) != list(second.get("rows") or []):
        return {"status": "fail", "message": "AppShell wrapper outputs drifted across repeated runs"}
    return {"status": "pass", "message": "AppShell wrapper outputs remain hash-stable"}
