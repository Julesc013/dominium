"""E94 duplicate scheduler smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E94_DUPLICATE_SCHEDULER_SMELL"


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

    core_path = "core/schedule/schedule_engine.py"
    core_text = _read_text(repo_root, core_path)
    if not core_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.duplicate_scheduler_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=core_path,
                line=1,
                evidence=["missing core schedule substrate file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-ADHOC-SCHEDULERS"],
                related_paths=[core_path],
            )
        )
        return findings

    src_root = os.path.join(repo_root, "src")
    for root, _dirs, files in os.walk(src_root):
        for name in files:
            if not name.endswith(".py"):
                continue
            abs_path = os.path.join(root, name)
            rel_path = _norm(os.path.relpath(abs_path, repo_root))
            if rel_path.startswith(("src/core/schedule/", "src/core/")):
                continue
            text = _read_text(repo_root, rel_path)
            if not text:
                continue
            has_schedule_tokens = (
                "recurrence_rule" in text
                and "next_due_tick" in text
                and "scheduled_tick" in text
            )
            if not has_schedule_tokens:
                continue
            if "tick_schedules(" in text or "advance_schedule(" in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.duplicate_scheduler_smell",
                    severity="RISK",
                    confidence=0.88,
                    file_path=rel_path,
                    line=1,
                    evidence=["scheduler recurrence tokens detected outside schedule substrate"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-ADHOC-SCHEDULERS"],
                    related_paths=[rel_path, core_path],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
