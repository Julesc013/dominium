"""E70 uncommitted macro change smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E70_UNCOMMITTED_MACRO_CHANGE_SMELL"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
COMMITMENT_ENGINE_PATH = "src/materials/commitments/commitment_engine.py"
REQUIRED_RUNTIME_TOKENS = (
    "_enforce_causality_commitment_requirement(",
    "resolve_causality_strictness_row(",
    "process.manifest_tick",
    "process.construction_project_tick",
    "process.maintenance_perform",
)
REQUIRED_ENGINE_TOKENS = (
    "REFUSAL_COMMITMENT_REQUIRED_MISSING",
    "strictness_requires_commitment(",
    "_MAJOR_CHANGE_PROCESS_IDS",
)


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

    runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    engine_text = _read_text(repo_root, COMMITMENT_ENGINE_PATH)
    if not runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.uncommitted_macro_change_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["process runtime file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO_SILENT_MACRO_CHANGE"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )
    else:
        for token in REQUIRED_RUNTIME_TOKENS:
            if token in runtime_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.uncommitted_macro_change_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=PROCESS_RUNTIME_PATH,
                    line=1,
                    evidence=["process runtime missing causality strictness enforcement token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO_SILENT_MACRO_CHANGE"],
                    related_paths=[PROCESS_RUNTIME_PATH],
                )
            )

    if not engine_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.uncommitted_macro_change_smell",
                severity="VIOLATION",
                confidence=0.91,
                file_path=COMMITMENT_ENGINE_PATH,
                line=1,
                evidence=["commitment engine file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO_SILENT_MACRO_CHANGE"],
                related_paths=[COMMITMENT_ENGINE_PATH],
            )
        )
    else:
        for token in REQUIRED_ENGINE_TOKENS:
            if token in engine_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.uncommitted_macro_change_smell",
                    severity="RISK",
                    confidence=0.82,
                    file_path=COMMITMENT_ENGINE_PATH,
                    line=1,
                    evidence=["commitment engine missing strictness requirement token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO_SILENT_MACRO_CHANGE"],
                    related_paths=[COMMITMENT_ENGINE_PATH],
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
