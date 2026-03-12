"""Helpers for TIME-ANCHOR-0 TestX coverage."""

from __future__ import annotations


def load_verify_report(repo_root: str) -> tuple[dict, str]:
    from tools.time.time_anchor_common import load_or_run_verify_report, verify_longrun_ticks, write_time_anchor_outputs

    report = load_or_run_verify_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        report = verify_longrun_ticks(repo_root)
        write_time_anchor_outputs(repo_root, verify_report=report)
    if str(report.get("result", "")).strip() != "complete":
        return report, "TIME-ANCHOR verify report is not complete"
    return report, ""


def load_compaction_report(repo_root: str) -> tuple[dict, str]:
    from tools.time.time_anchor_common import load_or_run_compaction_report, verify_compaction_anchor_alignment, write_time_anchor_outputs

    report = load_or_run_compaction_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        report = verify_compaction_anchor_alignment(repo_root)
        write_time_anchor_outputs(repo_root, compaction_report=report)
    if str(report.get("result", "")).strip() != "complete":
        return report, "TIME-ANCHOR compaction report is not complete"
    return report, ""
