"""FAST test: UNIVERSAL-ID0 print/diff tools produce deterministic output."""

from __future__ import annotations

import json


TEST_ID = "test_identity_tools_output_deterministic"
TEST_TAGS = ["fast", "meta", "identity", "tools"]


def run(repo_root: str):
    from tools.xstack.testx.tests.identity_testlib import diff_tool_outputs, print_tool_outputs, tool_output_hash

    print_first, print_second = print_tool_outputs(repo_root)
    if int(print_first.returncode or 0) != 0 or int(print_second.returncode or 0) != 0:
        return {"status": "fail", "message": "tool_print_identity must succeed on a governed artifact with an embedded identity block"}
    if print_first.stdout != print_second.stdout:
        return {"status": "fail", "message": "tool_print_identity output drifted across repeated runs"}
    diff_first, diff_second = diff_tool_outputs(repo_root)
    if int(diff_first.returncode or 0) != 0 or int(diff_second.returncode or 0) != 0:
        return {"status": "fail", "message": "tool_diff_identity must report no differences when comparing an artifact against itself"}
    if diff_first.stdout != diff_second.stdout:
        return {"status": "fail", "message": "tool_diff_identity output drifted across repeated runs"}
    diff_payload = json.loads(diff_first.stdout)
    if list(diff_payload.get("differences") or []):
        return {"status": "fail", "message": "tool_diff_identity reported differences for identical artifacts"}
    output_hash = tool_output_hash(repo_root)
    if len(output_hash) != 64:
        return {"status": "fail", "message": "identity tool output hash is not canonical sha256"}
    return {"status": "pass", "message": "identity print/diff tools are deterministic"}
