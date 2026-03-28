"""E80 task nondeterminism smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E80_TASK_NONDETERMINISM_SMELL"
TASK_ENGINE_PATH = "interaction/task/task_engine.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"

REQUIRED_TASK_TOKENS = (
    "def tick_tasks(",
    "dt_ticks",
    "fixed_point_add(",
    "sorted(",
    "process_id_to_execute",
)
FORBIDDEN_WALLCLOCK_TOKENS = (
    "time.time(",
    "datetime.",
    "perf_counter(",
    "monotonic(",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _append_missing_token_findings(findings, *, repo_root: str, rel_path: str, tokens, invariant_id: str) -> None:
    text = _read_text(repo_root, rel_path)
    if not text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.task_nondeterminism_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["required ACT-3 file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=[invariant_id],
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
                category="interaction.task_nondeterminism_smell",
                severity="RISK",
                confidence=0.86,
                file_path=rel_path,
                line=1,
                evidence=["missing deterministic task token", token],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[invariant_id],
                related_paths=[rel_path],
            )
        )


def _append_wallclock_findings(findings, *, repo_root: str, rel_path: str, invariant_id: str) -> None:
    text = _read_text(repo_root, rel_path)
    if not text:
        return
    for token in FORBIDDEN_WALLCLOCK_TOKENS:
        if token not in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="interaction.task_nondeterminism_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=rel_path,
                line=1,
                evidence=["wall-clock token used in task path", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=[invariant_id],
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
        rel_path=TASK_ENGINE_PATH,
        tokens=REQUIRED_TASK_TOKENS,
        invariant_id="INV-TASKS-PROCESS-ONLY-MUTATION",
    )
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=PROCESS_RUNTIME_PATH,
        tokens=("process.task_tick", "tick_tasks(", "dt_ticks", "pending_task_completion_intents"),
        invariant_id="INV-TASKS-PROCESS-ONLY-MUTATION",
    )
    _append_wallclock_findings(
        findings,
        repo_root=repo_root,
        rel_path=TASK_ENGINE_PATH,
        invariant_id="INV-NO-WALLCLOCK-IN-TASKS",
    )
    _append_wallclock_findings(
        findings,
        repo_root=repo_root,
        rel_path=PROCESS_RUNTIME_PATH,
        invariant_id="INV-NO-WALLCLOCK-IN-TASKS",
    )
    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )

