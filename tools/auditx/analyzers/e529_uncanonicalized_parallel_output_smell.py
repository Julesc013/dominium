"""E529 uncanonicalized parallel output smell analyzer for CONCURRENCY-CONTRACT-0."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.audit.arch_audit_common import scan_parallel_output_canonicalization


ANALYZER_ID = "E529_UNCANONICALIZED_PARALLEL_OUTPUT_SMELL"
RULE_ID = "INV-PARALLEL-DERIVED-MUST-CANONICALIZE"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    payload = scan_parallel_output_canonicalization(repo_root)
    findings = []
    for row in list(dict(payload or {}).get("blocking_findings") or []):
        item = dict(row or {})
        rel_path = str(item.get("path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="engine.uncanonicalized_parallel_output_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path or "appshell/supervisor/supervisor_engine.py",
                evidence=[
                    str(item.get("message", "")).strip() or "parallel output canonicalization violation detected",
                    str(item.get("snippet", "")).strip(),
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="CANONICALIZE_PARALLEL_OUTPUT_BEFORE_HASHING_OR_PERSISTENCE",
                related_invariants=[RULE_ID],
                related_paths=[rel_path or "appshell/supervisor/supervisor_engine.py", "engine/concurrency/canonical_merge.py"],
            )
        )
    return findings
