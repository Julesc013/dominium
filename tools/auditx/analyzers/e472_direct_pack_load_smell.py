"""E472 direct pack load smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.entrypoint_unify_common import entrypoint_unify_violations


ANALYZER_ID = "E472_DIRECT_PACK_LOAD_SMELL"
WATCH_PREFIXES = (
    "src/server/",
    "tools/launcher/",
    "tools/setup/",
    "tools/release/",
)


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in entrypoint_unify_violations(repo_root):
        item = dict(row or {})
        if str(item.get("code", "")).strip() != "direct_pack_load":
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="appshell.direct_pack_load_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                evidence=[str(item.get("message", "")).strip() or "entrypoint performs pack validation outside the shared AppShell gate"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="USE_APPSHELL_PACK_GATE",
                related_invariants=["INV-NO-ADHOC-MAIN"],
                related_paths=[rel_path],
            )
        )
    return findings
