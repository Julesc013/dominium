"""E407 ad hoc handshake smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E407_AD_HOC_HANDSHAKE_SMELL"
REQUIRED_TOKENS = {
    "tools/xstack/sessionx/net_handshake.py": (
        "negotiate_endpoint_descriptors(",
        '"negotiation_record_hash"',
        '"compatibility_mode_id"',
        '"endpoint_descriptor"',
    ),
    "src/server/net/loopback_transport.py": (
        "negotiate_endpoint_descriptors(",
        '"negotiation_record_hash"',
        '"compatibility_mode_id"',
        '"endpoint_descriptor"',
    ),
    "docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md": (
        "Choose a mutually supported “compatibility mode”",
        "Produce a signed/hashed negotiation record",
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
                    category="compat.capability_negotiation.ad_hoc_handshake_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required negotiation handshake surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-NEGOTIATION-REQUIRED-FOR-CONNECTIONS"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.capability_negotiation.ad_hoc_handshake_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing negotiation-handshake marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-NEGOTIATION-REQUIRED-FOR-CONNECTIONS"],
                    related_paths=related_paths,
                )
            )
    return findings
