"""FAST test: dom subprocess adapters use repo-relative virtual path conventions."""

from __future__ import annotations


TEST_ID = "test_tool_adapter_uses_virtual_paths"
TEST_TAGS = ["fast", "tools", "appshell"]


def run(repo_root: str):
    from tools.xstack.testx.tests.tool_surface_testlib import dispatch_dom

    payload = dispatch_dom(repo_root, ["dom", "compat", "emit-descriptor", "--product-id", "client"])
    adapter_payload = dict(payload.get("payload") or {})
    invocation_args = list(adapter_payload.get("invocation_args") or [])
    if adapter_payload.get("virtual_path_policy") != "repo_relative_cwd":
        return {"status": "fail", "message": "tool adapter did not declare repo-relative virtual path policy"}
    if "--repo-root" not in invocation_args or "." not in invocation_args:
        return {"status": "fail", "message": "tool adapter did not inject repo-relative --repo-root context"}
    if any(":\\" in str(token) for token in invocation_args):
        return {"status": "fail", "message": "tool adapter invocation leaked an absolute host path"}
    return {"status": "pass", "message": "tool adapter uses repo-relative virtual path arguments"}
