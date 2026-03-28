"""E316 unmetered-logic-eval smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E316_UNMETERED_LOGIC_EVAL_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e316_unmetered_logic_eval_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "docs/logic/LOGIC_EVALUATION_ENGINE.md",
    "src/logic/eval/",
    "tools/xstack/sessionx/process_runtime.py",
)


class UnmeteredLogicEvalSmell:
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

    doc_rel = "docs/logic/LOGIC_EVALUATION_ENGINE.md"
    doc_text = _read_text(repo_root, doc_rel).lower()
    for token in ("instruction_units", "memory_units", "per-network", "throttle"):
        if token in doc_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unmetered_logic_eval_smell",
                severity="RISK",
                confidence=0.82,
                file_path=doc_rel,
                line=1,
                evidence=["logic evaluation doctrine missing budgeting token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-LOGIC-EVAL-BUDGETED"],
                related_paths=[doc_rel],
            )
        )

    compute_rel = "logic/eval/compute_engine.py"
    compute_text = _read_text(repo_root, compute_rel)
    for token in ("request_logic_element_compute(", "compute_budget_profile_registry_payload"):
        if token in compute_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unmetered_logic_eval_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=compute_rel,
                line=1,
                evidence=["logic compute path missing compute-budget hook", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-LOGIC-EVAL-BUDGETED"],
                related_paths=[compute_rel],
            )
        )

    engine_rel = "logic/eval/logic_eval_engine.py"
    engine_text = _read_text(repo_root, engine_rel)
    for token in ("evaluate_logic_compute_phase(", "logic_compute_throttle", "logic_throttle_event_rows"):
        if token in engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unmetered_logic_eval_smell",
                severity="RISK",
                confidence=0.87,
                file_path=engine_rel,
                line=1,
                evidence=["logic eval orchestration missing throttle/budget token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-LOGIC-EVAL-BUDGETED"],
                related_paths=[engine_rel, compute_rel],
            )
        )

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _read_text(repo_root, runtime_rel)
    for token in ('"process.logic_network_evaluate"', "process_logic_network_evaluate("):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.unmetered_logic_eval_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=runtime_rel,
                line=1,
                evidence=["runtime missing logic evaluation process dispatch", token],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-LOGIC-EVAL-BUDGETED"],
                related_paths=[runtime_rel, engine_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
