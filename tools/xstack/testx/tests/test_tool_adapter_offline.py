"""FAST test: dom subprocess adapters remain offline."""

from __future__ import annotations


TEST_ID = "test_tool_adapter_offline"
TEST_TAGS = ["fast", "tools", "appshell"]


def run(repo_root: str):
    from tools.xstack.testx.tests.tool_surface_testlib import dispatch_dom

    payload = dispatch_dom(repo_root, ["dom", "compat", "emit-descriptor", "--product-id", "client"])
    adapter_payload = dict(payload.get("payload") or {})
    if int(payload.get("exit_code", -1)) != 0:
        return {"status": "fail", "message": "wrapped compat descriptor tool did not complete cleanly"}
    if not bool(adapter_payload.get("offline_only", False)):
        return {"status": "fail", "message": "tool adapter did not declare offline execution"}
    if str(adapter_payload.get("stdout_kind", "")).strip() != "json":
        return {"status": "fail", "message": "compat descriptor adapter did not preserve JSON output shape"}
    return {"status": "pass", "message": "tool adapter remains offline and deterministic"}
