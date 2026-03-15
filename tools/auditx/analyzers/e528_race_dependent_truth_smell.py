"""E528 race-dependent truth smell analyzer for CONCURRENCY-CONTRACT-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_parallel_truth, scan_truth_atomic_usage


ANALYZER_ID = "E528_RACE_DEPENDENT_TRUTH_SMELL"
RULE_ID = "INV-NO-PARALLEL-TRUTH-WITHOUT-SHARD-MERGE"


def _findings_from_scan(scan_payload: dict) -> list:
    findings = []
    for row in list(dict(scan_payload or {}).get("blocking_findings") or []):
        item = dict(row or {})
        rel_path = str(item.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="engine.race_dependent_truth_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "tools/xstack/sessionx/scheduler.py",
                evidence=[
                    str(item.get("message", "")).strip() or "truth concurrency violation detected",
                    str(item.get("snippet", "")).strip(),
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REMOVE_PARALLEL_TRUTH_WRITE_OR_ROUTE_THROUGH_DETERMINISTIC_SHARD_MERGE",
                related_invariants=[RULE_ID],
                related_paths=[rel_path or "tools/xstack/sessionx/scheduler.py"],
            )
        )
    return findings


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    findings.extend(_findings_from_scan(scan_parallel_truth(repo_root)))
    findings.extend(_findings_from_scan(scan_truth_atomic_usage(repo_root)))
    return findings
