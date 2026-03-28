"""E516 signature required but missing smell analyzer for TRUST-MODEL-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.security.trust_model_common import RULE_STRICT, trust_model_violations


ANALYZER_ID = "E516_SIGNATURE_REQUIRED_BUT_MISSING_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in trust_model_violations(repo_root):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() != RULE_STRICT:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="security.signature_required_but_missing_smell",
                severity="BLOCKER",
                confidence=0.99,
                file_path=rel_path or "security/trust/trust_verifier.py",
                evidence=[
                    str(item.get("code", "")).strip() or "strict_unsigned_not_refused",
                    str(item.get("message", "")).strip() or "strict trust policy is not enforcing required signatures deterministically",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REFUSE_UNSIGNED_OR_INVALID_ARTIFACTS_UNDER_STRICT_TRUST_POLICY",
                related_invariants=[RULE_STRICT],
                related_paths=[rel_path or "security/trust/trust_verifier.py", "tools/security/trust_model_common.py"],
            )
        )
    return findings
