"""E16 Movement bypass smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E16_MOVEMENT_BYPASS_SMELL"
TARGET_PATH = "tools/xstack/sessionx/process_runtime.py"
REQUIRED_TOKENS = (
    "elif process_id == \"process.agent_move\":",
    "moved = _apply_body_move_attempt(",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    rel_path = _norm(TARGET_PATH)
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="movement.bypass_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["process runtime missing; movement process-only mutation guarantees cannot be verified."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-MOVE-USES-BODY_MOVE_ATTEMPT"],
                related_paths=[rel_path],
            )
        )
        return findings

    try:
        text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return findings

    for token in REQUIRED_TOKENS:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="movement.bypass_smell",
                severity="RISK",
                confidence=0.9,
                file_path=rel_path,
                line=1,
                evidence=[
                    "Missing deterministic movement token.",
                    token,
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-MOVE-USES-BODY_MOVE_ATTEMPT"],
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
