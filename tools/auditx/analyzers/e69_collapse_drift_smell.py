"""E69 collapse drift smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E69_COLLAPSE_DRIFT_SMELL"
MATERIALIZATION_ENGINE_PATH = "materials/materialization/materialization_engine.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
REQUIRED_ENGINE_TOKENS = (
    "invariant_delta",
    "materialize_structure_roi(",
    "dematerialize_structure_roi(",
    "_mass_parts(",
)
REQUIRED_RUNTIME_TOKENS = (
    "inv.transition.expand_materialization",
    "inv.transition.collapse_materialization",
    "refusal.transition.invariant_violation",
    "exception.numeric_error_budget",
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

    engine_text = _read_text(repo_root, MATERIALIZATION_ENGINE_PATH)
    runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    if not engine_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.collapse_drift_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=MATERIALIZATION_ENGINE_PATH,
                line=1,
                evidence=["materialization engine file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-MATERIALIZATION-DETERMINISTIC"],
                related_paths=[MATERIALIZATION_ENGINE_PATH],
            )
        )
    else:
        for token in REQUIRED_ENGINE_TOKENS:
            if token in engine_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.collapse_drift_smell",
                    severity="RISK",
                    confidence=0.87,
                    file_path=MATERIALIZATION_ENGINE_PATH,
                    line=1,
                    evidence=["materialization engine missing collapse/expand invariant token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-MATERIALIZATION-DETERMINISTIC"],
                    related_paths=[MATERIALIZATION_ENGINE_PATH],
                )
            )

    if not runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.collapse_drift_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["process runtime file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-MATERIALIZATION-DETERMINISTIC"],
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
                    category="materials.collapse_drift_smell",
                    severity="RISK",
                    confidence=0.84,
                    file_path=PROCESS_RUNTIME_PATH,
                    line=1,
                    evidence=["process runtime missing collapse/expand drift check token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-MATERIALIZATION-DETERMINISTIC"],
                    related_paths=[PROCESS_RUNTIME_PATH],
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

