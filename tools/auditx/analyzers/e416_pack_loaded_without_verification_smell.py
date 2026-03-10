"""E416 pack loaded without offline verification smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E416_PACK_LOADED_WITHOUT_VERIFICATION_SMELL"
REQUIRED_TOKENS = {
    "docs/packs/PACK_VERIFICATION_PIPELINE.md": (
        "Produce a deterministic `PackCompatibilityReport`.",
        "Generate a deterministic `pack_lock.json` when the report is valid.",
    ),
    "src/packs/compat/pack_verification_pipeline.py": (
        "def verify_pack_set(",
        "merge_overlay_view(",
        "build_verified_pack_lock(",
    ),
    "tools/setup/setup_cli.py": (
        "handle_verify(",
        "handle_build_lock(",
        "verify_pack_set(",
    ),
    "tools/launcher/launch.py": (
        "verify_pack_set(",
        "cmd_compat_status(",
        "\"pack_compatibility_report\"",
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
                    category="packs.pack_loaded_without_verification_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required pack verification surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-PACK-VERIFICATION-REQUIRED-BEFORE-LOAD",
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
                    category="packs.pack_loaded_without_verification_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing pack verification marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-PACK-VERIFICATION-REQUIRED-BEFORE-LOAD",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
