"""E298 unbudgeted process loop smell analyzer for PROC-9 envelope."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E298_UNBUDGETED_PROCESS_LOOP_SMELL"


class UnbudgetedProcessLoopSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    rel_path = "tools/process/tool_run_proc_stress.py"
    text = _read_text(repo_root, rel_path)
    if not text:
        return []
    required_tokens = (
        "max_micro_steps_per_tick",
        "max_total_tasks_per_tick",
        "deferred_task_count",
        "degrade.proc.cap_micro_steps",
    )
    missing = [token for token in required_tokens if token not in text]
    if not missing:
        return []
    findings.append(
        make_finding(
            analyzer_id=ANALYZER_ID,
            category="architecture.unbudgeted_process_loop_smell",
            severity="RISK",
            confidence=0.9,
            file_path=rel_path,
            line=1,
            evidence=[
                "PROC stress harness is missing deterministic budget/degrade token(s): {}".format(
                    ", ".join(missing)
                )
            ],
            suggested_classification="NEEDS_REVIEW",
            recommended_action="REWRITE",
            related_invariants=[
                "INV-PROC-BUDGETED",
            ],
            related_paths=[
                rel_path,
                "docs/audit/PROC9_RETRO_AUDIT.md",
            ],
        )
    )
    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
