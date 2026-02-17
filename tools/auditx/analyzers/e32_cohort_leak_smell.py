"""E32 Cohort leak smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E32_COHORT_LEAK_SMELL"
WATCH_PREFIXES = (
    "tools/xstack/sessionx/",
    "docs/civilisation/",
    "data/registries/",
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
    required_runtime_tokens = (
        "process.cohort_expand_to_micro",
        "process.cohort_collapse_from_micro",
        "refusal.civ.cohort_cross_shard_forbidden",
        "anonymous_micro_agents",
        "parent_cohort_id",
    )
    for token in required_runtime_tokens:
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.cohort_leak_smell",
                severity="RISK",
                confidence=0.88,
                file_path=runtime_rel,
                line=1,
                evidence=[
                    "Cohort refinement safety token missing from runtime path.",
                    token,
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[
                    "INV-COHORT-EXPAND-COLLAPSE-PROCESS-ONLY",
                    "INV-COHORT-MAPPING-POLICY-DECLARED",
                ],
                related_paths=[runtime_rel],
            )
        )

    mapping_registry_rel = "data/registries/cohort_mapping_policy_registry.json"
    mapping_registry_text = _read_text(repo_root, mapping_registry_rel)
    required_policy_tokens = (
        "cohort.map.default",
        "cohort.map.rank_strict",
        "anonymous_micro_agents",
        "identity_exposure",
    )
    for token in required_policy_tokens:
        if token in mapping_registry_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.cohort_leak_smell",
                severity="WARN",
                confidence=0.8,
                file_path=mapping_registry_rel,
                line=1,
                evidence=[
                    "Cohort mapping policy registry is missing expected epistemic safety token.",
                    token,
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[
                    "INV-COHORT-MAPPING-POLICY-DECLARED",
                ],
                related_paths=[mapping_registry_rel],
            )
        )

    docs_rel = "docs/civilisation/COHORT_MODEL.md"
    if not _read_text(repo_root, docs_rel):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.cohort_leak_smell",
                severity="WARN",
                confidence=0.72,
                file_path=docs_rel,
                line=1,
                evidence=[
                    "Cohort doctrine document is missing.",
                    docs_rel,
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=[],
                related_paths=[docs_rel],
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

