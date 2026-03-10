"""E424 printf-style logging smell analyzer."""

from __future__ import annotations

import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E424_PRINTF_LOG_SMELL"
GUARDED_PATHS = (
    "src/server/net/loopback_transport.py",
    "src/server/runtime/tick_loop.py",
    "src/appshell/diag/diag_snapshot.py",
)
PRINT_RE = re.compile(r"\bprint\s*\(")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    for rel_path in GUARDED_PATHS:
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        if not PRINT_RE.search(text):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="appshell.printf_log_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["ad hoc print-style logging remains in a governed structured logging surface"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-PRINTF-LOGGING", "INV-LOG-ENGINE-ONLY"],
                related_paths=list(GUARDED_PATHS),
            )
        )
    return findings
