"""E325 security-bypass smell analyzer for LOGIC-8."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E325_SECURITY_BYPASS_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e325_security_bypass_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "docs/logic/FAULT_NOISE_SECURITY_MODEL.md",
    "schema/logic/security_policy.schema",
    "data/registries/logic_security_policy_registry.json",
    "logic/eval/sense_engine.py",
    "tools/logic/tool_replay_fault_window.py",
)


class SecurityBypassSmell:
    analyzer_id = ANALYZER_ID


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

    doc_rel = "docs/logic/FAULT_NOISE_SECURITY_MODEL.md"
    doc_text = _read_text(repo_root, doc_rel).lower()
    for token in ("credential verification", "encryption", "security_policy_id", "explain.logic_spoof_detected"):
        if token in doc_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.security_bypass_smell",
                severity="RISK",
                confidence=0.84,
                file_path=doc_rel,
                line=1,
                evidence=["fault/noise doctrine missing explicit security hook token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="DOC_FIX",
                related_invariants=["INV-SECURITY-POLICY-ENFORCED"],
                related_paths=[doc_rel],
            )
        )

    schema_rel = "schema/logic/security_policy.schema"
    schema_text = _read_text(repo_root, schema_rel)
    for token in ("security_policy_id", "requires_auth", "requires_encryption", "allowed_credential_types"):
        if token in schema_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.security_bypass_smell",
                severity="VIOLATION",
                confidence=0.93,
                file_path=schema_rel,
                line=1,
                evidence=["logic security policy schema missing required field", token],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-SECURITY-POLICY-ENFORCED"],
                related_paths=[schema_rel],
            )
        )

    registry_rel = "data/registries/logic_security_policy_registry.json"
    registry_text = _read_text(repo_root, registry_rel)
    for token in ("sec.none", "sec.auth_required_stub", "sec.encrypted_required_stub", "requires_auth", "requires_encryption"):
        if token in registry_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.security_bypass_smell",
                severity="VIOLATION",
                confidence=0.94,
                file_path=registry_rel,
                line=1,
                evidence=["logic security registry missing required security token", token],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-SECURITY-POLICY-ENFORCED"],
                related_paths=[registry_rel],
            )
        )

    sense_rel = "logic/eval/sense_engine.py"
    sense_text = _read_text(repo_root, sense_rel)
    for token in ("_security_gate(", "requires_auth", "requires_encryption", "build_logic_security_fail_row(", "explain.logic_spoof_detected"):
        if token in sense_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.security_bypass_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=sense_rel,
                line=1,
                evidence=["logic SENSE path missing security-enforcement token", token],
                suggested_classification="INVALID",
                recommended_action="REWRITE",
                related_invariants=["INV-SECURITY-POLICY-ENFORCED"],
                related_paths=[sense_rel],
            )
        )

    replay_rel = "tools/logic/tool_replay_fault_window.py"
    replay_text = _read_text(repo_root, replay_rel)
    if "logic_security_fail_hash_chain" not in replay_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.security_bypass_smell",
                severity="RISK",
                confidence=0.88,
                file_path=replay_rel,
                line=1,
                evidence=["fault replay tool missing security proof surface", "logic_security_fail_hash_chain"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SECURITY-POLICY-ENFORCED"],
                related_paths=[replay_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
