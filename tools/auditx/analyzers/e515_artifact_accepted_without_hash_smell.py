"""E515 artifact accepted without hash smell analyzer for TRUST-MODEL-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.security.trust_model_common import RULE_HASHES, trust_model_violations


ANALYZER_ID = "E515_ARTIFACT_ACCEPTED_WITHOUT_HASH_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in trust_model_violations(repo_root):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() != RULE_HASHES:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="security.artifact_accepted_without_hash_smell",
                severity="BLOCKER",
                confidence=0.99,
                file_path=rel_path or "security/trust/trust_verifier.py",
                evidence=[
                    str(item.get("code", "")).strip() or "hash_missing_not_refused",
                    str(item.get("message", "")).strip() or "artifact trust verification accepted or could accept an artifact without a canonical hash",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ROUTE_ARTIFACT_ACCEPTANCE_THROUGH_HASH_FIRST_VERIFICATION",
                related_invariants=[RULE_HASHES],
                related_paths=[rel_path or "security/trust/trust_verifier.py", "tools/security/trust_model_common.py"],
            )
        )
    return findings
