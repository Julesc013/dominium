"""E482 install discovery bypass smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.install_discovery_common import install_discovery_violations


ANALYZER_ID = "E482_INSTALL_ROOT_HARDCODED_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in install_discovery_violations(repo_root):
        item = dict(row or {})
        rel_path = str(item.get("file_path", "")).strip().replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="install.install_root_hardcoded_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                evidence=[
                    str(item.get("code", "")).strip(),
                    str(item.get("message", "")).strip() or "install discovery drift detected",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ROUTE_THROUGH_INSTALL_DISCOVERY",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-INSTALL-DISCOVERY-REQUIRED"],
                related_paths=[rel_path, "lib/install/install_discovery_engine.py"],
            )
        )
    return findings
