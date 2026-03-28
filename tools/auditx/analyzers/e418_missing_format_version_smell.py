"""E418 missing format-version smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E418_MISSING_FORMAT_VERSION_SMELL"
REQUIRED_TOKENS = {
    "docs/compat/DATA_FORMAT_VERSIONING.md": (
        "format_version",
        "No silent fallback to reinterpretation.",
        "read-only mode",
    ),
    "compat/data_format_loader.py": (
        "CURRENT_ARTIFACT_FORMAT_VERSION",
        "stamp_artifact_metadata(",
        "load_versioned_artifact(",
    ),
    "schemas/save_file.schema.json": (
        "\"title\": \"Save File Metadata Schema\"",
        "\"format_version\"",
        "\"semantic_contract_bundle_hash\"",
    ),
    "schemas/blueprint_file.schema.json": (
        "\"title\": \"Blueprint File Metadata Schema\"",
        "\"format_version\"",
        "\"required_contract_ranges\"",
    ),
    "schemas/profile_bundle.schema.json": (
        "\"format_version\"",
        "\"engine_version_created\"",
    ),
    "schemas/session_template.schema.json": (
        "\"format_version\"",
        "\"engine_version_created\"",
    ),
    "schemas/pack_lock.schema.json": (
        "\"format_version\"",
        "\"engine_version_created\"",
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
                    category="compat.missing_format_version_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required format-version surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-ARTIFACTS-MUST-HAVE-FORMAT-VERSION",
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
                    category="compat.missing_format_version_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing format-version marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-ARTIFACTS-MUST-HAVE-FORMAT-VERSION",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
