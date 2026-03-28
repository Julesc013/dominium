"""E422 ad hoc command smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E422_AD_HOC_COMMAND_SMELL"
REQUIRED_TOKENS = {
    "docs/appshell/COMMANDS_AND_REFUSALS.md": (
        "registered declaratively",
        "compat-status",
        "packs verify",
        "profiles show",
    ),
    "data/registries/command_registry.json": (
        '"command_path": "help"',
        '"command_path": "compat-status"',
        '"command_path": "packs verify"',
        '"command_path": "profiles show"',
    ),
    "appshell/bootstrap.py": (
        "dispatch_registered_command(",
        "build_root_command_descriptors(",
        "format_help_text(",
    ),
    "appshell/commands/command_engine.py": (
        "find_command_descriptor(",
        'handler_id == "packs_verify"',
        'handler_id == "profiles_show"',
        'handler_id == "compat_status"',
    ),
    "tools/appshell/tool_generate_command_docs.py": (
        "load_command_registry",
        "generate_cli_reference(",
        "CLI_REFERENCE.md",
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
                    category="appshell.ad_hoc_command_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required AppShell command surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-COMMANDS-REGISTERED",
                        "INV-NO-ADHOC-ARG-PARSING",
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
                    category="appshell.ad_hoc_command_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing APPSHELL-1 command marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-COMMANDS-REGISTERED",
                        "INV-NO-ADHOC-ARG-PARSING",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
