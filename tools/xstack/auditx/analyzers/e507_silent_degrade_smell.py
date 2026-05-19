"""E507 silent degrade smell analyzer for DIST-6."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(THIS_DIR)
for _repo_root_probe_depth in range(16):
    if os.path.exists(os.path.join(REPO_ROOT_HINT, "AGENTS.md")):
        break
    parent = os.path.dirname(REPO_ROOT_HINT)
    if parent == REPO_ROOT_HINT:
        REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
        break
    REPO_ROOT_HINT = parent
REPO_ROOT_HINT = os.path.normpath(REPO_ROOT_HINT)
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.dist.dist6_interop_common import version_interop_violations


ANALYZER_ID = "E507_SILENT_DEGRADE_SMELL"
_RELEVANT_CODES = {"silent_degrade_not_logged"}


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in version_interop_violations(repo_root):
        item = dict(row or {})
        code = str(item.get("code", "")).strip()
        if code not in _RELEVANT_CODES:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="dist.silent_degrade_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "docs/audit/DIST6_FINAL.md",
                evidence=[
                    code,
                    str(item.get("message", "")).strip() or "degrade path was not logged deterministically",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="LOG_INTEROP_DEGRADE_PATH",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-VERSION-INTEROP-MUST-PASS-BEFORE-DIST"],
                related_paths=[rel_path or "docs/audit/DIST6_FINAL.md", "tools/release/dist/dist6_interop_common.py"],
            )
        )
    return findings
