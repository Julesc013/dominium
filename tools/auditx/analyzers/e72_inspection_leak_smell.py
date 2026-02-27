"""E72 inspection leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E72_INSPECTION_LEAK_SMELL"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
INSPECTION_ENGINE_PATH = "src/inspection/inspection_engine.py"
OVERLAY_PATH = "src/client/interaction/inspection_overlays.py"
REQUIRED_RUNTIME_TOKENS = (
    "process.inspect_generate_snapshot",
    "build_inspection_snapshot_artifact(",
    "_augment_inspection_target_payload_for_materialization(",
    "_augment_inspection_target_payload_for_maintenance(",
    "_augment_inspection_target_payload_for_commitment_reenactment(",
    "refusal.inspect.forbidden_by_law",
)
REQUIRED_ENGINE_TOKENS = (
    "visibility_level",
    "micro_allowed",
    "include_part_ids",
    "epistemic_redaction_level",
    "\"derived_only\": True",
)
REQUIRED_OVERLAY_TOKENS = (
    "inspection_snapshot",
    "diegetic",
    "epistemic",
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

    for rel_path, tokens in (
        (PROCESS_RUNTIME_PATH, REQUIRED_RUNTIME_TOKENS),
        (INSPECTION_ENGINE_PATH, REQUIRED_ENGINE_TOKENS),
        (OVERLAY_PATH, REQUIRED_OVERLAY_TOKENS),
    ):
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.inspection_leak_smell",
                    severity="VIOLATION",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["required MAT-9 inspection safety file missing"],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-TRUTH-LEAK-VIA-INSPECTION"],
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
                    category="materials.inspection_leak_smell",
                    severity="RISK",
                    confidence=0.86,
                    file_path=rel_path,
                    line=1,
                    evidence=["inspection path missing required epistemic safety token", token],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-NO-TRUTH-LEAK-VIA-INSPECTION"],
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

