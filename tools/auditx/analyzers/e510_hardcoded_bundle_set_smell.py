"""E510 hardcoded bundle set smell analyzer for DIST-REFINE-1."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.install_profile_common import install_profile_violations


ANALYZER_ID = "E510_HARDCODED_BUNDLE_SET_SMELL"
_RULE_ID = "INV-NO-HARDCODED-BUNDLE-CONTENTS"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in install_profile_violations(repo_root):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() != _RULE_ID:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.hardcoded_bundle_set_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "data/registries/install_profile_registry.json",
                evidence=[
                    str(item.get("code", "")).strip() or "hardcoded_bundle_set",
                    str(item.get("message", "")).strip() or "bundle composition still depends on implicit full-bundle assumptions",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ROUTE_DIST_ASSEMBLY_THROUGH_INSTALL_PROFILE_RESOLUTION",
                related_invariants=[_RULE_ID],
                related_paths=[rel_path or "data/registries/install_profile_registry.json", "tools/release/install_profile_common.py"],
            )
        )
    return findings
