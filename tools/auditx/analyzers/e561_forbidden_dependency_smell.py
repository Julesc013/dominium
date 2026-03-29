"""E561 Xi-6 forbidden dependency smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.review.xi6_common import build_boundary_findings


ANALYZER_ID = "E561_FORBIDDEN_DEPENDENCY_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in build_boundary_findings(repo_root):
        item = dict(row or {})
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.forbidden_dependency_smell",
                severity="RISK",
                confidence=0.97,
                file_path=str(item.get("file_path", "")),
                line=int(item.get("line_number", 0) or 0),
                evidence=[
                    str(item.get("message", "")).strip() or "forbidden dependency detected",
                    "dependency={}".format(str(item.get("dependency_module_id", "")).strip()),
                    str(item.get("remediation", "")).strip(),
                ],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-MODULE-BOUNDARIES-RESPECTED"],
                related_paths=[str(item.get("file_path", ""))],
            )
        )
    return findings
