"""E517 hardcoded component set smell analyzer for ARCH-AUDIT-2."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.audit.arch_audit_common import build_arch_audit2_report, run_arch_audit


ANALYZER_ID = "E517_HARDCODED_COMPONENT_SET_SMELL"
RULE_ID = "INV-DIST-USES-COMPONENT-GRAPH"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = build_arch_audit2_report(run_arch_audit(repo_root))
    for row in list(report.get("blocking_findings") or []):
        item = dict(row or {})
        if str(item.get("category", "")).strip() != "dist_bundle_composition":
            continue
        rel_path = str(item.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.hardcoded_component_set_smell",
                severity="BLOCKER",
                confidence=0.99,
                file_path=rel_path or "tools/dist/dist_tree_common.py",
                evidence=[
                    str(item.get("message", "")).strip() or "distribution composition is not derived purely from the component graph",
                    str(item.get("snippet", "")).strip() or "component graph / install profile bypass",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ROUTE_DIST_COMPOSITION_THROUGH_COMPONENT_GRAPH_AND_INSTALL_PROFILE",
                related_invariants=[RULE_ID],
                related_paths=[rel_path or "tools/dist/dist_tree_common.py", "release/component_graph_resolver.py"],
            )
        )
    return findings
