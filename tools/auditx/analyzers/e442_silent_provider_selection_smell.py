"""E442 silent-provider-selection smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E442_SILENT_PROVIDER_SELECTION_SMELL"
REQUIRED_TOKENS = {
    "docs/architecture/FORKING_AND_PROVIDES_MODEL.md": (
        "No silent provider selection is permitted.",
        "resolve.deterministic_highest_priority",
        "resolve.deterministic_lowest_pack_id",
    ),
    "lib/provides/provider_resolution.py": (
        "selection_logged",
        "resolve_providers(",
        "REFUSAL_PROVIDES_AMBIGUOUS",
    ),
    "tools/launcher/launcher_cli.py": (
        "\"provider_resolution\": provider_resolution",
        "\"provider_selection_logged\": bool(provider_resolution.get(\"selection_logged\", False))",
        "provider resolution failed",
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
                category="provides.silent_provider_selection_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["missing provider-selection marker(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-PROVIDES-RESOLUTION-DETERMINISTIC",
                    "INV-STRICT-REFUSES-AMBIGUITY",
                ],
                related_paths=related_paths,
            )
        )
    return findings
