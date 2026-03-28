"""E389 missing contract bundle smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E389_MISSING_CONTRACT_BUNDLE_SMELL"
REQUIRED_FILE_TOKENS = {
    "schema/universe/universe_identity.schema": (
        "universe_contract_bundle_ref",
        "universe_contract_bundle_hash",
    ),
    "schemas/universe_identity.schema.json": (
        '"universe_contract_bundle_ref"',
        '"universe_contract_bundle_hash"',
    ),
    "universe/universe_identity_builder.py": (
        "pin_contract_bundle_metadata(",
        "validate_pinned_contract_bundle_metadata(",
    ),
    "tools/xstack/sessionx/creator.py": (
        "DEFAULT_UNIVERSE_CONTRACT_BUNDLE_REF",
        '"contract_bundle_hash"',
    ),
    "docs/meta/UNIVERSE_CONTRACT_BUNDLE.md": (
        "refusal.contract.missing_bundle",
        "UniverseIdentity",
        "SessionSpec",
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
    related_paths = list(REQUIRED_FILE_TOKENS.keys())
    for rel_path, tokens in REQUIRED_FILE_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.missing_contract_bundle_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["required contract-bundle surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-UNIVERSE-MUST-HAVE-CONTRACT-BUNDLE"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.missing_contract_bundle_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing contract-bundle marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-UNIVERSE-MUST-HAVE-CONTRACT-BUNDLE"],
                    related_paths=related_paths,
                )
            )
    return findings
