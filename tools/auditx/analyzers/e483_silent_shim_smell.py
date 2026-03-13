"""E483 silent shim smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.shim_coverage_common import build_shim_coverage_report


ANALYZER_ID = "E483_SILENT_SHIM_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = build_shim_coverage_report(repo_root)
    for row in list(report.get("violations") or []):
        row_map = dict(row or {})
        if str(row_map.get("code", "")).strip() != "shim_warning_missing":
            continue
        rel_path = str(row_map.get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="compat.silent_shim_smell",
                severity="RISK",
                confidence=0.93,
                file_path=rel_path,
                evidence=[
                    str(row_map.get("message", "")).strip() or "shim warning coverage is incomplete",
                    "transitional shims must emit deterministic deprecation warnings with replacement guidance",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="WIRE_SHIM_WARNING",
                related_invariants=["INV-SHIMS-MUST-LOG-DEPRECATION"],
                related_paths=[rel_path, "src/compat/shims/common.py"],
            )
        )
    return findings
