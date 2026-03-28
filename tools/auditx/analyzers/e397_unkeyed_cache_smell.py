"""E397 unkeyed refinement-cache smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E397_UNKEYED_CACHE_SMELL"
REQUIRED_TOKENS = {
    "worldgen/refinement/refinement_cache.py": (
        "universe_contract_bundle_hash",
        "overlay_manifest_hash",
        "mod_policy_id",
        "refinement_level",
    ),
    "geo/worldgen/worldgen_engine.py": (
        "build_refinement_cache_key(",
        "universe_contract_bundle_hash",
        "overlay_manifest_hash",
        "mod_policy_id",
        "cache_key",
    ),
    "tools/xstack/sessionx/process_runtime.py": (
        "EXPLAIN_CONTRACT_MISMATCH_CACHE",
        "universe_contract_bundle_hash",
        "overlay_manifest_hash",
        "mod_policy_id",
    ),
    "docs/worldgen/REFINEMENT_PIPELINE_MODEL.md": (
        "contract_bundle_hash",
        "overlay_manifest_hash",
        "mod_policy_id",
        "cache_key = H(",
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
                    category="worldgen.unkeyed_cache_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required MW-4 cache-key surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=[
                        "INV-CACHE-KEY-INCLUDES-CONTRACTS",
                        "INV-REFINEMENT-BUDGETED",
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
                    category="worldgen.unkeyed_cache_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing MW-4 cache-key marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-CACHE-KEY-INCLUDES-CONTRACTS",
                        "INV-REFINEMENT-BUDGETED",
                    ],
                    related_paths=related_paths,
                )
            )
    return findings
