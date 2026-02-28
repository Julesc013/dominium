"""E83 port truth leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E83_PORT_TRUTH_LEAK_SMELL"
AFFORDANCE_PATH = "src/client/interaction/affordance_generator.py"
DISPATCH_PATH = "src/client/interaction/interaction_dispatch.py"
INSPECTION_ENGINE_PATH = "src/inspection/inspection_engine.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"

REQUIRED_SAFE_TOKENS = (
    "machine_provenance_events",
    "_events_for_target(",
    "process.port_insert_batch",
    "process.port_extract_batch",
    "_inspection_target_payload(",
)

FORBIDDEN_UI_TOKENS = (
    "truth_model",
    "truthmodel",
    "universe_state",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _append_missing_token_findings(findings, *, repo_root: str, rel_path: str, tokens, invariant_id: str) -> None:
    text = _read_text(repo_root, rel_path)
    if not text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.port_truth_leak_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=rel_path,
                line=1,
                evidence=["required ACT-4 integration file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=[invariant_id],
                related_paths=[rel_path],
            )
        )
        return
    for token in tokens:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.port_truth_leak_smell",
                severity="RISK",
                confidence=0.86,
                file_path=rel_path,
                line=1,
                evidence=["missing ACT-4 epistemic/process token", token],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[invariant_id],
                related_paths=[rel_path],
            )
        )


def _append_forbidden_ui_tokens(findings, *, repo_root: str, rel_path: str, invariant_id: str) -> None:
    text = _read_text(repo_root, rel_path)
    if not text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.port_truth_leak_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=rel_path,
                line=1,
                evidence=["required interaction UI file missing"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=[invariant_id],
                related_paths=[rel_path],
            )
        )
        return
    lowered = text.lower()
    for token in FORBIDDEN_UI_TOKENS:
        if token not in lowered:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.port_truth_leak_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=rel_path,
                line=1,
                evidence=["interaction layer references forbidden truth token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=[invariant_id],
                related_paths=[rel_path],
            )
        )


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=INSPECTION_ENGINE_PATH,
        tokens=("machine_provenance_events", "_events_for_target("),
        invariant_id="INV-PORTS-PROCESS-ONLY",
    )
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=PROCESS_RUNTIME_PATH,
        tokens=("process.port_insert_batch", "process.port_extract_batch", "_inspection_target_payload("),
        invariant_id="INV-PORTS-PROCESS-ONLY",
    )
    _append_missing_token_findings(
        findings,
        repo_root=repo_root,
        rel_path=INSPECTION_ENGINE_PATH,
        tokens=REQUIRED_SAFE_TOKENS[:2],
        invariant_id="INV-NO-SILENT-BATCH-CREATION",
    )
    _append_forbidden_ui_tokens(
        findings,
        repo_root=repo_root,
        rel_path=AFFORDANCE_PATH,
        invariant_id="INV-PORTS-PROCESS-ONLY",
    )
    _append_forbidden_ui_tokens(
        findings,
        repo_root=repo_root,
        rel_path=DISPATCH_PATH,
        invariant_id="INV-PORTS-PROCESS-ONLY",
    )
    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )

