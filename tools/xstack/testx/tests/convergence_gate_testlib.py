"""Helpers for CONVERGENCE-GATE-0 TestX coverage."""

from __future__ import annotations

import os

from tools.convergence.convergence_gate_common import (
    CONVERGENCE_FINAL_DOC_PATH,
    CONVERGENCE_FINAL_JSON_PATH,
    convergence_step_ids,
    load_convergence_report,
    run_convergence_gate,
)
from tools.xstack.compatx.canonical_json import canonical_json_text


def step_ids() -> list[str]:
    return convergence_step_ids(include_cross_platform=True)


def load_report(repo_root: str) -> tuple[dict, str]:
    report = load_convergence_report(repo_root)
    if not report:
        return {}, "convergence gate report missing"
    if str(report.get("result", "")).strip() != "complete":
        return report, "convergence gate report is not complete"
    return report, ""


def build_report(
    repo_root: str,
    *,
    selected_step_ids: list[str] | None = None,
    force_fail_step_id: str = "",
    out_root_rel: str = "build/tmp/testx_convergence_gate",
) -> dict:
    out_root = os.path.join(repo_root, out_root_rel.replace("/", os.sep))
    step_json_dir = os.path.join(out_root, "data", "audit", "convergence_steps").replace("\\", "/")
    step_doc_dir = os.path.join(out_root, "docs", "audit", "convergence_steps").replace("\\", "/")
    final_json_path = os.path.join(out_root, CONVERGENCE_FINAL_JSON_PATH.replace("/", os.sep)).replace("\\", "/")
    final_doc_path = os.path.join(out_root, CONVERGENCE_FINAL_DOC_PATH.replace("/", os.sep)).replace("\\", "/")
    return run_convergence_gate(
        repo_root,
        skip_cross_platform=True,
        prefer_cached_heavy=True,
        step_json_dir=step_json_dir,
        step_doc_dir=step_doc_dir,
        final_json_path=final_json_path,
        final_doc_path=final_doc_path,
        selected_step_ids=selected_step_ids or [],
        force_fail_step_id=force_fail_step_id,
        force_fail_message="forced failure for TestX",
    )


def canonical_report_text(report: dict) -> str:
    return canonical_json_text(report)
