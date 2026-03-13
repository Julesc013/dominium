"""E485 standalone product boot failure smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.mvp.prod_gate0_common import product_boot_matrix_violations


ANALYZER_ID = "E485_PRODUCT_STANDALONE_FAILURE_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in product_boot_matrix_violations(repo_root):
        item = dict(row or {})
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.product_standalone_failure_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                evidence=[
                    str(item.get("code", "")).strip() or "product_boot_matrix_violation",
                    str(item.get("message", "")).strip() or "standalone product boot matrix drift detected",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REGENERATE_AND_FIX_PRODUCT_BOOT_MATRIX",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-PROD-GATE-0-MUST-PASS-BEFORE-RELEASE"],
                related_paths=[rel_path or "data/audit/product_boot_matrix.json", "tools/mvp/tool_run_product_boot_matrix.py"],
            )
        )
    return findings
