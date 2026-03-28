"""E419 silent migration smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E419_SILENT_MIGRATION_SMELL"
REQUIRED_TOKENS = {
    "compat/data_format_loader.py": (
        "REFUSAL_FORMAT_MIGRATION_MISSING",
        "\"migration_events\"",
        "\"read_only_applied\"",
        "REFUSAL_FORMAT_READ_ONLY_UNAVAILABLE",
    ),
    "tools/compat/tool_replay_migration.py": (
        "\"migration_events\"",
        "\"read_only_applied\"",
        "load_versioned_artifact(",
    ),
    "tools/xstack/sessionx/creator.py": (
        "stamp_artifact_metadata(",
        "artifact_kind=\"save_file\"",
    ),
    "tools/xstack/sessionx/script_runner.py": (
        "stamp_artifact_metadata(",
        "artifact_kind=\"save_file\"",
    ),
    "server/server_console.py": (
        "stamp_artifact_metadata(",
        "artifact_kind=\"save_file\"",
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
                    category="compat.silent_migration_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required migration logging surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-NO-SILENT-FORMAT-INTERPRETATION",
                        "INV-MIGRATIONS-LOGGED",
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
                    category="compat.silent_migration_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing migration marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-NO-SILENT-FORMAT-INTERPRETATION",
                        "INV-MIGRATIONS-LOGGED",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
