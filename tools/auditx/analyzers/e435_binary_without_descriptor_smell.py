"""E435 binary-without-descriptor smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E435_BINARY_WITHOUT_DESCRIPTOR_SMELL"
REQUIRED_TOKENS = {
    "schema/lib/product_build_descriptor.schema": (
        "binary_hash",
        "endpoint_descriptor_hash",
    ),
    "lib/install/install_validator.py": (
        "descriptor_ref",
        "endpoint_descriptor_hash",
        "REFUSAL_INSTALL_HASH_MISMATCH",
    ),
    "tools/setup/setup_cli.py": (
        "descriptor_relpath",
        "endpoint_descriptor_hash",
        "product_build_descriptors",
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
                category="install.binary_without_descriptor_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["missing binary/descriptor integrity marker(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=[
                    "INV-BINARY-HASH-MATCHES-MANIFEST",
                ],
                related_paths=related_paths,
            )
        )
    return findings
