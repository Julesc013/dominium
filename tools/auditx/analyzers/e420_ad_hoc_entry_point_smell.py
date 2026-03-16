"""E420 ad hoc entrypoint smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E420_AD_HOC_ENTRY_POINT_SMELL"
REQUIRED_TOKENS = {
    "docs/appshell/APPSHELL_CONSTITUTION.md": (
        "parse args",
        "mode.cli",
        "Runtime Independence",
    ),
    "src/appshell/bootstrap.py": (
        "def appshell_main(",
        "dispatch_registered_command(",
        "build_root_command_descriptors(",
        "format_help_text(",
    ),
    "tools/mvp/runtime_entry.py": (
        "from src.appshell import appshell_main",
        "def appshell_product_bootstrap(",
        "def client_main(",
        "def server_main(",
        "product_bootstrap=appshell_product_bootstrap",
    ),
    "src/server/server_main.py": (
        "from src.appshell import appshell_main",
        "def appshell_product_bootstrap(",
        "product_bootstrap=appshell_product_bootstrap",
    ),
    "tools/setup/setup_cli.py": (
        "from src.appshell import appshell_main",
        "def appshell_product_bootstrap(",
        "product_bootstrap=appshell_product_bootstrap",
    ),
    "tools/launcher/launch.py": (
        "from src.appshell import appshell_main",
        "def appshell_product_bootstrap(",
        "product_bootstrap=appshell_product_bootstrap",
    ),
    "dist/bin/dominium_client": (
        "client_main(sys.argv[1:])",
    ),
    "dist/bin/dominium_server": (
        "server_main(sys.argv[1:])",
    ),
    "dist/bin/launcher": (
        "from tools.launcher.launch import main",
    ),
    "dist/bin/setup": (
        "from tools.setup.setup_cli import main",
    ),
    "dist/bin/engine": (
        "product_stub_cli.py",
        "--product-id",
    ),
    "dist/bin/game": (
        "product_stub_cli.py",
        "--product-id",
    ),
    "dist/bin/tool_attach_console_stub": (
        "product_stub_cli.py",
        "--product-id",
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
                    category="appshell.ad_hoc_entry_point_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required AppShell entrypoint surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-PRODUCTS-MUST-USE-APPSHELL",
                        "INV-NO-ADHOC-MAIN",
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
                    category="appshell.ad_hoc_entry_point_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing AppShell adoption marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-PRODUCTS-MUST-USE-APPSHELL",
                        "INV-NO-ADHOC-MAIN",
                    ],
                    related_paths=related_paths,
                )
            )
            continue
        if rel_path.startswith("dist/bin/") and "tool_emit_descriptor" in text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="appshell.ad_hoc_entry_point_smell",
                    severity="RISK",
                    confidence=0.94,
                    file_path=rel_path,
                    line=1,
                    evidence=["wrapper still contains ad hoc descriptor routing instead of AppShell-owned entrypoint flow"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-PRODUCTS-MUST-USE-APPSHELL",
                        "INV-NO-ADHOC-MAIN",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
