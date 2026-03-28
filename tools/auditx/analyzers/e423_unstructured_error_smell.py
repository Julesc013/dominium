"""E423 unstructured error smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E423_UNSTRUCTURED_ERROR_SMELL"
REQUIRED_TOKENS = {
    "docs/appshell/COMMANDS_AND_REFUSALS.md": (
        "refusal_code",
        "reason",
        "remediation_hint",
        "Exit Codes",
    ),
    "data/registries/refusal_to_exit_registry.json": (
        '"refusal_code": "refusal.io.invalid_args"',
        '"refusal_prefix": "refusal.compat."',
        '"refusal_prefix": "refusal.debug."',
    ),
    "data/registries/refusal_code_registry.json": (
        '"refusal_code": "refusal.debug.command_unavailable"',
        '"refusal_code": "refusal.debug.command_unknown"',
        '"refusal_code": "refusal.io.invalid_args"',
    ),
    "appshell/commands/command_engine.py": (
        '"refusal_code"',
        '"reason"',
        '"remediation_hint"',
        "_exit_code_for_refusal(",
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
                    category="appshell.unstructured_error_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required AppShell refusal surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-REFUSAL-CODES-STABLE"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="appshell.unstructured_error_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing APPSHELL-1 refusal marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-REFUSAL-CODES-STABLE"],
                    related_paths=related_paths,
                )
            )
    return findings
