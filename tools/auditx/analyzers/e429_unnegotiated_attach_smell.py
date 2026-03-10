"""E429 unnegotiated IPC attach smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E429_UNNEGOTIATED_ATTACH_SMELL"
REQUIRED_TOKENS = {
    "docs/appshell/IPC_ATTACH_CONSOLES.md": (
        "`refusal.connection.no_negotiation`",
        "`refusal.connection.negotiation_mismatch`",
        "no shell escape to the operating system",
    ),
    "src/appshell/ipc/ipc_endpoint_server.py": (
        "REFUSAL_CONNECTION_NO_NEGOTIATION",
        "_READ_ONLY_SAFE_COMMAND_PREFIXES",
        "_read_only_command_allowed(",
        "refusal.law.attach_denied",
    ),
    "src/appshell/commands/command_engine.py": (
        'handler_id == "console_attach"',
        '"refusal.connection.no_negotiation"',
        '"refusal.connection.negotiation_mismatch"',
        '"refusal.law.attach_denied"',
    ),
    "tools/appshell/tool_replay_ipc_attach.py": (
        "verify_ipc_attach_replay(",
        "deterministic APPSHELL-4 IPC attach",
    ),
}
FORBIDDEN_TOKENS = {
    "src/appshell/ipc/ipc_endpoint_server.py": ("subprocess.", "os.system(", "Popen("),
    "src/appshell/ipc/ipc_client.py": ("subprocess.", "os.system(", "Popen("),
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
                    category="appshell.ipc.unnegotiated_attach_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required APPSHELL-4 attach-authorization surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-IPC-ATTACH-NEGOTIATED",
                        "INV-NO-PRIVILEGE-ESCALATION",
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
                    category="appshell.ipc.unnegotiated_attach_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing APPSHELL-4 attach marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-IPC-ATTACH-NEGOTIATED",
                        "INV-NO-PRIVILEGE-ESCALATION",
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
                    category="appshell.ipc.unnegotiated_attach_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["forbidden IPC privilege-escalation token(s): {}".format(", ".join(found[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-NO-PRIVILEGE-ESCALATION",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
