"""E506 unstructured user-facing error smell analyzer for DIST-5."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.dist.ux_smoke_common import ux_smoke_violations


ANALYZER_ID = "E506_UNSTRUCTURED_USER_FACING_ERROR_SMELL"
_RELEVANT_CODES = {
    "unstructured_user_facing_error",
    "status_payload_not_json",
    "status_payload_missing_summary",
}


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
                category="dist.unstructured_user_facing_error_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "data/audit/dist5_ux_smoke.json",
                evidence=[
                    code,
                    str(item.get("message", "")).strip() or "user-facing UX output is missing the structured public contract",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="NORMALIZE_USER_FACING_OUTPUT_STRUCTURE",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-REFUSALS-MUST-HAVE-REMEDIATION"],
                related_paths=[rel_path or "data/audit/dist5_ux_smoke.json", "tools/dist/ux_smoke_common.py"],
            )
        )
    return findings
