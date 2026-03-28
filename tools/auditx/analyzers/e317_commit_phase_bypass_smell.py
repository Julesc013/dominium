"""E317 commit-phase-bypass smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E317_COMMIT_PHASE_BYPASS_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e317_commit_phase_bypass_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "src/logic/eval/",
    "tools/xstack/sessionx/process_runtime.py",
)

_NON_COMMIT_PATHS = (
    "logic/eval/sense_engine.py",
    "logic/eval/compute_engine.py",
    "logic/eval/propagate_engine.py",
)
_COMMIT_ONLY_TOKENS = (
    "serialize_state(",
    "process_statevec_update(",
)


class CommitPhaseBypassSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _contains_call(text: str, token: str) -> bool:
    stem = str(token or "").strip()
    if stem.endswith("("):
        stem = stem[:-1]
    return bool(re.search(r"\b{}\s*\(".format(re.escape(stem)), str(text or "")))


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    commit_rel = "logic/eval/commit_engine.py"
    commit_text = _read_text(repo_root, commit_rel)
    for token in _COMMIT_ONLY_TOKENS:
        if _contains_call(commit_text, token):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.commit_phase_bypass_smell",
                severity="VIOLATION",
                confidence=0.91,
                file_path=commit_rel,
                line=1,
                evidence=["logic commit engine missing canonical state update token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-STATE-UPDATES-OUTSIDE-COMMIT"],
                related_paths=[commit_rel],
            )
        )

    for rel_path in _NON_COMMIT_PATHS:
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for token in _COMMIT_ONLY_TOKENS:
            if not _contains_call(text, token):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="logic.commit_phase_bypass_smell",
                    severity="VIOLATION",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["non-COMMIT logic phase contains state mutation token", token],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-STATE-UPDATES-OUTSIDE-COMMIT"],
                    related_paths=[rel_path, commit_rel],
                )
            )
            break

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _read_text(repo_root, runtime_rel)
    if '"process.statevec_update"' not in runtime_text or "process_statevec_update(" not in runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.commit_phase_bypass_smell",
                severity="RISK",
                confidence=0.84,
                file_path=runtime_rel,
                line=1,
                evidence=["runtime missing explicit LOGIC commit process registration/dispatch"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-STATE-UPDATES-OUTSIDE-COMMIT"],
                related_paths=[runtime_rel, commit_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
