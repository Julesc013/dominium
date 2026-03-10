"""E428 ad hoc IPC protocol smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E428_AD_HOC_IPC_PROTOCOL_SMELL"
REQUIRED_TOKENS = {
    "docs/appshell/IPC_ATTACH_CONSOLES.md": (
        "connector and endpoint run the CAP-NEG-2 handshake",
        "Connections must not succeed without negotiation.",
        "each channel has a monotonic `seq_no`",
    ),
    "src/appshell/ipc/ipc_transport.py": (
        "build_ipc_frame(",
        "IPC_CHANNEL_IDS",
        "send_frame(",
        "recv_frame(",
    ),
    "src/appshell/ipc/ipc_endpoint_server.py": (
        "build_handshake_message(",
        "build_compat_refusal(",
        "_next_seq(",
        "dispatch_registered_command(",
    ),
    "src/appshell/ipc/ipc_client.py": (
        "build_handshake_message(",
        "attach_ipc_endpoint(",
        "run_ipc_console_command(",
        "query_ipc_log_events(",
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
                    category="appshell.ipc.ad_hoc_ipc_protocol_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required APPSHELL-4 IPC surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-IPC-ATTACH-NEGOTIATED",
                        "INV-IPC-SEQ-NO-MONOTONIC",
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
                    category="appshell.ipc.ad_hoc_ipc_protocol_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing APPSHELL-4 IPC marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-IPC-ATTACH-NEGOTIATED",
                        "INV-IPC-SEQ-NO-MONOTONIC",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
