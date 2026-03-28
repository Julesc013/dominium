"""E118 silent downgrade smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E118_SILENT_DOWNGRADE_SMELL"
WATCH_PREFIXES = (
    "control/control_plane_engine.py",
    "client/interaction/interaction_dispatch.py",
    "inspection/inspection_engine.py",
    "materials/materialization/materialization_engine.py",
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

    control_plane_rel = "control/control_plane_engine.py"
    control_plane_text = _read_text(repo_root, control_plane_rel)
    if not control_plane_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_downgrade_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=control_plane_rel,
                line=1,
                evidence=["missing control plane engine file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DOMAIN-DOWNGRADE-LOGIC"],
                related_paths=[control_plane_rel],
            )
        )
        return findings

    for token in ("negotiate_request(", "downgrade_entries", "_negotiation_downgrade_reasons("):
        if token in control_plane_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_downgrade_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=control_plane_rel,
                line=1,
                evidence=["missing downgrade audit token in control plane", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DOMAIN-DOWNGRADE-LOGIC", "INV-DECISION-LOG-MANDATORY"],
                related_paths=[control_plane_rel],
            )
        )

    for rel_path in (
        "inspection/inspection_engine.py",
        "materials/materialization/materialization_engine.py",
    ):
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.silent_downgrade_smell",
                    severity="RISK",
                    confidence=0.82,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing domain module file"],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-DOMAIN-DOWNGRADE-LOGIC"],
                    related_paths=[rel_path],
                )
            )
            continue
        if "negotiate_request(" in text and "downgrade_entries" in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_downgrade_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=rel_path,
                line=1,
                evidence=["domain downgrade path missing negotiation downgrade surface"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DOMAIN-DOWNGRADE-LOGIC"],
                related_paths=[rel_path, control_plane_rel],
            )
        )

    ui_rel = "client/interaction/interaction_dispatch.py"
    ui_text = _read_text(repo_root, ui_rel)
    if ui_text and ("_decision_log_ui_messages(" not in ui_text or "_read_decision_log_payload(" not in ui_text):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.silent_downgrade_smell",
                severity="RISK",
                confidence=0.84,
                file_path=ui_rel,
                line=1,
                evidence=["UI path does not appear to source downgrade messaging from decision log artifacts"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-DECISION-LOG-MANDATORY"],
                related_paths=[ui_rel, control_plane_rel],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

