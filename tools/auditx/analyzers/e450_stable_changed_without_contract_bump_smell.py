"""E450 stable registry change without semantic contract bump smell analyzer."""

from __future__ import annotations

import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)

from analyzers.base import make_finding


ANALYZER_ID = "E450_STABLE_CHANGED_WITHOUT_CONTRACT_BUMP_SMELL"
RULE_ID = "INV-STABLE-REQUIRES-CONTRACT-ID"
SEMANTIC_CONTRACT_REGISTRY_REL = "data/registries/semantic_contract_registry.json"
STABLE_WATCH_RELS = (
    "data/registries/capability_fallback_registry.json",
    "data/registries/compat_mode_registry.json",
    "data/registries/degrade_ladder_registry.json",
    "data/registries/protocol_registry.json",
)
WATCH_PREFIXES = STABLE_WATCH_RELS + (SEMANTIC_CONTRACT_REGISTRY_REL,)


def run(graph, repo_root, changed_files=None):
    del graph, repo_root
    changed = {
        str(path).replace("\\", "/").strip()
        for path in list(changed_files or [])
        if str(path).strip()
    }
    if not changed:
        return []
    if SEMANTIC_CONTRACT_REGISTRY_REL in changed:
        return []
    findings = []
    for rel_path in STABLE_WATCH_RELS:
        if rel_path not in changed:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="meta.stable_changed_without_contract_bump_smell",
                severity="RISK",
                confidence=0.9,
                file_path=rel_path,
                evidence=[
                    "stable negotiation registry changed without a semantic contract registry update in the same diff",
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=[RULE_ID],
                related_paths=[rel_path, SEMANTIC_CONTRACT_REGISTRY_REL],
            )
        )
    return findings
