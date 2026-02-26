"""E42 unaccounted conservation violation smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E42_UNACCOUNTED_VIOLATION_SMELL"
LEDGER_ENGINE_PATH = "src/reality/ledger/ledger_engine.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
DOC_PATH = "docs/reality/CONSERVATION_AND_EXCEPTIONS.md"


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

    ledger_text = _read_text(repo_root, LEDGER_ENGINE_PATH)
    for token in (
        "refusal.conservation_unaccounted",
        "record_unaccounted_delta(",
        "finalize_process_accounting(",
    ):
        if token in ledger_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reality.unaccounted_violation_smell",
                severity="RISK",
                confidence=0.9,
                file_path=LEDGER_ENGINE_PATH,
                line=1,
                evidence=[
                    "Ledger engine is missing required unaccounted violation token.",
                    token,
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[
                    "INV-CONSERVATION-CONTRACT-SET-REQUIRED",
                    "INV-NO-SILENT-VIOLATIONS",
                ],
                related_paths=[LEDGER_ENGINE_PATH],
            )
        )

    runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    for token in (
        "_record_unaccounted_conservation_delta(",
        "_finalize_conservation_process(",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reality.unaccounted_violation_smell",
                severity="WARN",
                confidence=0.82,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=[
                    "Process runtime is missing conservation accounting token.",
                    token,
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[
                    "INV-NO-SILENT-VIOLATIONS",
                ],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )

    if "CONSERVATION_VIOLATION" in runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reality.unaccounted_violation_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=[
                    "Legacy hardcoded conservation violation refusal detected.",
                ],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-NO-SILENT-VIOLATIONS",
                ],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )

    docs_text = _read_text(repo_root, DOC_PATH)
    if not docs_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="reality.unaccounted_violation_smell",
                severity="WARN",
                confidence=0.72,
                file_path=DOC_PATH,
                line=1,
                evidence=[
                    "Conservation doctrine document is missing.",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=[],
                related_paths=[DOC_PATH],
            )
        )

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )
