"""E123 unbounded fidelity cost smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E123_UNBOUNDED_COST_SMELL"
WATCH_PREFIXES = (
    "src/control/fidelity/",
    "src/inspection/inspection_engine.py",
    "src/materials/materialization/materialization_engine.py",
    "src/materials/commitments/commitment_engine.py",
    "tools/xstack/sessionx/process_runtime.py",
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

    fidelity_engine_rel = "src/control/fidelity/fidelity_engine.py"
    fidelity_engine_text = _read_text(repo_root, fidelity_engine_rel)
    required_engine_tokens = (
        "max_cost_units_per_tick",
        "remaining_total",
        "budget_allocation_records",
        "used_by_tick_subject",
    )
    if not fidelity_engine_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unbounded_cost_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=fidelity_engine_rel,
                line=1,
                evidence=["missing fidelity engine file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-FIDELITY-USES-ENGINE"],
                related_paths=[fidelity_engine_rel],
            )
        )
        return findings
    for token in required_engine_tokens:
        if token in fidelity_engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unbounded_cost_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=fidelity_engine_rel,
                line=1,
                evidence=["fidelity engine missing bounded-budget token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-FIDELITY-USES-ENGINE"],
                related_paths=[fidelity_engine_rel],
            )
        )

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    runtime_text = _read_text(repo_root, runtime_rel)
    if not runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unbounded_cost_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=runtime_rel,
                line=1,
                evidence=["missing process runtime file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-FIDELITY-USES-ENGINE"],
                related_paths=[runtime_rel],
            )
        )
        return findings

    runtime_required_tokens = (
        "inspection_runtime_budget_state",
        "materialization_runtime_budget_state",
        "reenactment_runtime_budget_state",
        "cost_allocated",
        "_append_fidelity_decision_entries(",
    )
    for token in runtime_required_tokens:
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unbounded_cost_smell",
                severity="VIOLATION",
                confidence=0.88,
                file_path=runtime_rel,
                line=1,
                evidence=["runtime fidelity integration missing bounded-budget token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-FIDELITY-USES-ENGINE"],
                related_paths=[runtime_rel, fidelity_engine_rel],
            )
        )

    for rel_path in (
        "src/inspection/inspection_engine.py",
        "src/materials/materialization/materialization_engine.py",
        "src/materials/commitments/commitment_engine.py",
    ):
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        if "max_cost_units" in text and "arbitrate_fidelity_requests(" not in text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.unbounded_cost_smell",
                    severity="VIOLATION",
                    confidence=0.9,
                    file_path=rel_path,
                    line=1,
                    evidence=["domain path references max_cost_units without fidelity engine arbitration"],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-FIDELITY-USES-ENGINE", "INV-NO-DOMAIN-FIDELITY-DOWNGRADE"],
                    related_paths=[rel_path, fidelity_engine_rel],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

