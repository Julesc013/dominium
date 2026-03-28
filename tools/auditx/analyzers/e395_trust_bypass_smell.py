"""E395 mod trust bypass smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E395_TRUST_BYPASS_SMELL"
REQUIRED_TOKENS = {
    "docs/modding/MOD_TRUST_AND_CAPABILITIES.md": (
        "trust.official_signed",
        "trust.thirdparty_signed",
        "trust.unsigned",
        "trust.local_dev",
        "refusal.mod.trust_denied",
        "refusal.mod.nondeterminism_forbidden",
    ),
    "data/registries/mod_policy_registry.json": (
        "mod_policy.anarchy",
        "mod_policy.strict",
        "mod_policy.lab",
        "overlay.conflict.refuse",
        "overlay.conflict.last_wins",
    ),
    "modding/mod_policy_engine.py": (
        "REFUSAL_MOD_TRUST_DENIED",
        "REFUSAL_MOD_NONDETERMINISM_FORBIDDEN",
        "allowed_trust_levels",
        "forbid_nondeterminism",
        "validate_saved_mod_policy(",
    ),
    "tools/xstack/registry_compile/compiler.py": (
        "evaluate_mod_policy(",
        "\"mod_policy_id\"",
        "\"mod_policy_registry_hash\"",
        "\"mod_policy_proof_hash\"",
    ),
    "tools/xstack/sessionx/runner.py": (
        "validate_saved_mod_policy(",
        "\"mod_policy_id\"",
        "\"mod_policy_registry_hash\"",
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
                    category="modding.trust_bypass_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required mod trust enforcement surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-MOD-POLICY-ENFORCED",
                        "INV-PACKS-MUST-DECLARE-CAPABILITIES",
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
                    category="modding.trust_bypass_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing mod trust marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-MOD-POLICY-ENFORCED",
                        "INV-PACKS-MUST-DECLARE-CAPABILITIES",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
