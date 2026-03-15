"""E530 missing guaranteed log smell analyzer for OBSERVABILITY-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.meta.observability_common import RULE_GUARANTEES, observability_violations


ANALYZER_ID = "E530_MISSING_GUARANTEED_LOG_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in observability_violations(repo_root):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() != RULE_GUARANTEES:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="observability.missing_guaranteed_log_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "data/registries/observability_guarantee_registry.json",
                evidence=[
                    str(item.get("code", "")).strip() or "missing_guaranteed_log",
                    str(item.get("message", "")).strip() or "guaranteed observability category drift detected",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DECLARE_AND_EMIT_THE_GUARANTEED_CATEGORY_THROUGH_THE_STRUCTURED_LOG_ENGINE",
                related_invariants=[RULE_GUARANTEES],
                related_paths=[rel_path or "data/registries/observability_guarantee_registry.json", "tools/meta/observability_common.py"],
            )
        )
    return findings
