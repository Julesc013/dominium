"""E565 Xi-8 repository structure drift smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.review.xi8_common import build_arch_graph_matches_repo_violations, build_repository_structure_violations


ANALYZER_ID = "E565_REPOSITORY_STRUCTURE_DRIFT_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in list(build_repository_structure_violations(repo_root)) + list(build_arch_graph_matches_repo_violations(repo_root)):
        item = dict(row or {})
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="repo.repository_structure_drift_smell",
                severity="RISK",
                confidence=0.99,
                file_path=str(item.get("file_path", "")),
                line=1,
                evidence=[
                    str(item.get("message", "")).strip() or "Xi-8 repository structure drift detected",
                    "rule_id={}".format(str(item.get("rule_id", "")).strip()),
                    "code={}".format(str(item.get("code", "")).strip()),
                    str(item.get("remediation", "")).strip(),
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-REPO-STRUCTURE-LOCKED"],
                related_paths=[str(item.get("file_path", ""))],
            )
        )
    return findings
