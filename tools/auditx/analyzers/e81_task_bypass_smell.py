"""E81 task bypass smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E81_TASK_BYPASS_SMELL"
DISPATCH_PATH = "client/interaction/interaction_dispatch.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
TASK_ENGINE_PATH = "interaction/task/task_engine.py"

REQUIRED_DISPATCH_TOKENS = (
    "resolve_task_type_for_completion_process(",
    "process.task_create",
    "process_id_to_execute",
    "surface_id",
)
REQUIRED_RUNTIME_TOKENS = (
    "process.task_create",
    "process.task_tick",
    "process.task_pause",
    "process.task_resume",
    "process.task_cancel",
    "pending_task_completion_intents",
)
REQUIRED_TASK_ENGINE_TOKENS = (
    "_completion_intent(",
    "process_id_to_execute",
    "task_completed",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _append_missing_token_findings(findings, *, repo_root: str, rel_path: str, tokens) -> None:
    text = _read_text(repo_root, rel_path)
    if not text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.task_bypass_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["required ACT-3 file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-TASKS-PROCESS-ONLY-MUTATION"],
                related_paths=[rel_path],
            )
        )
        return
    for token in tokens:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.task_bypass_smell",
                severity="RISK",
                confidence=0.86,
                file_path=rel_path,
                line=1,
                evidence=["missing task process-only token", token],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-TASKS-PROCESS-ONLY-MUTATION"],
                related_paths=[rel_path],
            )
        )


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=DISPATCH_PATH,
        tokens=REQUIRED_DISPATCH_TOKENS,
    )
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=PROCESS_RUNTIME_PATH,
        tokens=REQUIRED_RUNTIME_TOKENS,
    )
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=TASK_ENGINE_PATH,
        tokens=REQUIRED_TASK_ENGINE_TOKENS,
    )
    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )

