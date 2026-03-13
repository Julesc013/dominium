"""FAST test: PROD-GATE-0 report is deterministic."""

from __future__ import annotations


TEST_ID = "test_boot_matrix_tool_deterministic"
TEST_TAGS = ["fast", "mvp", "products", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.prod_gate0_testlib import build_report, canonical_report_text, load_report

    cached_report, error = load_report(repo_root, prefer_cached=True)
    if error:
        return {"status": "fail", "message": error}
    rebuilt_report = build_report(repo_root)
    if canonical_report_text(cached_report) != canonical_report_text(rebuilt_report):
        return {"status": "fail", "message": "product boot matrix report drifted across repeated deterministic builds"}
    return {"status": "pass", "message": "product boot matrix report is deterministic"}
