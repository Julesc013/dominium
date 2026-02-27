"""E74 unbounded work smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E74_UNBOUNDED_WORK_SMELL"
TARGETS = (
    (
        "src/materials/performance/mat_scale_engine.py",
        (
            "DEFAULT_MAT_DEGRADATION_ORDER",
            "apply_mat_degradation_policy(",
            "max_solver_cost_units_per_tick",
            "max_inspection_cost_units_per_tick",
            "\"bounded\":",
        ),
    ),
    (
        "tools/materials/tool_run_stress.py",
        (
            "run_stress_simulation(",
            "stress_report",
            "degradation_event_count",
        ),
    ),
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

    for rel_path, tokens in TARGETS:
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.unbounded_work_smell",
                    severity="VIOLATION",
                    confidence=0.96,
                    file_path=rel_path,
                    line=1,
                    evidence=["required MAT-10 stress bounding file missing"],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-DEGRADE-NOT-MELTDOWN"],
                    related_paths=[rel_path],
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.unbounded_work_smell",
                    severity="RISK",
                    confidence=0.87,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing stress bounding token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-DEGRADE-NOT-MELTDOWN"],
                    related_paths=[rel_path],
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
