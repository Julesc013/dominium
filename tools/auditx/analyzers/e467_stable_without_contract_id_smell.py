"""E467 stable registry entry without contract id smell analyzer."""

from __future__ import annotations

import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)

from analyzers.base import make_finding
from meta.stability import ALL_REGISTRY_PATHS, validate_all_registries


ANALYZER_ID = "E467_STABLE_WITHOUT_CONTRACT_ID_SMELL"
WATCH_PREFIXES = tuple(ALL_REGISTRY_PATHS)
RULE_ID = "INV-STABLE-REQUIRES-CONTRACT-ID"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = validate_all_registries(repo_root)
    for row in list(report.get("reports") or []):
        registry_report = dict(row or {})
        rel_path = str(registry_report.get("file_path", "")).replace("\\", "/")
        for error in list(registry_report.get("errors") or []):
            error_row = dict(error or {})
            if str(error_row.get("code", "")).strip() != "stable_requires_contract_id":
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="meta.stable_without_contract_id_smell",
                    severity="RISK",
                    confidence=0.94,
                    file_path=rel_path,
                    evidence=[str(error_row.get("message", "")).strip()],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[RULE_ID],
                    related_paths=[rel_path],
                )
            )
    return findings
