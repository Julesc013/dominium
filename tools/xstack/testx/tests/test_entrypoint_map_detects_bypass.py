"""FAST test: repository inventory bypass detection catches product mains outside AppShell."""

from __future__ import annotations


TEST_ID = "test_entrypoint_map_detects_bypass"
TEST_TAGS = ["fast", "review", "inventory", "appshell"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.repo_review2_testlib import detect_bypass_in_fixture

    rows = detect_bypass_in_fixture()
    if not rows:
        return {"status": "fail", "message": "repository inventory bypass detection missed a synthetic server main() bypass"}
    first = dict(rows[0] or {})
    if str(first.get("path", "")).replace("\\", "/") != "server/server_main.py":
        return {"status": "fail", "message": "unexpected bypass path '{}'".format(str(first.get("path", "")).strip())}
    return {"status": "pass", "message": "repository inventory detects synthetic AppShell bypass entrypoints"}
