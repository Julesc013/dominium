"""E440 manifest-missing smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E440_MANIFEST_MISSING_SMELL"
REQUIRED_TOKENS = {
    "docs/architecture/ARTIFACT_MODEL.md": (
        "INV-SHAREABLE-ARTIFACTS-MUST-HAVE-MANIFEST",
        "artifact_id",
        "content_hash",
    ),
    "schema/lib/artifact_manifest.schema": (
        "artifact_id",
        "artifact_kind_id",
        "migration_refs",
    ),
    "tools/share/share_cli.py": (
        "SHAREABLE_ARTIFACT_MANIFEST_NAME",
        "_build_bundle_artifact_manifest(",
        "validate_bundle_artifact(",
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
                category="artifact.manifest_missing_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["missing artifact-manifest marker(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=[
                    "INV-SHAREABLE-ARTIFACTS-MUST-HAVE-MANIFEST",
                    "INV-ARTIFACTS-CONTENT-ADDRESSED",
                ],
                related_paths=related_paths,
            )
        )
    return findings
