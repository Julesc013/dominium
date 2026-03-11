"""E437 save-locked-to-instance smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E437_SAVE_LOCKED_TO_INSTANCE_SMELL"
REQUIRED_TOKENS = {
    "docs/architecture/INSTANCE_MODEL.md": (
        "INV-SAVES-NOT-EMBEDDED-IN-INSTANCE",
        "save_refs",
        "do not own saves",
    ),
    "docs/architecture/BUNDLE_MODEL.md": (
        "save_refs",
        "must not be embedded",
        "instance bundle",
    ),
    "tools/ops/ops_cli.py": (
        "clone_ignore_entries",
        "\"saves\"",
        "save_refs",
    ),
    "tools/share/share_cli.py": (
        "save_refs",
        "copy_tree(bundle_instance_root, args.out)",
        "linked_manifest[\"embedded_builds\"] = {}",
    ),
    "tools/launcher/launcher_cli.py": (
        "selected_save_id",
        "save_refs",
        "requested save is not associated with this instance",
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
                category="instance.save_locked_to_instance_smell",
                severity="RISK",
                confidence=0.94,
                file_path=rel_path,
                line=1,
                evidence=["missing save/reference portability marker(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[
                    "INV-SAVES-NOT-EMBEDDED-IN-INSTANCE",
                ],
                related_paths=related_paths,
            )
        )
    return findings
