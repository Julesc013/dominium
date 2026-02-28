"""E121 plan bypass smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E121_PLAN_BYPASS_SMELL"
WATCH_PREFIXES = (
    "tools/xstack/sessionx/process_runtime.py",
    "src/client/interaction/inspection_overlays.py",
    "src/control/planning/plan_engine.py",
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
                category="architecture.plan_bypass_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=runtime_rel,
                line=1,
                evidence=["missing process runtime file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DIRECT-STRUCTURE-INSTALL"],
                related_paths=[runtime_rel],
            )
        )
        return findings

    for token in (
        'elif process_id == "process.plan_create":',
        'elif process_id == "process.plan_update_incremental":',
        'elif process_id == "process.plan_execute":',
        "create_plan_artifact(",
        "build_plan_execution_ir(",
        "update_plan_artifact_incremental(",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.plan_bypass_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=runtime_rel,
                line=1,
                evidence=["missing planning pipeline token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-DIRECT-STRUCTURE-INSTALL", "INV-GHOST-IS-DERIVED"],
                related_paths=[runtime_rel, "src/control/planning/plan_engine.py"],
            )
        )

    overlays_rel = "src/client/interaction/inspection_overlays.py"
    overlays_text = _read_text(repo_root, overlays_rel)
    if not overlays_text or "_plan_overlay_payload(" not in overlays_text or "\"plan_artifacts\"" not in overlays_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.plan_bypass_smell",
                severity="RISK",
                confidence=0.86,
                file_path=overlays_rel,
                line=1,
                evidence=["missing plan overlay integration for ghost derived visualization"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-GHOST-IS-DERIVED"],
                related_paths=[overlays_rel],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

