"""E484 shim bypass smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.shim_coverage_common import build_shim_coverage_report


ANALYZER_ID = "E484_SHIM_BYPASS_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = build_shim_coverage_report(repo_root)
    for row in list(report.get("violations") or []):
        row_map = dict(row or {})
        if str(row_map.get("code", "")).strip() not in {"shim_integration_missing"}:
            continue
        rel_path = str(row_map.get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="compat.shim_bypass_smell",
                severity="RISK",
                confidence=0.94,
                file_path=rel_path,
                evidence=[
                    str(row_map.get("message", "")).strip() or "shim integration is incomplete",
                    "transitional shims must stay on the governed AppShell/vpath/validation path and must not bypass validation or negotiation",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ROUTE_THROUGH_GOVERNED_SHIM",
                related_invariants=[str(row_map.get("rule_id", "")).strip() or "INV-SHIMS-MUST-NOT-BYPASS-VALIDATION"],
                related_paths=[rel_path, "tools/release/shim_coverage_common.py"],
            )
        )
    return findings
