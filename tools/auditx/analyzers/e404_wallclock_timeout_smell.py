"""E404 wallclock timeout smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E404_WALLCLOCK_TIMEOUT_SMELL"
REQUIRED_TOKENS = {
    "client/local_server/local_server_controller.py": (
        "LOCAL_READY_POLL_ITERATIONS",
        '"strategy": "bounded_poll_iterations"',
        "for attempt in range(1, LOCAL_READY_POLL_ITERATIONS + 1):",
        "accept_loopback_connection(",
    ),
    "tools/mvp/runtime_entry.py": (
        "--local-singleplayer",
        "start_local_singleplayer(",
    ),
    "docs/server/LOCAL_SINGLEPLAYER_MODEL.md": (
        "Ready detection must not use wall-clock timeouts.",
        "bounded polling iterations",
    ),
}
FORBIDDEN_TOKENS = {
    "client/local_server/local_server_controller.py": ("time.time(", "datetime.utcnow(", "perf_counter(", "time.sleep(", "sleep("),
    "tools/server/server_mvp1_probe.py": ("time.time(", "datetime.utcnow(", "perf_counter(", "time.sleep(", "sleep("),
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
                    category="server.local_singleplayer.wallclock_timeout_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required SERVER-MVP-1 local-start surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-NO-WALLCLOCK-TIMEOUTS-IN-BOOT"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="server.local_singleplayer.wallclock_timeout_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing local-singleplayer timeout marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-WALLCLOCK-TIMEOUTS-IN-BOOT"],
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
                    category="server.local_singleplayer.wallclock_timeout_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["forbidden wall-clock boot token(s): {}".format(", ".join(found[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NO-WALLCLOCK-TIMEOUTS-IN-BOOT"],
                    related_paths=related_paths,
                )
            )
    return findings
