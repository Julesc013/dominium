"""E119 unlogged refusal smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E119_UNLOGGED_REFUSAL_SMELL"
WATCH_PREFIXES = (
    "control/control_plane_engine.py",
)

_ALLOWED_UNLOGGED_MARKERS = (
    "control_intent_id is required",
    "requested_action_id is required",
    "requested action is unknown",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_lines(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read().splitlines()
    except OSError:
        return []


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    rel_path = "control/control_plane_engine.py"
    lines = _read_lines(repo_root, rel_path)
    if not lines:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unlogged_refusal_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["missing control plane engine file"],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-DECISION-LOG-MANDATORY"],
                related_paths=[rel_path],
            )
        )
        return findings

    full_text = "\n".join(lines)
    for token in ("_write_decision_log(", "_decision_log_row(", "decision_log_ref"):
        if token in full_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unlogged_refusal_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=rel_path,
                line=1,
                evidence=["missing decision-log integration token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-DECISION-LOG-MANDATORY"],
                related_paths=[rel_path],
            )
        )

    for idx, line in enumerate(lines, start=1):
        token = str(line).strip()
        if '"result": "refused"' not in token:
            continue
        window_start = max(1, idx - 20)
        context = "\n".join(lines[window_start - 1 : idx])
        if "_finalize_refusal(" in context or "_write_decision_log(" in context:
            continue
        if any(marker in context for marker in _ALLOWED_UNLOGGED_MARKERS):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.unlogged_refusal_smell",
                severity="VIOLATION",
                confidence=0.9,
                file_path=rel_path,
                line=idx,
                evidence=["refused result path not obviously tied to decision log emission", token[:140]],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-DECISION-LOG-MANDATORY"],
                related_paths=[rel_path],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

