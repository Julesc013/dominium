"""E327 protocol-security-bypass smell analyzer for LOGIC-9."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E327_PROTOCOL_SECURITY_BYPASS_SMELL"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


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

    doc_rel = "docs/logic/PROTOCOL_LAYER_MODEL.md"
    doc_text = _read_text(repo_root, doc_rel).lower()
    for token in ("auth", "encryption", "security", "sig"):
        if token in doc_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.protocol_security_bypass_smell",
                severity="RISK",
                confidence=0.85,
                file_path=doc_rel,
                line=1,
                evidence=["protocol doctrine missing security token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-PROTOCOL-SECURITY-ENFORCED"],
                related_paths=[doc_rel],
            )
        )

    registry_rel = "data/registries/protocol_registry.json"
    registry_text = _read_text(repo_root, registry_rel)
    for token in ("security_policy_id", "protocol.simple_frame_stub", "protocol.bus_arbitration_stub"):
        if token in registry_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.protocol_security_bypass_smell",
                severity="VIOLATION",
                confidence=0.91,
                file_path=registry_rel,
                line=1,
                evidence=["protocol registry missing security-binding token", token],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-PROTOCOL-SECURITY-ENFORCED"],
                related_paths=[registry_rel],
            )
        )

    engine_rel = "logic/protocol/protocol_engine.py"
    engine_text = _read_text(repo_root, engine_rel)
    for token in ("security_policy_id", "protocol_security_block", "logic_security_fail_rows", "security_header"):
        if token in engine_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.protocol_security_bypass_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=engine_rel,
                line=1,
                evidence=["protocol engine missing security-enforcement token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-PROTOCOL-SECURITY-ENFORCED"],
                related_paths=[engine_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
