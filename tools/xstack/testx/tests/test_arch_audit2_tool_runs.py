"""FAST test: ARCH-AUDIT-2 report builds and stays clean on the governed repository state."""

from __future__ import annotations


TEST_ID = "test_arch_audit2_tool_runs"
TEST_TAGS = ["fast", "audit", "architecture", "dist", "release"]


def run(repo_root: str):
    from tools.xstack.testx.tests.arch_audit2_testlib import build_report

    report = build_report(repo_root)
    if str(report.get("report_id", "")).strip() != "arch.audit.cross_layer.v1":
        return {"status": "fail", "message": "ARCH-AUDIT-2 report id is missing or invalid"}
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "ARCH-AUDIT-2 report is not clean"}
    expected_checks = {
        "dist_bundle_composition_scan",
        "update_model_scan",
        "trust_bypass_scan",
        "target_matrix_scan",
        "archive_determinism_scan",
    }
    if set(report.get("check_order") or []) != expected_checks:
        return {"status": "fail", "message": "ARCH-AUDIT-2 check order is incomplete"}
    return {"status": "pass", "message": "ARCH-AUDIT-2 report builds cleanly"}
