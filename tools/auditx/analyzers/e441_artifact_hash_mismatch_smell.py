"""E441 artifact-hash-mismatch smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E441_ARTIFACT_HASH_MISMATCH_SMELL"
REQUIRED_TOKENS = {
    "docs/architecture/ARTIFACT_MODEL.md": (
        "INV-ARTIFACT-LOAD-VALIDATED",
        "content_hash",
        "No silent migration is permitted.",
    ),
    "lib/artifact/artifact_validator.py": (
        "compute_artifact_content_hash(",
        "REFUSAL_ARTIFACT_HASH_MISMATCH",
        "evaluate_artifact_load(",
    ),
    "tools/launcher/launcher_cli.py": (
        "evaluate_artifact_load(",
        "profile bundle verification failed",
        "\"profile_bundle_open\": profile_bundle_open",
    ),
    "tools/share/share_cli.py": (
        "validate_bundle_artifact(",
        "artifact manifest validation failed",
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
                category="artifact.artifact_hash_mismatch_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["missing artifact-hash-validation marker(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=[
                    "INV-ARTIFACT-LOAD-VALIDATED",
                ],
                related_paths=related_paths,
            )
        )
    return findings
