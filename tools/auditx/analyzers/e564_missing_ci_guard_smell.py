"""E564 Xi-7 missing CI guard smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.xstack.ci.ci_common import build_ci_guard_violations


ANALYZER_ID = "E564_MISSING_CI_GUARD_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in build_ci_guard_violations(repo_root):
        item = dict(row or {})
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="ci.missing_ci_guard_smell",
                severity="RISK",
                confidence=0.99,
                file_path=str(item.get("file_path", "")),
                line=1,
                evidence=[
                    str(item.get("message", "")).strip() or "Xi-7 CI guard surface is incomplete",
                    "rule_id={}".format(str(item.get("rule_id", "")).strip()),
                    "code={}".format(str(item.get("code", "")).strip()),
                    str(item.get("remediation", "")).strip(),
                ],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-XSTACK-CI-MUST-RUN"],
                related_paths=[str(item.get("file_path", ""))],
            )
        )
    return findings
