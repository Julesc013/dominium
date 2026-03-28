"""E391 bare extension key smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E391_BARE_EXTENSION_KEY_SMELL"
REGISTRY_REL = "data/registries/extension_interpretation_registry.json"
ENGINE_REL = "meta_extensions_engine.py"
WRAPPER_REL = "meta/extensions/extensions_engine.py"
DOC_REL = "docs/meta/EXTENSION_DISCIPLINE.md"
MIGRATION_DOC_REL = "docs/meta/EXTENSION_MIGRATION_NOTES.md"
REQUIRED_TOKENS = {
    ENGINE_REL: (
        "legacy_alias_for_key(",
        "normalize_extensions_map(",
        "normalize_extensions_tree(",
        "DEFAULT_EXTENSION_POLICY_ID",
        "STRICT_EXTENSION_POLICY_ID",
    ),
    DOC_REL: (
        "official.*",
        "mod.<pack_id>.*",
        "dev.*",
        "Unknown keys have no authoritative effect in `extensions.default`.",
    ),
    MIGRATION_DOC_REL: (
        "mod.unknown.<key>",
        "extensions.default",
        "extensions.strict",
    ),
    WRAPPER_REL: (
        "from meta_extensions_engine import (",
        "extensions_get",
        "normalize_extensions_tree",
    ),
}


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _load_registry(repo_root: str) -> dict:
    abs_path = os.path.join(repo_root, REGISTRY_REL.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    related_paths = [REGISTRY_REL, ENGINE_REL, WRAPPER_REL, DOC_REL, MIGRATION_DOC_REL]

    for rel_path, required_tokens in REQUIRED_TOKENS.items():
        text = _read_text(repo_root, rel_path)
        if not text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.bare_extension_key_smell",
                    severity="RISK",
                    confidence=0.97,
                    file_path=rel_path,
                    line=1,
                    evidence=["required extension-discipline artifact is missing"],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="RESTORE",
                    related_invariants=["INV-EXTENSIONS-NAMESPACED"],
                    related_paths=related_paths,
                )
            )
            continue
        missing = [token for token in required_tokens if token not in text]
        if missing:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="compat.bare_extension_key_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path=rel_path,
                    line=1,
                    evidence=["missing extension-discipline marker(s): {}".format(", ".join(missing[:4]))],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-EXTENSIONS-NAMESPACED"],
                    related_paths=related_paths,
                )
            )

    payload = _load_registry(repo_root)
    rows = list((((payload.get("record") or {}).get("extension_interpretations")) or [])) if isinstance(payload, dict) else []
    if not rows:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="compat.bare_extension_key_smell",
                severity="RISK",
                confidence=0.98,
                file_path=REGISTRY_REL,
                line=1,
                evidence=["extension interpretation registry is empty"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-EXTENSIONS-NAMESPACED"],
                related_paths=related_paths,
            )
        )
        return findings

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            continue
        extension_key = str(row.get("extension_key", "")).strip()
        if extension_key.startswith(("official.", "dev.", "mod.")):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="compat.bare_extension_key_smell",
                severity="RISK",
                confidence=0.99,
                file_path=REGISTRY_REL,
                line=index + 1,
                evidence=["registry row is not namespaced: {}".format(extension_key)],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-EXTENSIONS-NAMESPACED"],
                related_paths=related_paths,
            )
        )
        break
    return findings
