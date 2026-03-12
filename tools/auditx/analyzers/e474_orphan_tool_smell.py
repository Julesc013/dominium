"""E474 orphan tool smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)

from analyzers.base import make_finding
from src.tools import tool_surface_violations


ANALYZER_ID = "E474_ORPHAN_TOOL_SMELL"
RULE_IDS = ("INV-TOOLS-EXPOSED-VIA-REGISTRY", "INV-NO-ADHOC-TOOL-ENTRYPOINTS")


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in tool_surface_violations(repo_root):
        item = dict(row or {})
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="tools.orphan_tool_smell",
                severity="RISK",
                confidence=0.97,
                file_path=rel_path,
                evidence=[
                    "code={}".format(str(item.get("code", "")).strip() or "<missing>"),
                    str(item.get("message", "")).strip() or "tool surface drift detected",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="CONSOLIDATE",
                related_invariants=[rule for rule in RULE_IDS if rule == str(item.get("rule_id", "")).strip()] or list(RULE_IDS),
                related_paths=[rel_path or "data/registries/command_registry.json"],
            )
        )
    return findings
