"""E388 missing migration plan smell analyzer for semantic contracts."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E388_MISSING_MIGRATION_PLAN_SMELL"
WATCH_PREFIXES = (
    "data/registries/semantic_contract_registry.json",
    "docs/contracts/SEMANTIC_CONTRACT_MODEL.md",
)
REGISTRY_REL = "data/registries/semantic_contract_registry.json"
DOC_REL = "docs/contracts/SEMANTIC_CONTRACT_MODEL.md"
REQUIRED_BREAKING_TOKENS = (
    "CompatX migration descriptor",
    "explicit migration tool or explicit refusal path",
    "regression lock update",
    "release notes",
)
REQUIRED_DOC_TOKENS = REQUIRED_BREAKING_TOKENS


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
    registry_path = os.path.join(repo_root, REGISTRY_REL.replace("/", os.sep))
    try:
        payload = json.load(open(registry_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        payload = {}
    rows = (((payload.get("record") or {}).get("contracts")) or []) if isinstance(payload, dict) else []
    for row in rows:
        if not isinstance(row, dict):
            continue
        contract_id = str(row.get("contract_id", "")).strip()
        breaking = row.get("breaking_change_requires")
        joined = " | ".join(str(item) for item in breaking) if isinstance(breaking, list) else ""
        missing = [token for token in REQUIRED_BREAKING_TOKENS if token not in joined]
        if not missing:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="compat.missing_migration_plan_smell",
                severity="RISK",
                confidence=0.95,
                file_path=REGISTRY_REL,
                line=1,
                evidence=["semantic contract '{}' missing migration-plan token(s): {}".format(contract_id, ", ".join(missing))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-UNVERSIONED-BEHAVIOR-CHANGE"],
                related_paths=[REGISTRY_REL, DOC_REL],
            )
        )

    doc_text = _read_text(repo_root, DOC_REL)
    missing_doc_tokens = [token for token in REQUIRED_DOC_TOKENS if token not in doc_text]
    if missing_doc_tokens:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="compat.missing_migration_plan_smell",
                severity="RISK",
                confidence=0.93,
                file_path=DOC_REL,
                line=1,
                evidence=["semantic contract doc missing migration-plan token(s): {}".format(", ".join(missing_doc_tokens))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-UNVERSIONED-BEHAVIOR-CHANGE"],
                related_paths=[REGISTRY_REL, DOC_REL],
            )
        )
    return findings
