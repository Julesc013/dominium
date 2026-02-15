"""E12 Signature bypass smell analyzer."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

from analyzers.base import make_finding


ANALYZER_ID = "E12_SIGNATURE_BYPASS_SMELL"
WATCH_PREFIXES = (
    "tools/xstack/sessionx/net_handshake.py",
    "tools/security/tool_securex_verify_pack.py",
    "tools/security/tool_securex_verify_lockfile.py",
    "data/registries/securex_policy_registry.json",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _load_json(path: str) -> Tuple[Dict[str, object], str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid_json"
    if not isinstance(payload, dict):
        return {}, "invalid_object"
    return payload, ""


def _load_text(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    securex_registry_path = os.path.join(repo_root, "data", "registries", "securex_policy_registry.json")
    securex_registry_payload, securex_registry_err = _load_json(securex_registry_path)
    if securex_registry_err:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.signature_bypass_smell",
                severity="RISK",
                confidence=0.94,
                file_path="data/registries/securex_policy_registry.json",
                evidence=["SecureX policy registry is missing or invalid JSON."],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-RANKED-REQUIRES-SECUREX-STRICT"],
                related_paths=["data/registries/securex_policy_registry.json"],
            )
        )
        return findings

    securex_rows = (((securex_registry_payload.get("record") or {}).get("policies")) or [])
    rank_row = {}
    for row in securex_rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("securex_policy_id", "")).strip() == "securex.policy.rank_strict":
            rank_row = dict(row)
            break
    if not rank_row:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.signature_bypass_smell",
                severity="VIOLATION",
                confidence=0.98,
                file_path="data/registries/securex_policy_registry.json",
                evidence=["Missing canonical strict SecureX policy securex.policy.rank_strict."],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-RANKED-REQUIRES-SECUREX-STRICT"],
                related_paths=["data/registries/securex_policy_registry.json"],
            )
        )
        return findings

    if bool(rank_row.get("allow_unsigned", True)):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.signature_bypass_smell",
                severity="VIOLATION",
                confidence=0.98,
                file_path="data/registries/securex_policy_registry.json",
                evidence=["securex.policy.rank_strict has allow_unsigned=true."],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-RANKED-REQUIRES-SECUREX-STRICT"],
                related_paths=["data/registries/securex_policy_registry.json"],
            )
        )
    if not bool(rank_row.get("signature_verification_required", False)):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="net.signature_bypass_smell",
                severity="VIOLATION",
                confidence=0.98,
                file_path="data/registries/securex_policy_registry.json",
                evidence=["securex.policy.rank_strict has signature_verification_required=false."],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-RANKED-REQUIRES-SECUREX-STRICT"],
                related_paths=["data/registries/securex_policy_registry.json"],
            )
        )

    handshake_rel = "tools/xstack/sessionx/net_handshake.py"
    handshake_abs = os.path.join(repo_root, handshake_rel.replace("/", os.sep))
    handshake_text = _load_text(handshake_abs)
    required_tokens = (
        "required_signature_status",
        "allow_unsigned",
        "signature_verification_required",
        "_securex_verification_tool_available",
        "refusal.net.handshake_securex_denied",
    )
    for token in required_tokens:
        if token not in handshake_text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="net.signature_bypass_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=handshake_rel,
                    evidence=["Missing SecureX enforcement token '{}' in handshake path.".format(token)],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-RANKED-REQUIRES-SECUREX-STRICT"],
                    related_paths=[
                        handshake_rel,
                        "tools/security/tool_securex_verify_pack.py",
                        "tools/security/tool_securex_verify_lockfile.py",
                    ],
                )
            )

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )

