"""E509 hardcoded bundle composition smell analyzer for COMPONENT-GRAPH-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.release.component_graph_common import component_graph_violations


ANALYZER_ID = "E509_HARDCODED_BUNDLE_COMPOSITION_SMELL"
_RULE_ID = "INV-NO-HARDCODED-COMPONENT-SETS"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in component_graph_violations(repo_root):
        item = dict(row or {})
        if str(item.get("rule_id", "")).strip() != _RULE_ID:
            continue
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.hardcoded_bundle_composition_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "data/registries/component_graph_registry.json",
                evidence=[
                    str(item.get("code", "")).strip() or "hardcoded_component_set",
                    str(item.get("message", "")).strip() or "bundle composition still depends on hardcoded release/dist assumptions",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ROUTE_BUNDLE_COMPOSITION_THROUGH_THE_COMPONENT_GRAPH_RESOLVER",
                related_invariants=[_RULE_ID],
                related_paths=[rel_path or "data/registries/component_graph_registry.json", "tools/release/component_graph_common.py"],
            )
        )
    return findings
