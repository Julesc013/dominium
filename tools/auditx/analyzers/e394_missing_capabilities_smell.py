"""E394 missing pack capability declaration smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E394_MISSING_CAPABILITIES_SMELL"
REQUIRED_TOKENS = {
    "docs/modding/MOD_TRUST_AND_CAPABILITIES.md": (
        "cap.overlay_patch",
        "cap.add_templates",
        "cap.add_processes",
        "cap.add_logic_elements",
        "cap.add_profiles",
        "cap.add_contracts",
        "cap.allow_exception_profiles",
        "pack.capabilities.json",
    ),
    "data/registries/capability_registry.json": (
        "cap.overlay_patch",
        "cap.add_templates",
        "cap.add_processes",
        "cap.add_logic_elements",
        "cap.add_profiles",
        "cap.add_contracts",
        "cap.allow_exception_profiles",
    ),
    "modding/mod_policy_engine.py": (
        "PACK_CAPABILITIES_NAME",
        "infer_required_capabilities(",
        "REFUSAL_MOD_CAPABILITY_DENIED",
        "cap.allow_exception_profiles",
    ),
    "tools/xstack/pack_loader/loader.py": (
        "PACK_CAPABILITIES_NAME",
        "PACK_TRUST_DESCRIPTOR_NAME",
        "mod_policy_metadata_errors",
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
                    category="modding.missing_capabilities_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required mod capability surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-PACKS-MUST-DECLARE-CAPABILITIES",
                        "INV-MOD-POLICY-ENFORCED",
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
                    category="modding.missing_capabilities_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing mod capability marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-PACKS-MUST-DECLARE-CAPABILITIES",
                        "INV-MOD-POLICY-ENFORCED",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
