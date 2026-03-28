"""E443 pack-id-collision smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E443_PACK_ID_COLLISION_SMELL"
REQUIRED_TOKENS = {
    "docs/architecture/FORKING_AND_PROVIDES_MODEL.md": (
        "INV-FORKS-MUST-NAMESPACE",
        "fork.<origin_pack_id>.<fork_author>.<fork_name>",
        "forks must not reuse the origin pack_id",
    ),
    "schema/pack_manifest.schema": (
        "fork.<origin_pack_id>.<fork_author>.<fork_name>",
        "Legacy reverse-DNS pack ids remain loadable for compatibility.",
    ),
    "lib/provides/provider_resolution.py": (
        "classify_pack_namespace(",
        "REFUSAL_PACK_NAMESPACE_INVALID",
    ),
    "tools/xstack/pack_loader/loader.py": (
        "classify_pack_namespace(",
        "refuse.pack.invalid_namespace",
        "refuse.pack.duplicate_pack_id",
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
                category="provides.pack_id_collision_smell",
                severity="RISK",
                confidence=0.95,
                file_path=rel_path,
                line=1,
                evidence=["missing pack-namespace marker(s): {}".format(", ".join(missing[:4]))],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=[
                    "INV-FORKS-MUST-NAMESPACE",
                ],
                related_paths=related_paths,
            )
        )
    return findings
