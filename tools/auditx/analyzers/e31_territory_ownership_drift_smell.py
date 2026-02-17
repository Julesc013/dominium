"""E31 Territory ownership drift smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E31_TERRITORY_OWNERSHIP_DRIFT_SMELL"
WATCH_PREFIXES = (
    "tools/xstack/sessionx/",
    "schemas/",
    "docs/civilisation/",
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

    process_runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    process_runtime_text = _read_text(repo_root, process_runtime_rel)
    required_runtime_tokens = (
        "process.territory_claim",
        "process.territory_release",
        "\"owner_faction_id\"",
        "\"claim_status\"",
        "refusal.civ.claim_forbidden",
        "refusal.civ.territory_invalid",
    )
    for token in required_runtime_tokens:
        if token in process_runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.territory_ownership_drift",
                severity="RISK",
                confidence=0.91,
                file_path=process_runtime_rel,
                line=1,
                evidence=[
                    "Territory ownership enforcement token missing from CIV runtime path.",
                    token,
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-CIV-PROCESSES-ONLY-MUTATION"],
                related_paths=[process_runtime_rel],
            )
        )

    universe_schema_rel = "schemas/universe_state.schema.json"
    universe_schema_text = _read_text(repo_root, universe_schema_rel)
    required_schema_tokens = (
        "\"territory_assemblies\"",
        "\"owner_faction_id\"",
        "\"claim_status\"",
        "\"contested\"",
    )
    for token in required_schema_tokens:
        if token in universe_schema_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.territory_ownership_drift",
                severity="WARN",
                confidence=0.8,
                file_path=universe_schema_rel,
                line=1,
                evidence=[
                    "Universe state schema missing territory ownership token.",
                    token,
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-CIV-PROCESSES-ONLY-MUTATION"],
                related_paths=[universe_schema_rel],
            )
        )

    docs_rel = "docs/civilisation/TERRITORY_AND_CLAIMS.md"
    if not _read_text(repo_root, docs_rel):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.territory_ownership_drift",
                severity="WARN",
                confidence=0.7,
                file_path=docs_rel,
                line=1,
                evidence=[
                    "Territory doctrine document is missing.",
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

