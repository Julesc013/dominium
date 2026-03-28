"""E75 thrash smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E75_THRASH_SMELL"
MAT_SCALE_ENGINE_PATH = "materials/performance/mat_scale_engine.py"
STRESS_TOOL_PATH = "tools/materials/tool_run_stress.py"
REQUIRED_ENGINE_TOKENS = (
    "_inspection_cache_key(",
    "inspection_cache_summary",
    "\"hits\":",
    "\"misses\":",
    "cache_hit",
)
REQUIRED_TOOL_TOKENS = (
    "inspection_cache_hit_rate_permille",
    "stress_report",
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

    engine_text = _read_text(repo_root, MAT_SCALE_ENGINE_PATH)
    if not engine_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.thrash_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=MAT_SCALE_ENGINE_PATH,
                line=1,
                evidence=["MAT-10 cache-aware scale engine file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-DEGRADE-NOT-MELTDOWN"],
                related_paths=[MAT_SCALE_ENGINE_PATH],
            )
        )
    else:
        for token in REQUIRED_ENGINE_TOKENS:
            if token in engine_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.thrash_smell",
                    severity="RISK",
                    confidence=0.83,
                    file_path=MAT_SCALE_ENGINE_PATH,
                    line=1,
                    evidence=["MAT-10 cache/thrash token missing", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-DEGRADE-NOT-MELTDOWN"],
                    related_paths=[MAT_SCALE_ENGINE_PATH],
                )
            )

    tool_text = _read_text(repo_root, STRESS_TOOL_PATH)
    if not tool_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.thrash_smell",
                severity="RISK",
                confidence=0.9,
                file_path=STRESS_TOOL_PATH,
                line=1,
                evidence=["MAT-10 stress harness output path missing"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-DEGRADE-NOT-MELTDOWN"],
                related_paths=[STRESS_TOOL_PATH],
            )
        )
    else:
        for token in REQUIRED_TOOL_TOKENS:
            if token in tool_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.thrash_smell",
                    severity="RISK",
                    confidence=0.8,
                    file_path=STRESS_TOOL_PATH,
                    line=1,
                    evidence=["MAT-10 stress summary token missing", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-DEGRADE-NOT-MELTDOWN"],
                    related_paths=[STRESS_TOOL_PATH],
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
