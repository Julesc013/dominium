"""E408 silent degrade smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E408_SILENT_DEGRADE_SMELL"
REQUIRED_TOKENS = {
    "compat/capability_negotiation.py": (
        "def _degrade_plan(",
        '"degrade.optional_capability_unavailable"',
        '"ignored.unknown_capability"',
        '"compatibility_mode_id"',
    ),
    "data/registries/product_registry.json": (
        '"default_degrade_ladders"',
        '"degrade.client.rendered_to_tui"',
        '"degrade.client.contract_read_only"',
    ),
    "docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md": (
        "All degradation decisions must appear in the NegotiationRecord.",
        "disable feature",
        "substitute stub",
        "refuse the entire connection",
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
                    category="compat.capability_negotiation.silent_degrade_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required degrade-plan surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-DEGRADE-PLAN-DECLARED", "INV-UNKNOWN-CAP-IGNORED-DETERMINISTICALLY"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.capability_negotiation.silent_degrade_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing degrade marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-DEGRADE-PLAN-DECLARED", "INV-UNKNOWN-CAP-IGNORED-DETERMINISTICALLY"],
                    related_paths=related_paths,
                )
            )
    return findings
