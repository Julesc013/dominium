"""E520 non-deterministic archive smell analyzer for ARCH-AUDIT-2."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.audit.arch_audit_common import build_arch_audit2_report, run_arch_audit


ANALYZER_ID = "E520_NON_DETERMINISTIC_ARCHIVE_SMELL"
RULE_ID = "INV-DIST-USES-COMPONENT-GRAPH"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    report = build_arch_audit2_report(run_arch_audit(repo_root))
    for row in list(report.get("blocking_findings") or []):
        item = dict(row or {})
        if str(item.get("category", "")).strip() != "archive_determinism":
            continue
        rel_path = str(item.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="release.non_deterministic_archive_smell",
                severity="BLOCKER",
                confidence=0.98,
                file_path=rel_path or "tools/dist",
                evidence=[
                    str(item.get("message", "")).strip() or "archive generation mixes timestamp-bearing metadata into governed distribution tooling",
                    str(item.get("snippet", "")).strip() or "archive/timestamp coupling",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REMOVE_TIMESTAMP_AND_MTIME_DEPENDENCE_FROM_ARCHIVE_TOOLING",
                related_invariants=[RULE_ID],
                related_paths=[rel_path or "tools/dist", "tools/release"],
            )
        )
    return findings
