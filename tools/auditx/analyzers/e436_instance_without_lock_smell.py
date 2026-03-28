"""E436 instance-without-lock smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E436_INSTANCE_WITHOUT_LOCK_SMELL"
REQUIRED_TOKENS = {
    "docs/architecture/INSTANCE_MODEL.md": (
        "INV-INSTANCE-USES-PACK-LOCK",
        "pack_lock_hash",
        "profile_bundle_hash",
    ),
    "schema/lib/instance_manifest.schema": (
        "pack_lock_hash",
        "profile_bundle_hash",
        "save_refs",
    ),
    "lib/instance/instance_validator.py": (
        "REFUSAL_INSTANCE_MISSING_LOCK",
        "REFUSAL_INSTANCE_MISSING_PROFILE_BUNDLE",
        "pack_lock_hash",
    ),
    "tools/launcher/launcher_cli.py": (
        "resolve_pack_lock(",
        "profile bundle artifact missing",
        "pack lock hash does not match instance manifest",
    ),
    "tools/ops/ops_cli.py": (
        "pack_lock_hash",
        "profile_bundle_hash",
        "build_instance_manifest_payload(",
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
                category="instance.instance_without_lock_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["missing instance lock/profile binding marker(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=[
                    "INV-INSTANCE-USES-PACK-LOCK",
                    "INV-INSTANCE-USES-PROFILE-BUNDLE",
                ],
                related_paths=related_paths,
            )
        )
    return findings
