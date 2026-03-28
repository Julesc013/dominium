"""E116 macro behavior smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E116_MACRO_BEHAVIOR_SMELL"
WATCH_PREFIXES = (
    "tools/xstack/sessionx/process_runtime.py",
    "materials/construction/construction_engine.py",
    "control/ir/control_ir_programs.py",
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

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _read_text(repo_root, runtime_rel)
    if not runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.macro_behavior_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=runtime_rel,
                line=1,
                evidence=["missing process runtime file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-MACRO-BEHAVIOR-WITHOUT-IR"],
                related_paths=[runtime_rel],
            )
        )
        return findings

    required_runtime_tokens = (
        "build_blueprint_execution_ir(",
        "build_autopilot_stub_ir(",
        "build_ai_controller_stub_ir(",
        "compile_ir_program(",
    )
    for token in required_runtime_tokens:
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.macro_behavior_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=runtime_rel,
                line=1,
                evidence=["missing Control IR integration token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-MACRO-BEHAVIOR-WITHOUT-IR"],
                related_paths=[runtime_rel, "control/ir/control_ir_programs.py"],
            )
        )

    construction_rel = "materials/construction/construction_engine.py"
    construction_text = _read_text(repo_root, construction_rel)
    if construction_text and "tick_construction_projects(" in construction_text and "build_blueprint_execution_ir(" not in runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.macro_behavior_smell",
                severity="RISK",
                confidence=0.86,
                file_path=construction_rel,
                line=1,
                evidence=["construction macro flow present without visible runtime Control IR bridge"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-MACRO-BEHAVIOR-WITHOUT-IR"],
                related_paths=[construction_rel, runtime_rel],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

