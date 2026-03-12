"""E469 unclassified module smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.review.repo_inventory_common import SCAN_ROOTS, load_or_run_inventory_report, unknown_inventory_entries


ANALYZER_ID = "E469_UNCLASSIFIED_MODULE_SMELL"
WATCH_PREFIXES = tuple(SCAN_ROOTS)
RULE_ID = "INV-REPO-INVENTORY-MUST-EXIST"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = load_or_run_inventory_report(repo_root, prefer_cached=True)
    if str(dict(report or {}).get("inventory_id", "")).strip() != "repo.inventory.v1":
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="review.unclassified_module_smell",
                severity="RISK",
                confidence=0.94,
                file_path="data/audit/repo_inventory.json",
                evidence=["repository inventory report is missing or invalid"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=[RULE_ID],
                related_paths=["data/audit/repo_inventory.json"],
            )
        )
        return findings
    for row in unknown_inventory_entries(report):
        item = dict(row or {})
        rel_path = str(item.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="review.unclassified_module_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                evidence=[
                    "module_name={}".format(str(item.get("module_name", "")).strip() or "<missing>"),
                    "responsibility={}".format(str(item.get("responsibility", "")).strip() or "<missing>"),
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="CLASSIFY",
                related_invariants=[RULE_ID],
                related_paths=[rel_path],
            )
        )
    return findings
