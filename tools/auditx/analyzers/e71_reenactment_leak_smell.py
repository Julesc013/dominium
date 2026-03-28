"""E71 reenactment leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E71_REENACTMENT_LEAK_SMELL"
COMMITMENT_ENGINE_PATH = "materials/commitments/commitment_engine.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
INSPECTION_OVERLAY_PATH = "client/interaction/inspection_overlays.py"
REQUIRED_ENGINE_TOKENS = (
    "REFUSAL_REENACTMENT_FORBIDDEN_BY_LAW",
    "\"derived_only\": True",
    "build_reenactment_artifact(",
)
REQUIRED_RUNTIME_TOKENS = (
    "process.reenactment_generate",
    "process.reenactment_play",
    "skip_state_log = True",
    "_augment_inspection_target_payload_for_commitment_reenactment(",
)
REQUIRED_OVERLAY_TOKENS = (
    "_commitment_reenactment_overlay_payload(",
    "diegetic_reenactment_summary",
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

    for rel_path, tokens, invariant in (
        (COMMITMENT_ENGINE_PATH, REQUIRED_ENGINE_TOKENS, "INV-REENACTMENT_DERIVED_ONLY"),
        (PROCESS_RUNTIME_PATH, REQUIRED_RUNTIME_TOKENS, "INV-REENACTMENT_DERIVED_ONLY"),
        (INSPECTION_OVERLAY_PATH, REQUIRED_OVERLAY_TOKENS, "INV-NO_SILENT_MACRO_CHANGE"),
    ):
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.reenactment_leak_smell",
                    severity="VIOLATION",
                    confidence=0.93,
                    file_path=rel_path,
                    line=1,
                    evidence=["required MAT-8 reenactment file missing"],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=[invariant],
                    related_paths=[rel_path],
                )
            )
            continue
        for token in tokens:
            if token in text:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.reenactment_leak_smell",
                    severity="RISK",
                    confidence=0.84,
                    file_path=rel_path,
                    line=1,
                    evidence=["reenactment file missing required privacy/derived token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[invariant],
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
