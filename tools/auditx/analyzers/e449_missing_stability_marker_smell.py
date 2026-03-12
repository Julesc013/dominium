"""E449 missing stability marker smell analyzer."""

from __future__ import annotations

import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)

from analyzers.base import make_finding
from src.meta.stability import SCOPED_REGISTRY_PATHS, validate_scoped_registries


ANALYZER_ID = "E449_MISSING_STABILITY_MARKER_SMELL"
WATCH_PREFIXES = tuple(SCOPED_REGISTRY_PATHS)
RULE_IDS = (
    "INV-REGISTRY-ENTRIES-MUST-HAVE-STABILITY",
    "INV-STABLE-REQUIRES-CONTRACT-ID",
)


def _rule_id(error_code: str) -> str:
    if str(error_code) == "stable_requires_contract_id":
        return "INV-STABLE-REQUIRES-CONTRACT-ID"
    return "INV-REGISTRY-ENTRIES-MUST-HAVE-STABILITY"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = validate_scoped_registries(repo_root)
    for row in list(report.get("reports") or []):
        registry_report = dict(row or {})
        rel_path = str(registry_report.get("file_path", "")).replace("\\", "/")
        for error in list(registry_report.get("errors") or []):
            error_row = dict(error or {})
            message = str(error_row.get("message", "")).strip() or "stability validation failed"
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="meta.missing_stability_marker_smell",
                    severity="RISK",
                    confidence=0.94,
                    file_path=rel_path,
                    evidence=[message],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=[_rule_id(str(error_row.get("code", "")))],
                    related_paths=[rel_path],
                )
            )
    return findings
