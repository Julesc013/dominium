"""E421 XStack runtime dependency smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E421_XSTACK_RUNTIME_DEPENDENCY_SMELL"
WATCH_PATHS = (
    "docs/appshell/APPSHELL_CONSTITUTION.md",
    "appshell/__init__.py",
    "appshell/args_parser.py",
    "appshell/bootstrap.py",
    "appshell/command_registry.py",
    "appshell/compat_adapter.py",
    "appshell/config_loader.py",
    "appshell/console_repl.py",
    "appshell/logging_sink.py",
    "appshell/mode_dispatcher.py",
    "appshell/pack_verifier_adapter.py",
    "appshell/rendered_stub.py",
    "appshell/tui/__init__.py",
    "appshell/tui/tui_engine.py",
    "appshell/tui_stub.py",
    "tools/appshell/product_stub_cli.py",
)
FORBIDDEN_TOKENS = (
    "tools.xstack",
    "xstack.",
)


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
    related_paths = list(WATCH_PATHS)
    doctrine_text = _read_text(repo_root, "docs/appshell/APPSHELL_CONSTITUTION.md")
    if "must not depend on repo or XStack at runtime" not in doctrine_text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="appshell.xstack_runtime_dependency_smell",
                severity="RISK",
                confidence=0.95,
                file_path="docs/appshell/APPSHELL_CONSTITUTION.md",
                line=1,
                evidence=["AppShell doctrine no longer declares runtime independence from XStack"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-OFFLINE-BOOT-OK",
                ],
                related_paths=related_paths,
            )
        )
    for rel_path in WATCH_PATHS[1:]:
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="appshell.xstack_runtime_dependency_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required AppShell runtime surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-OFFLINE-BOOT-OK",
                    ],
                    related_paths=related_paths,
                )
            )
            continue
        for token in FORBIDDEN_TOKENS:
            if token in text:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="appshell.xstack_runtime_dependency_smell",
                        severity="RISK",
                        confidence=0.98,
                        file_path=rel_path,
                        line=1,
                        evidence=["forbidden runtime XStack token '{}' detected".format(token)],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="REWRITE",
                        related_invariants=[
                            "INV-OFFLINE-BOOT-OK",
                        ],
                        related_paths=related_paths,
                    )
                )
                break
    return findings
