"""E534 missing governance profile smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.governance.governance_model_common import RULE_PROFILE, governance_model_violations


ANALYZER_ID = "E534_MISSING_GOVERNANCE_PROFILE_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in governance_model_violations(repo_root):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() != RULE_PROFILE:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="governance.missing_governance_profile_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "data/governance/governance_profile.json",
                evidence=[
                    str(item.get("code", "")).strip() or "governance_profile_missing",
                    str(item.get("message", "")).strip() or "release artifacts are missing governance profile linkage",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="PUBLISH_GOVERNANCE_PROFILE_AND_RECORD_ITS_HASH_IN_RELEASE_INDEX_AND_BUNDLE_METADATA",
                related_invariants=[RULE_PROFILE],
                related_paths=[
                    rel_path or "data/governance/governance_profile.json",
                    "tools/release/update_model_common.py",
                    "tools/setup/setup_cli.py",
                ],
            )
        )
    return findings
