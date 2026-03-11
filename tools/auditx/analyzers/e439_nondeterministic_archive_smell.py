"""E439 nondeterministic LIB-6 bundle/archive smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E439_NONDETERMINISTIC_ARCHIVE_SMELL"
REQUIRED_TOKENS = {
    "docs/lib/EXPORT_IMPORT_FORMAT.md": (
        "fixed timestamp `2000-01-01T00:00:00Z`",
        "archive container metadata does not affect `bundle_hash`",
        "No OS-specific metadata is permitted in archive entries.",
    ),
    "src/lib/bundle/bundle_manifest.py": (
        "compute_bundle_hash(",
        "verify_bundle_directory(",
        "\"bundle_hash_mismatch\"",
    ),
    "tools/lib/tool_verify_bundle.py": (
        "Verify a deterministic LIB-6 bundle directory.",
        "verify_bundle_directory(",
    ),
}
FORBIDDEN_TOKENS = {
    "src/lib/bundle/bundle_manifest.py": ("time.time(", "datetime.utcnow(", "uuid.uuid4(", "os.path.getmtime(", "random."),
    "src/lib/export/export_engine.py": ("time.time(", "datetime.utcnow(", "uuid.uuid4(", "os.path.getmtime(", "random."),
    "tools/lib/tool_verify_bundle.py": ("time.time(", "datetime.utcnow(", "uuid.uuid4(", "random."),
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
    related_paths = sorted(set(REQUIRED_TOKENS.keys()) | set(FORBIDDEN_TOKENS.keys()))
    for rel_path, tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="bundle.nondeterministic_archive_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required LIB-6 bundle/archive surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-BUNDLES-DETERMINISTIC",
                        "INV-NO-TIMESTAMPS-IN-ARCHIVES",
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
                    category="bundle.nondeterministic_archive_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing LIB-6 bundle determinism marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-BUNDLES-DETERMINISTIC",
                        "INV-NO-TIMESTAMPS-IN-ARCHIVES",
                    ],
                    related_paths=related_paths,
                )
            )
    for rel_path, tokens in FORBIDDEN_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            continue
        found = [token for token in tokens if token in text]
        if found:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="bundle.nondeterministic_archive_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["forbidden nondeterministic bundle/archive token(s): {}".format(", ".join(found[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-BUNDLES-DETERMINISTIC",
                        "INV-NO-TIMESTAMPS-IN-ARCHIVES",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
