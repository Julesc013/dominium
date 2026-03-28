"""E440 LIB-6 import without hash verification smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E440_IMPORT_WITHOUT_HASH_CHECK_SMELL"
REQUIRED_TOKENS = {
    "docs/lib/EXPORT_IMPORT_FORMAT.md": (
        "recompute each `content_hash`",
        "recompute `bundle_hash`",
        "refuse if any mismatch occurs",
    ),
    "lib/import/import_engine.py": (
        "verify_bundle_directory(",
        "_insert_bundle_store_artifacts(",
        "\"refusal.bundle.artifact_hash_mismatch\"",
    ),
    "lib/bundle/bundle_manifest.py": (
        "\"bundle_content_hash_mismatch\"",
        "\"bundle_hash_mismatch\"",
        "\"bundle_hash_index_mismatch\"",
    ),
    "tools/lib/tool_verify_bundle.py": (
        "verify_bundle_directory(",
        "return 0 if str(result.get(\"result\", \"\")).strip() == \"complete\" else 3",
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
                    category="bundle.import_without_hash_check_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required LIB-6 import/hash-verification surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-IMPORT-VALIDATES-HASHES",
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
                    category="bundle.import_without_hash_check_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing LIB-6 import/hash-check marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-IMPORT-VALIDATES-HASHES",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
