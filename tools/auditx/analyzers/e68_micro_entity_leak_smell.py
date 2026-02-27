"""E68 micro entity leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E68_MICRO_ENTITY_LEAK_SMELL"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
INSPECTION_OVERLAY_PATH = "src/client/interaction/inspection_overlays.py"
REQUIRED_RUNTIME_TOKENS = (
    "process.materialize_structure_roi",
    "process.dematerialize_structure_roi",
    "_augment_inspection_target_payload_for_materialization(",
    "epistemic_redaction",
    "visibility_level",
)
REQUIRED_OVERLAY_TOKENS = (
    "_materialization_overlay_payload(",
    "_has_materialized_micro_for_structure(",
    "hide_macro_ghost",
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
    overlay_text = _read_text(repo_root, INSPECTION_OVERLAY_PATH)
    if not runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.micro_entity_leak_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["process runtime file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-GLOBAL-MICRO-PARTS", "INV-MACRO-STOCK-CANONICAL"],
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
                    category="materials.micro_entity_leak_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=PROCESS_RUNTIME_PATH,
                    line=1,
                    evidence=["process runtime missing required materialization/epistemic token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-GLOBAL-MICRO-PARTS", "INV-MACRO-STOCK-CANONICAL"],
                    related_paths=[PROCESS_RUNTIME_PATH],
                )
            )

    if not overlay_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.micro_entity_leak_smell",
                severity="VIOLATION",
                confidence=0.92,
                file_path=INSPECTION_OVERLAY_PATH,
                line=1,
                evidence=["inspection overlay file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-GLOBAL-MICRO-PARTS"],
                related_paths=[INSPECTION_OVERLAY_PATH],
            )
        )
    else:
        for token in REQUIRED_OVERLAY_TOKENS:
            if token in overlay_text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.micro_entity_leak_smell",
                    severity="RISK",
                    confidence=0.83,
                    file_path=INSPECTION_OVERLAY_PATH,
                    line=1,
                    evidence=["inspection overlays missing required materialization visibility token", token],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-GLOBAL-MICRO-PARTS"],
                    related_paths=[INSPECTION_OVERLAY_PATH],
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

