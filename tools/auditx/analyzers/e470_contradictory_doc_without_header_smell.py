"""E470 contradictory doc without header smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.review.doc_inventory_common import contradictory_doc_header_issues, load_or_run_doc_inventory


ANALYZER_ID = "E470_CONTRADICTORY_DOC_WITHOUT_HEADER_SMELL"
WATCH_PREFIXES = ("docs/", "tools/review/", "data/audit/doc_inventory.json")
RULE_ID = "INV-SUPERSEDED-DOCS-MUST-LINK-REPLACEMENT"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = load_or_run_doc_inventory(repo_root, prefer_cached=True)
    if str(dict(report or {}).get("inventory_id", "")).strip() != "doc.inventory.v1":
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="docs.contradictory_doc_without_header_smell",
                severity="RISK",
                confidence=0.94,
                file_path="data/audit/doc_inventory.json",
                evidence=["documentation inventory report is missing or invalid"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[RULE_ID],
                related_paths=["data/audit/doc_inventory.json"],
            )
        )
        return findings
    for row in contradictory_doc_header_issues(report):
        item = dict(row or {})
        rel_path = str(item.get("path", "")).replace("\\", "/")
        replacement_doc = str(item.get("replacement_doc", "")).strip() or "<missing>"
        missing_headers = list(item.get("missing_headers") or [])
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="docs.contradictory_doc_without_header_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                evidence=[
                    "alignment_status=contradictory",
                    "replacement_doc={}".format(replacement_doc),
                    "missing_headers={}".format(",".join(missing_headers) or "<missing>"),
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ANNOTATE",
                related_invariants=[RULE_ID],
                related_paths=[rel_path],
            )
        )
    return findings
