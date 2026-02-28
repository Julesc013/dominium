"""E82 silent batch creation smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E82_SILENT_BATCH_CREATION_SMELL"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
PORT_ENGINE_PATH = "src/machines/port_engine.py"

REQUIRED_RUNTIME_TOKENS = (
    "process.port_extract_batch",
    "process.machine_operate",
    "event.batch_created",
    "_machine_output_batch_id(",
    "_machine_event_row(",
)

REQUIRED_ENGINE_TOKENS = (
    "extract_from_port(",
    "insert_into_port(",
    "normalize_port_row(",
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
                category="materials.silent_batch_creation_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["required ACT-4 machine/port file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-SILENT-BATCH-CREATION"],
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
                category="materials.silent_batch_creation_smell",
                severity="RISK",
                confidence=0.88,
                file_path=rel_path,
                line=1,
                evidence=["missing deterministic batch provenance token", token],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-SILENT-BATCH-CREATION"],
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
        rel_path=PROCESS_RUNTIME_PATH,
        tokens=REQUIRED_RUNTIME_TOKENS,
    )
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=PORT_ENGINE_PATH,
        tokens=REQUIRED_ENGINE_TOKENS,
    )
    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )

