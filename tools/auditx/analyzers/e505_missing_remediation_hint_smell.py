"""E505 missing remediation hint smell analyzer for DIST-5."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.dist.ux_smoke_common import ux_smoke_violations


ANALYZER_ID = "E505_MISSING_REMEDIATION_HINT_SMELL"
_RELEVANT_CODES = {"refusal_missing_remediation"}


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in ux_smoke_violations(repo_root):
        item = dict(row or {})
        code = str(item.get("code", "")).strip()
        if code not in _RELEVANT_CODES:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="dist.missing_remediation_hint_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "data/audit/dist5_ux_smoke.json",
                evidence=[
                    code,
                    str(item.get("message", "")).strip() or "user-facing refusal is missing a remediation hint",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_STABLE_REMEDIATION_HINT_TO_REFUSAL_SURFACE",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-REFUSALS-MUST-HAVE-REMEDIATION"],
                related_paths=[rel_path or "data/audit/dist5_ux_smoke.json", "tools/dist/ux_smoke_common.py"],
            )
        )
    return findings
