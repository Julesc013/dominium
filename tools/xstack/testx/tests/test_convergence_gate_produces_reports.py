"""FAST test: convergence gate writes deterministic reports."""

from __future__ import annotations

import os


TEST_ID = "test_convergence_gate_produces_reports"
TEST_TAGS = ["fast", "convergence", "release"]


def run(repo_root: str):
    from tools.xstack.testx.tests.convergence_gate_testlib import build_report

    report = build_report(
        repo_root,
        selected_step_ids=["meta_stability", "time_anchor", "arch_audit"],
        out_root_rel="build/tmp/testx_convergence_gate_reports",
    )
    written = dict(report.get("written_outputs") or {})
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "subset convergence gate report did not complete"}
    final_json = os.path.join(repo_root, str(written.get("final_json_path", "")).replace("/", os.sep))
    final_doc = os.path.join(repo_root, str(written.get("final_doc_path", "")).replace("/", os.sep))
    if not os.path.isfile(final_json):
        return {"status": "fail", "message": "convergence final JSON report missing"}
    if not os.path.isfile(final_doc):
        return {"status": "fail", "message": "convergence final markdown report missing"}
    if len(list(report.get("step_outputs") or [])) != 3:
        return {"status": "fail", "message": "convergence subset did not write all step snapshots"}
    return {"status": "pass", "message": "convergence gate writes deterministic reports"}
