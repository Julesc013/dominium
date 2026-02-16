"""E20 Cosmetic semantics smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E20_COSMETIC_SEMANTICS_SMELL"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
FORBIDDEN_TOKENS = (
    "collision_layer",
    "shape_type",
    "shape_parameters",
    "body_move_attempt",
    "speed_scalar",
    "velocity_mm_per_tick",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        return ""
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    if not text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="representation.cosmetic_semantics_smell",
                severity="RISK",
                confidence=0.95,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["process runtime missing; cosmetic representation boundary cannot be validated."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-COSMETIC-SEMANTICS"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )
        return findings

    required_tokens = (
        "elif process_id == \"process.cosmetic_assign\":",
        "representation_state = _representation_state(policy_context)",
        "skip_state_log = True",
    )
    for token in required_tokens:
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="representation.cosmetic_semantics_smell",
                severity="RISK",
                confidence=0.86,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["Missing cosmetic representation token '{}'".format(token)],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-NO-COSMETIC-SEMANTICS"],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )

    for line_no, line in enumerate(text.splitlines(), start=1):
        lower = str(line).lower()
        if "cosmetic" not in lower:
            continue
        if "representation_state" in lower or "refusal.cosmetic" in lower:
            continue
        for token in FORBIDDEN_TOKENS:
            if token not in lower:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="representation.cosmetic_semantics_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=PROCESS_RUNTIME_PATH,
                    line=line_no,
                    evidence=[
                        "Cosmetic path references movement/collision token '{}'".format(token),
                        str(line).strip()[:200],
                    ],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-COSMETIC-SEMANTICS"],
                    related_paths=[PROCESS_RUNTIME_PATH],
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

