"""E434 path-dependent install smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E434_PATH_DEPENDENT_INSTALL_SMELL"
REQUIRED_TOKENS = {
    "docs/architecture/INSTALL_MODEL.md": (
        "INV-INSTALL-NO-ABSOLUTE-PATH-DEPENDENCY",
        "store_root_ref",
        "product_builds",
    ),
    "tools/setup/setup_cli.py": (
        "\"install_root\": \".\"",
        "store_root_ref",
        "install_mode",
    ),
    "tools/launcher/launcher_cli.py": (
        "resolve_install_root(",
        "compare_required_product_builds(",
        "compare_required_contract_ranges(",
    ),
    "tools/ops/ops_cli.py": (
        "resolve_install_root(",
        "required_product_builds",
        "required_contract_ranges",
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
        missing = [token for token in tokens if token not in text]
        if not missing:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="install.path_dependent_install_smell",
                severity="RISK",
                confidence=0.94,
                file_path=rel_path,
                line=1,
                evidence=["missing install path-independence marker(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-INSTALL-NO-ABSOLUTE-PATH-DEPENDENCY",
                ],
                related_paths=related_paths,
            )
        )
    return findings
