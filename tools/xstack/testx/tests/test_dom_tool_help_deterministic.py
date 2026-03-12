"""FAST test: dom root help is deterministic."""

from __future__ import annotations


TEST_ID = "test_dom_tool_help_deterministic"
TEST_TAGS = ["fast", "tools", "appshell"]


def run(repo_root: str):
    from tools.xstack.testx.tests.tool_surface_testlib import dispatch_dom

    first = dispatch_dom(repo_root, ["dom"])
    second = dispatch_dom(repo_root, ["dom"])
    if dict(first) != dict(second):
        return {"status": "fail", "message": "dom help output drifted between repeated runs"}
    if str(first.get("dispatch_kind", "")).strip() != "text":
        return {"status": "fail", "message": "dom help did not return text output"}
    if "usage: dom <area> <command> [-- ...]" not in str(first.get("text", "")):
        return {"status": "fail", "message": "dom help did not declare the stable umbrella usage"}
    return {"status": "pass", "message": "dom help is deterministic"}
