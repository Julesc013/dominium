"""STRICT test: domain report JSON/Markdown outputs are deterministic."""

from __future__ import annotations

import os
import sys


TEST_ID = "testx.domain.report_deterministic"
TEST_TAGS = ["strict", "smoke", "repox"]


def _read_text(path: str) -> str:
    return open(path, "r", encoding="utf-8").read()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.domain.tool_domain_report import build_domain_report

    a_json = "build/domain_report.a.json"
    a_md = "build/domain_report.a.md"
    b_json = "build/domain_report.b.json"
    b_md = "build/domain_report.b.md"
    first = build_domain_report(repo_root=repo_root, out_json_rel=a_json, out_md_rel=a_md)
    second = build_domain_report(repo_root=repo_root, out_json_rel=b_json, out_md_rel=b_md)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "domain report generation refused"}

    a_json_abs = os.path.join(repo_root, a_json.replace("/", os.sep))
    a_md_abs = os.path.join(repo_root, a_md.replace("/", os.sep))
    b_json_abs = os.path.join(repo_root, b_json.replace("/", os.sep))
    b_md_abs = os.path.join(repo_root, b_md.replace("/", os.sep))
    if _read_text(a_json_abs) != _read_text(b_json_abs):
        return {"status": "fail", "message": "domain report JSON outputs are not deterministic"}
    if _read_text(a_md_abs) != _read_text(b_md_abs):
        return {"status": "fail", "message": "domain report Markdown outputs are not deterministic"}
    return {"status": "pass", "message": "domain report determinism passed"}
