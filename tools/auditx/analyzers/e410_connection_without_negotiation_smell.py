"""E410 connection without negotiation smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E410_CONNECTION_WITHOUT_NEGOTIATION_SMELL"
REQUIRED_TOKENS = {
    "docs/compat/NEGOTIATION_HANDSHAKES.md": (
        "Missing negotiation yields `refusal.connection.no_negotiation`.",
        "`compat.read_only`",
        "session_begin",
    ),
    "server/net/loopback_transport.py": (
        "build_handshake_message(",
        '"official.handshake_messages"',
        '"client_acknowledged"',
        "compat.handshake.ack.v1",
    ),
    "server/server_boot.py": (
        "REFUSAL_CONNECTION_NO_NEGOTIATION",
        "REFUSAL_CLIENT_READ_ONLY",
        "COMPAT_MODE_READ_ONLY",
    ),
    "tools/compat/tool_replay_negotiation.py": (
        "verify_recorded_negotiation(",
        '"negotiation_record_hash"',
    ),
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
    related_paths = sorted(REQUIRED_TOKENS.keys())
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.negotiation.connection_without_negotiation_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required CAP-NEG-2 negotiation surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-CONNECTION-REQUIRES-NEGOTIATION",
                        "INV-NEGOTIATION-RECORD-LOGGED",
                        "INV-READONLY-ENFORCED-WHEN-NEGOTIATED",
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
                    category="compat.negotiation.connection_without_negotiation_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing CAP-NEG-2 marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-CONNECTION-REQUIRES-NEGOTIATION",
                        "INV-NEGOTIATION-RECORD-LOGGED",
                        "INV-READONLY-ENFORCED-WHEN-NEGOTIATED",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
