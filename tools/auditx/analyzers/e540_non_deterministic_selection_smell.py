"""E540 non-deterministic selection smell analyzer for RELEASE-INDEX-POLICY-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.release_index_policy_common import RULE_POLICY_DECLARED, release_index_policy_violations


ANALYZER_ID = "E540_NON_DETERMINISTIC_SELECTION_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in release_index_policy_violations(repo_root):
        item = dict(row or {})
        code = str(item.get("code", "")).strip()
        if code != "selection_nondeterministic":
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.non_deterministic_selection_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "data/audit/release_index_policy_report.json",
                evidence=[
                    code,
                    str(item.get("message", "")).strip() or "release-resolution selection drifted across identical runs",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="CANONICALIZE_COMPONENT_CANDIDATE_ORDER_AND_STABILIZE_TIE_BREAK_SELECTION",
                related_invariants=[RULE_POLICY_DECLARED],
                related_paths=[
                    rel_path or "data/audit/release_index_policy_report.json",
                    "src/release/update_resolver.py",
                    "tools/release/release_index_policy_common.py",
                ],
            )
        )
    return findings
