"""E390 contract mismatch not refused smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E390_CONTRACT_MISMATCH_NOT_REFUSED_SMELL"
REQUIRED_FILE_TOKENS = {
    "universe/universe_contract_enforcer.py": (
        "enforce_session_contract_bundle(",
        "refusal.contract.missing_bundle",
        "refusal.contract.mismatch",
        "Replay requires SessionSpec.semantic_contract_registry_hash",
    ),
    "tools/xstack/sessionx/runner.py": (
        "enforce_session_contract_bundle(",
        '"contract_bundle_hash"',
        '"semantic_contract_registry_hash"',
    ),
    "tools/xstack/sessionx/script_runner.py": (
        "enforce_session_contract_bundle(",
        '"contract_bundle_hash"',
        '"semantic_contract_registry_hash"',
    ),
    "docs/meta/UNIVERSE_CONTRACT_BUNDLE.md": (
        "refusal.contract.mismatch",
        "Run the explicit CompatX migration tool",
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
                    category="compat.contract_mismatch_not_refused_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["required contract refusal surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-REPLAY-REFUSES-CONTRACT-MISMATCH"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.contract_mismatch_not_refused_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing contract-refusal marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-REPLAY-REFUSES-CONTRACT-MISMATCH"],
                    related_paths=related_paths,
                )
            )
    return findings
