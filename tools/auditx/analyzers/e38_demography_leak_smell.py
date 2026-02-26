"""E38 demography leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E38_DEMOGRAPHY_LEAK_SMELL"
PROCESS_RUNTIME_PATH = "tools/xstack/sessionx/process_runtime.py"
OBSERVATION_PATH = "tools/xstack/sessionx/observation.py"
DOC_PATH = "docs/civilisation/DEMOGRAPHY_OPTIONALITY.md"


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
    for token in (
        "process.demography_tick",
        "refusal.civ.births_forbidden_by_law",
        "_demography_policy_rows(",
        "_birth_model_rows(",
        "_death_model_rows(",
    ):
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.demography_leak_smell",
                severity="RISK",
                confidence=0.9,
                file_path=PROCESS_RUNTIME_PATH,
                line=1,
                evidence=[
                    "Demography runtime missing required policy/refusal token.",
                    token,
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[
                    "INV-DEMOGRAPHY-POLICY-REGISTRY-DRIVEN",
                ],
                related_paths=[PROCESS_RUNTIME_PATH],
            )
        )

    observation_text = _read_text(repo_root, OBSERVATION_PATH)
    for token in (
        "_population_view(",
        "_population_quantization_step(",
        "population_estimate",
        "precision_mode",
    ):
        if token in observation_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.demography_leak_smell",
                severity="WARN",
                confidence=0.82,
                file_path=OBSERVATION_PATH,
                line=1,
                evidence=[
                    "Population observability path missing quantization token.",
                    token,
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[
                    "INV-DEMOGRAPHY-POLICY-REGISTRY-DRIVEN",
                ],
                related_paths=[OBSERVATION_PATH],
            )
        )

    if "population_exact" in observation_text and "if can_view_exact" not in observation_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.demography_leak_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=OBSERVATION_PATH,
                line=1,
                evidence=[
                    "population_exact appears without explicit entitlement/hidden-state guard.",
                ],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-DEMOGRAPHY-POLICY-REGISTRY-DRIVEN",
                ],
                related_paths=[OBSERVATION_PATH],
            )
        )

    docs_text = _read_text(repo_root, DOC_PATH)
    if not docs_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.demography_leak_smell",
                severity="WARN",
                confidence=0.7,
                file_path=DOC_PATH,
                line=1,
                evidence=[
                    "Demography doctrine document is missing.",
                    DOC_PATH,
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=[],
                related_paths=[DOC_PATH],
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
