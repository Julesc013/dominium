"""E431 wallclock polling smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E431_WALLCLOCK_POLLING_SMELL"
REQUIRED_TOKENS = {
    "docs/appshell/SUPERVISOR_MODEL.md": (
        "bounded polling iterations",
        "The supervisor never uses wall-clock timeouts.",
    ),
    "appshell/supervisor/supervisor_engine.py": (
        "STOP_POLL_ITERATIONS = 4",
        "for _ in range(STOP_POLL_ITERATIONS):",
        "poll_process(process)",
    ),
    "tools/appshell/appshell6_probe.py": (
        "for _ in range(4):",
        "invoke_supervisor_service_command(repo_root, \"launcher stop\")",
    ),
}
FORBIDDEN_TOKENS = {
    "appshell/supervisor/supervisor_engine.py": ("time.sleep(", "time.time(", "datetime.utcnow(", "perf_counter(", "sleep("),
    "tools/appshell/appshell6_probe.py": ("time.sleep(", "time.time(", "datetime.utcnow(", "perf_counter(", "sleep("),
}


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
    related_paths = sorted(set(REQUIRED_TOKENS.keys()) | set(FORBIDDEN_TOKENS.keys()))
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="appshell.supervisor.wallclock_polling_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required APPSHELL-6 bounded-polling surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-NO-WALLCLOCK-POLLING",
                    ],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="appshell.supervisor.wallclock_polling_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing APPSHELL-6 bounded-polling marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-NO-WALLCLOCK-POLLING",
                    ],
                    related_paths=related_paths,
                )
            )
    for rel_path, tokens in FORBIDDEN_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        found = [token for token in tokens if token in text]
        if found:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="appshell.supervisor.wallclock_polling_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["forbidden wall-clock polling token(s): {}".format(", ".join(found[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-NO-WALLCLOCK-POLLING",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
