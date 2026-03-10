"""E402 wallclock tick smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E402_WALLCLOCK_TICK_SMELL"
REQUIRED_TOKENS = {
    "src/server/runtime/tick_loop.py": (
        "advance_authoritative_tick(",
        "proof_anchor_interval_ticks",
        "build_server_proof_anchor(",
        "run_server_ticks(",
    ),
    "tools/server/tool_replay_server_window.py": (
        "Verify SERVER-MVP-0 deterministic tick, loopback, and proof-anchor replay.",
        "verify_server_window_replay(",
    ),
    "docs/server/SERVER_MVP_BASELINE.md": (
        "simulation time advances only through canonical ticks",
        "wall-clock is forbidden for authoritative scheduling",
        "proof anchors are emitted every configured `proof_anchor_interval_ticks`",
    ),
}
FORBIDDEN_TOKENS = {
    "src/server/runtime/tick_loop.py": ("time.time(", "datetime.utcnow(", "perf_counter(", "time.sleep(", "sleep("),
    "tools/server/server_mvp0_probe.py": ("time.time(", "datetime.utcnow(", "perf_counter(", "time.sleep(", "sleep("),
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
                    category="server.wallclock_tick_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required SERVER-MVP-0 deterministic tick surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-SERVER-TICK-DETERMINISTIC"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="server.wallclock_tick_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing server tick marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-SERVER-TICK-DETERMINISTIC"],
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
                    category="server.wallclock_tick_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["forbidden wall-clock tick token(s): {}".format(", ".join(found[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-SERVER-TICK-DETERMINISTIC"],
                    related_paths=related_paths,
                )
            )
    return findings

