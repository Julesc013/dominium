"""E433 secrets-in-repro-bundle smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E433_SECRETS_IN_BUNDLE_SMELL"
REQUIRED_TOKENS = {
    "docs/diag/REPRO_BUNDLE_MODEL.md": (
        "Bundles must exclude:",
        "account secrets",
        "signing keys",
        "machine identifiers beyond coarse host meta",
    ),
    "diag/repro_bundle_builder.py": (
        "_SECRET_KEY_FRAGMENTS",
        "_sanitize_tree(",
        '"account_secret"',
        '"machine_id"',
        '"private_key"',
        '"signing_key"',
    ),
    "tools/xstack/testx/tests/test_no_secrets_in_bundle.py": (
        "repro bundle strips secret-like fields",
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
                    category="diag.secrets_in_bundle_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required DIAG-0 secret-scrubbing surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-REPRO-BUNDLE-NO-SECRETS",
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
                    category="diag.secrets_in_bundle_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing DIAG-0 secret-scrubbing marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-REPRO-BUNDLE-NO-SECRETS",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
