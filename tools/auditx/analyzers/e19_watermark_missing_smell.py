"""E19 Watermark missing smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E19_WATERMARK_MISSING_SMELL"
OBSERVATION_PATH = "tools/xstack/sessionx/observation.py"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"


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

    observation_text = _read_text(repo_root, OBSERVATION_PATH)
    if not observation_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="watermark.missing_smell",
                severity="RISK",
                confidence=0.95,
                file_path=OBSERVATION_PATH,
                line=1,
                evidence=["observation kernel missing; observer watermark channel enforcement cannot be verified."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-WATERMARK-ENFORCED"],
                related_paths=[OBSERVATION_PATH],
            )
        )
        return findings

    observation_tokens = (
        "_observer_watermark_payload(",
        "ch.watermark.observer_mode",
        "refusal.ep.entitlement_missing",
    )
    for token in observation_tokens:
        if token in observation_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="watermark.missing_smell",
                severity="RISK",
                confidence=0.9,
                file_path=OBSERVATION_PATH,
                line=1,
                evidence=[
                    "Missing observer watermark enforcement token in Observation Kernel.",
                    token,
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-WATERMARK-ENFORCED"],
                related_paths=[OBSERVATION_PATH],
            )
        )

    process_runtime_text = _read_text(repo_root, PROCESS_RUNTIME_PATH)
    if not process_runtime_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="watermark.missing_smell",
                severity="WARN",
                confidence=0.85,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=["camera process runtime missing; view-mode watermark refusal path cannot be verified."],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-WATERMARK-ENFORCED"],
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

    runtime_tokens = (
        "refusal.view.watermark_required",
        "watermark_policy_id",
    )
    for token in runtime_tokens:
        if token in process_runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="watermark.missing_smell",
                severity="WARN",
                confidence=0.82,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=[
                    "Missing camera view watermark enforcement token in process runtime.",
                    token,
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-WATERMARK-ENFORCED"],
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
