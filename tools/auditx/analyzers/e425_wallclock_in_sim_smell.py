"""E425 wallclock-in-simulation smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E425_WALLCLOCK_IN_SIM_SMELL"
GUARDED_PATHS = (
    "src/server/net/loopback_transport.py",
    "src/server/runtime/tick_loop.py",
    "src/appshell/logging/log_engine.py",
    "src/appshell/diag/diag_snapshot.py",
)
FORBIDDEN_TOKENS = (
    "datetime.utcnow(",
    "datetime.now(",
    "time.time(",
    "time.monotonic(",
    "time.perf_counter(",
)


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
        matched = [token for token in FORBIDDEN_TOKENS if token in text]
        if not matched:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="appshell.wallclock_in_sim_smell",
                severity="RISK",
                confidence=0.97,
                file_path=rel_path,
                line=1,
                evidence=["forbidden wallclock token(s): {}".format(", ".join(matched[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-WALLCLOCK-IN-SIM"],
                related_paths=list(GUARDED_PATHS),
            )
        )
    return findings
