"""E386 semantic behavior-without-contract smell analyzer."""

from __future__ import annotations

import os

from analyzers.base import make_finding


ANALYZER_ID = "E386_BEHAVIOR_WITHOUT_CONTRACT_SMELL"
WATCH_PREFIXES = (
    "data/registries/semantic_contract_registry.json",
    "schema/universe/universe_contract_bundle.schema",
    "schemas/universe_contract_bundle.schema.json",
    "tools/xstack/sessionx/creator.py",
    "tools/compatx/core/semantic_contract_validator.py",
    "docs/contracts/SEMANTIC_CONTRACT_MODEL.md",
)

REQUIRED_FILE_TOKENS = {
    "data/registries/semantic_contract_registry.json": (
        '"contract.worldgen.refinement.v1"',
        '"contract.overlay.merge.v1"',
        '"contract.logic.eval.v1"',
    ),
    "schema/universe/universe_contract_bundle.schema": (
        "record universe_contract_bundle",
        "contract_worldgen_refinement_version",
        "contract_appshell_lifecycle_version",
    ),
    "schemas/universe_contract_bundle.schema.json": (
        '"contract_worldgen_refinement_version"',
        '"contract_appshell_lifecycle_version"',
        '"deterministic_fingerprint"',
    ),
    "tools/xstack/sessionx/creator.py": (
        "build_default_universe_contract_bundle(",
        "validate_universe_contract_bundle(",
        '"universe_contract_bundle_path"',
    ),
    "tools/compatx/core/semantic_contract_validator.py": (
        "validate_replay_contract_match(",
        "build_semantic_contract_proof_bundle(",
        "refuse.semantic_contract_mismatch",
    ),
    "docs/contracts/SEMANTIC_CONTRACT_MODEL.md": (
        "Semantic contracts version behavior meaning, not payload shape.",
        "Universe creation writes an immutable sidecar: `universe_contract_bundle.json`.",
        "No runtime behavior change is authorized by this document.",
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
    related_paths = list(REQUIRED_FILE_TOKENS.keys())
    for rel_path, tokens in REQUIRED_FILE_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.behavior_without_contract_smell",
                    severity="RISK",
                    confidence=0.98,
                    file_path=rel_path,
                    line=1,
                    evidence=["required semantic-contract surface is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-CONTRACT-PINNED-IN-UNIVERSE"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.behavior_without_contract_smell",
                    severity="RISK",
                    confidence=0.96,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing semantic-contract marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-CONTRACT-PINNED-IN-UNIVERSE"],
                    related_paths=related_paths,
                )
            )
    return findings
