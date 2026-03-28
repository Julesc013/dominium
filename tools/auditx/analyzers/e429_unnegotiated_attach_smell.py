"""E429 unnegotiated IPC attach smell analyzer."""

from __future__ import annotations

import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from analyzers.base import make_finding
from tools.appshell.ipc_unify_common import ipc_unify_violations


ANALYZER_ID = "E429_UNNEGOTIATED_ATTACH_SMELL"


def run(graph, repo_root, changed_files=None):
    del graph, changed_files
    findings = []
    for row in ipc_unify_violations(repo_root):
        item = dict(row or {})
        rel_path = str(item.get("file_path", "")).replace("\\", "/")
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="appshell.ipc.unnegotiated_attach_smell",
                severity="RISK",
                confidence=0.98,
                file_path=rel_path,
                evidence=[
                    str(item.get("code", "")).strip() or "ipc_unify_violation",
                    str(item.get("message", "")).strip() or "canonical IPC negotiation discipline drift detected",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REGENERATE_AND_FIX_IPC_UNIFY",
                related_invariants=[str(item.get("rule_id", "")).strip() or "INV-IPC-REQUIRES-NEGOTIATION"],
                related_paths=[
                    rel_path or "data/audit/ipc_unify_report.json",
                    "tools/appshell/tool_run_ipc_unify.py",
                    "appshell/ipc/ipc_transport.py",
                    "compat/handshake/handshake_engine.py",
                ],
            )
        )
    return findings
