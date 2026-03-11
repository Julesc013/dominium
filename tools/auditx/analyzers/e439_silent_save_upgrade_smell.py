"""E439 silent-save-upgrade smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E439_SILENT_SAVE_UPGRADE_SMELL"
REQUIRED_TOKENS = {
    "docs/architecture/SAVE_MODEL.md": (
        "INV-NO-SILENT-MIGRATION",
        "explicit invoke-only",
        "Silent save upgrades are forbidden.",
    ),
    "schema/lib/migration_event.schema": (
        "migration application remains explicit invoke-only",
        "tick_applied",
        "migration_id",
    ),
    "src/lib/save/save_validator.py": (
        "migrate_save_manifest(",
        "allow_save_migration",
        "REFUSAL_SAVE_MIGRATION_REQUIRED",
    ),
    "tools/launcher/launcher_cli.py": (
        "--allow-save-migration",
        "--save-migration-id",
        "--migration-tick",
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
                category="save.silent_save_upgrade_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["missing explicit save-migration marker(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=[
                    "INV-NO-SILENT-MIGRATION",
                ],
                related_paths=related_paths,
            )
        )
    return findings
