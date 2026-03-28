"""E392 undeclared extension interpretation smell analyzer."""

from __future__ import annotations

import json
import os
import pathlib
import re

from analyzers.base import make_finding


ANALYZER_ID = "E392_UNDECLARED_EXTENSION_INTERPRETATION_SMELL"
REGISTRY_REL = "data/registries/extension_interpretation_registry.json"
ENGINE_REL = "meta_extensions_engine.py"
DOC_REL = "docs/meta/EXTENSION_DISCIPLINE.md"
GET_RE = re.compile(r'extensions\s*\.\s*get\(\s*["\']([^"\']+)["\']')


def _load_registry(repo_root: str) -> dict:
    abs_path = os.path.join(repo_root, REGISTRY_REL.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _registry_keys(payload: dict) -> set[str]:
    rows = list((((payload.get("record") or {}).get("extension_interpretations")) or [])) if isinstance(payload, dict) else []
    out = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        extension_key = str(row.get("extension_key", "")).strip()
        if extension_key:
            out.add(extension_key)
        legacy = str(dict(row.get("extensions") or {}).get("legacy_alias_for", "")).strip()
        if legacy:
            out.add(legacy)
    return out


def _scan_extension_get_literals(repo_root: str) -> list[tuple[str, int, str]]:
    out: list[tuple[str, int, str]] = []
    for subtree in ("src", "tools"):
        base = pathlib.Path(repo_root) / subtree
        if not base.is_dir():
            continue
        for path in base.rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for line_no, line in enumerate(text.splitlines(), start=1):
                if "extensions" not in line or ".get(" not in line:
                    continue
                match = GET_RE.search(line)
                if not match:
                    continue
                out.append((str(path.relative_to(repo_root)).replace("\\", "/"), line_no, str(match.group(1)).strip()))
    return sorted(out)


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    related_paths = [REGISTRY_REL, ENGINE_REL, DOC_REL]
    payload = _load_registry(repo_root)
    if not payload:
        return [
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="compat.undeclared_extension_interpretation_smell",
                severity="RISK",
                confidence=0.98,
                file_path=REGISTRY_REL,
                line=1,
                evidence=["extension interpretation registry is missing or invalid"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-NO-EXTENSION-INTERPRETATION-WITHOUT-REGISTRY"],
                related_paths=related_paths,
            )
        ]

    registry_keys = _registry_keys(payload)
    text = open(os.path.join(repo_root, ENGINE_REL.replace("/", os.sep)), "r", encoding="utf-8", errors="ignore").read()
    if "extensions_get(" not in text:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="compat.undeclared_extension_interpretation_smell",
                severity="RISK",
                confidence=0.97,
                file_path=ENGINE_REL,
                line=1,
                evidence=["registry-backed extension accessor is missing"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-NO-EXTENSION-INTERPRETATION-WITHOUT-REGISTRY"],
                related_paths=related_paths,
            )
        )

    for rel_path, line_no, key in _scan_extension_get_literals(repo_root):
        if key in registry_keys:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="compat.undeclared_extension_interpretation_smell",
                severity="RISK",
                confidence=0.99,
                file_path=rel_path,
                line=line_no,
                evidence=["extension key '{}' is interpreted without a registry declaration".format(key)],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-NO-EXTENSION-INTERPRETATION-WITHOUT-REGISTRY"],
                related_paths=related_paths + [rel_path],
            )
        )
        break
    return findings
