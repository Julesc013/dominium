"""E403 intent without authority smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E403_INTENT_WITHOUT_AUTHORITY_SMELL"
REQUIRED_TOKENS = {
    "src/server/server_boot.py": (
        "REFUSAL_CLIENT_UNAUTHORIZED",
        "build_connection_authority_context(",
        "submit_client_intent(",
        "build_client_intent_envelope(",
        "queue_intent_envelope(",
        "incoming client intent must declare intent_id and target",
    ),
    "src/server/net/loopback_transport.py": (
        "build_connection_authority_context(",
        '"authority_context": authority_context',
        "join_client_midstream(",
    ),
    "tools/server/server_mvp0_probe.py": (
        "unauthorized_intent_report(",
        '"reason_code"',
        '"refusal.client.unauthorized"',
    ),
    "docs/server/SERVER_MVP_BASELINE.md": (
        "Every incoming client intent must be wrapped in `AuthorityContext`.",
        "`refusal.client.unauthorized`",
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
    related_paths = list(REQUIRED_TOKENS.keys())
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="server.intent_without_authority_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required SERVER-MVP-0 authority-enforcement surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-AUTHORITY-REQUIRED"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="server.intent_without_authority_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing authority-enforcement marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-AUTHORITY-REQUIRED"],
                    related_paths=related_paths,
                )
            )
    return findings
