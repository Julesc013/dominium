"""E122 silent fidelity downgrade smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E122_SILENT_FIDELITY_DOWNGRADE_SMELL"
WATCH_PREFIXES = (
    "src/control/fidelity/",
    "inspection/inspection_engine.py",
    "materials/materialization/materialization_engine.py",
    "materials/commitments/commitment_engine.py",
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

    fidelity_core_rel = "control/fidelity/fidelity_engine.py"
    fidelity_core_text = _read_text(repo_root, fidelity_core_rel)
    if not fidelity_core_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_fidelity_downgrade_smell",
                severity="VIOLATION",
                confidence=0.96,
                file_path=fidelity_core_rel,
                line=1,
                evidence=["missing fidelity engine"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-FIDELITY-USES-ENGINE"],
                related_paths=[fidelity_core_rel],
            )
        )
        return findings

    for token in ("def arbitrate_fidelity_requests(", "REFUSAL_CTRL_FIDELITY_DENIED", "decision_log_entries"):
        if token in fidelity_core_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_fidelity_downgrade_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=fidelity_core_rel,
                line=1,
                evidence=["fidelity engine missing required downgrade/refusal token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-FIDELITY-USES-ENGINE"],
                related_paths=[fidelity_core_rel],
            )
        )

    # Domain modules should use fidelity engine + expose allocation evidence.
    domain_expectations = {
        "inspection/inspection_engine.py": ("build_fidelity_request(", "arbitrate_fidelity_requests(", "fidelity_allocation"),
        "materials/materialization/materialization_engine.py": ("build_fidelity_request(", "arbitrate_fidelity_requests(", "fidelity_allocation"),
        "materials/commitments/commitment_engine.py": ("build_fidelity_request(", "arbitrate_fidelity_requests(", "fidelity_allocation"),
        "tools/xstack/sessionx/process_runtime.py": ("arbitrate_fidelity_requests(", "_append_fidelity_decision_entries(", "fidelity_decision_entries"),
    }
    for rel_path, required_tokens in sorted(domain_expectations.items(), key=lambda item: item[0]):
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.silent_fidelity_downgrade_smell",
                    severity="VIOLATION",
                    confidence=0.9,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing domain fidelity file"],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-FIDELITY-USES-ENGINE"],
                    related_paths=[rel_path],
                )
            )
            continue
        for token in required_tokens:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.silent_fidelity_downgrade_smell",
                    severity="VIOLATION",
                    confidence=0.9,
                    file_path=rel_path,
                    line=1,
                    evidence=["domain fidelity flow missing required token", token],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-FIDELITY-USES-ENGINE", "INV-NO-DOMAIN-FIDELITY-DOWNGRADE"],
                    related_paths=[rel_path, fidelity_core_rel],
                )
            )

    # Legacy inline downgrade patterns should not appear in domain files.
    legacy_patterns = (
        "if desired_fidelity == \"micro\" and micro_cost >",
        "if fidelity_achieved == \"meso\" and meso_cost >",
        "if desired_fidelity == \"micro\" and not micro_allowed",
    )
    for rel_path in (
        "inspection/inspection_engine.py",
        "materials/materialization/materialization_engine.py",
        "materials/commitments/commitment_engine.py",
    ):
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        for token in legacy_patterns:
            if token not in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.silent_fidelity_downgrade_smell",
                    severity="VIOLATION",
                    confidence=0.92,
                    file_path=rel_path,
                    line=1,
                    evidence=["legacy inline fidelity downgrade token detected", token],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-DOMAIN-FIDELITY-DOWNGRADE"],
                    related_paths=[rel_path],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

