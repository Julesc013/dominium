"""E30 Faction orphan smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E30_FACTION_ORPHAN_SMELL"
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
    required_process_tokens = (
        "_ensure_faction_assemblies(",
        "_find_faction(",
        "process.faction_create",
        "process.faction_dissolve",
        "process.affiliation_join",
        "process.affiliation_leave",
    )
    for token in required_process_tokens:
        if token in process_runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.faction_orphan_smell",
                severity="RISK",
                confidence=0.9,
                file_path=process_runtime_rel,
                line=1,
                evidence=[
                    "Faction/affiliation substrate token missing from process runtime.",
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
        "\"faction_assemblies\"",
        "\"affiliations\"",
        "\"territory_assemblies\"",
        "\"diplomatic_relations\"",
    )
    for token in required_schema_tokens:
        if token in universe_schema_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.faction_orphan_smell",
                severity="WARN",
                confidence=0.84,
                file_path=universe_schema_rel,
                line=1,
                evidence=[
                    "Universe state schema is missing CIV structural field token.",
                    token,
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=["INV-CIV-PROCESSES-ONLY-MUTATION"],
                related_paths=[universe_schema_rel],
            )
        )

    docs_rel = "docs/civilisation/FACTIONS_AND_AFFILIATION.md"
    if not _read_text(repo_root, docs_rel):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="civilisation.faction_orphan_smell",
                severity="WARN",
                confidence=0.72,
                file_path=docs_rel,
                line=1,
                evidence=[
                    "Faction doctrine document is missing.",
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

