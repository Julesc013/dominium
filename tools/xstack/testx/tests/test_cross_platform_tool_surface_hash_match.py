"""FAST test: tool surface fingerprint matches the committed baseline report."""

from __future__ import annotations

import re


TEST_ID = "test_cross_platform_tool_surface_hash_match"
TEST_TAGS = ["fast", "tools", "appshell", "cross_platform"]


def run(repo_root: str):
    from tools.xstack.testx.tests.tool_surface_testlib import build_report

    report = build_report(repo_root)
    final_doc_path = "docs/audit/TOOL_SURFACE_FINAL.md"
    try:
        text = open(final_doc_path, "r", encoding="utf-8").read()
    except OSError:
        return {"status": "fail", "message": "tool surface final report is missing"}
    match = re.search(r"Surface fingerprint: `([A-Fa-f0-9]{64})`", text)
    if not match:
        return {"status": "fail", "message": "tool surface final report does not declare the surface fingerprint"}
    if str(report.get("surface_fingerprint", "")).strip() != match.group(1):
        return {"status": "fail", "message": "tool surface fingerprint drifted from the committed report"}
    return {"status": "pass", "message": "tool surface fingerprint matches the committed baseline"}
