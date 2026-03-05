"""E273 missing system explain contract smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E273_MISSING_SYSTEM_EXPLAIN_CONTRACT_SMELL"


class MissingSystemExplainContractSmell:
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

    explain_registry_rel = "data/registries/explain_contract_registry.json"
    runtime_rel = "tools/xstack/sessionx/process_runtime.py"
    process_registry_rel = "data/registries/process_registry.json"
    explain_registry_text = _read_text(repo_root, explain_registry_rel)
    runtime_text = _read_text(repo_root, runtime_rel)
    process_registry_text = _read_text(repo_root, process_registry_rel)

    required_contract_tokens = (
        '"contract_id": "explain.system_forced_expand"',
        '"contract_id": "explain.system_failure"',
        '"contract_id": "explain.system_safety_shutdown"',
        '"contract_id": "explain.system.certificate_revocation"',
        '"contract_id": "explain.system_capsule_error_bound_exceeded"',
        '"contract_id": "explain.system_invariant_violation"',
        '"contract_id": "explain.system_compliance_failure"',
    )
    for token in required_contract_tokens:
        if token in explain_registry_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="contracts.missing_system_explain_contract_smell",
                severity="RISK",
                confidence=0.95,
                file_path=explain_registry_rel,
                line=1,
                evidence=["missing SYS-7 explain contract declaration", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-EXPLAIN-CONTRACT-REQUIRED-FOR-SYSTEM-EVENTS"],
                related_paths=[explain_registry_rel, runtime_rel, process_registry_rel],
            )
        )

    for token, file_path in (
        ('elif process_id == "process.system_generate_explain":', runtime_rel),
        ("evaluate_system_explain_request(", runtime_rel),
        ('"process_id": "process.system_generate_explain"', process_registry_rel),
    ):
        text = runtime_text if file_path == runtime_rel else process_registry_text
        if token in text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="contracts.missing_system_explain_contract_smell",
                severity="RISK",
                confidence=0.9,
                file_path=file_path,
                line=1,
                evidence=["missing SYS-7 system explain integration token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-EXPLAIN-CONTRACT-REQUIRED-FOR-SYSTEM-EVENTS"],
                related_paths=[runtime_rel, process_registry_rel],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
