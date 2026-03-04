"""E215 entropy bypass smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E215_ENTROPY_BYPASS_SMELL"


class EntropyBypassSmell:
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

    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    contribution_registry_rel = "data/registries/entropy_contribution_registry.json"
    effect_registry_rel = "data/registries/entropy_effect_policy_registry.json"

    runtime_text = _read_text(repo_root, runtime_rel)
    if not runtime_text:
        return findings

    required_runtime_tokens = (
        "_record_entropy_contribution_in_state(",
        "_apply_entropy_reset_in_state(",
        "entropy_hash_chain",
        "entropy_reset_events_hash_chain",
        "evaluate_entropy_effects(",
    )
    for token in required_runtime_tokens:
        if token in runtime_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.entropy_bypass_smell",
                severity="RISK",
                confidence=0.88,
                file_path=runtime_rel,
                line=1,
                evidence=["required PHYS-4 entropy integration token missing", token],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-ENTROPY-UPDATE-THROUGH-ENGINE",
                ],
                related_paths=[runtime_rel],
            )
        )

    contribution_text = _read_text(repo_root, contribution_registry_rel)
    if not contribution_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.entropy_bypass_smell",
                severity="RISK",
                confidence=0.9,
                file_path=contribution_registry_rel,
                line=1,
                evidence=["entropy contribution registry missing"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-ENTROPY-UPDATE-THROUGH-ENGINE",
                ],
                related_paths=[contribution_registry_rel],
            )
        )

    effect_text = _read_text(repo_root, effect_registry_rel)
    if not effect_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.entropy_bypass_smell",
                severity="RISK",
                confidence=0.9,
                file_path=effect_registry_rel,
                line=1,
                evidence=["entropy effect policy registry missing"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-ENTROPY-UPDATE-THROUGH-ENGINE",
                ],
                related_paths=[effect_registry_rel],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
