"""E387 silent semantic change smell analyzer."""

from __future__ import annotations

import json
import os
import re

from analyzers.base import make_finding


ANALYZER_ID = "E387_SILENT_SEMANTIC_CHANGE_SMELL"
WATCH_PREFIXES = ("docs/", "src/", "tools/", "data/", "schema/", "schemas/")
REGISTRY_REL = "data/registries/semantic_contract_registry.json"
TOKEN_RE = re.compile(r"\b(contract\.[a-z0-9_.]+\.v[0-9]+)\b")
SCAN_EXTS = (".md", ".txt", ".py", ".json", ".schema", ".schema.json")


def _read_text(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _load_registry_ids(repo_root: str):
    abs_path = os.path.join(repo_root, REGISTRY_REL.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    rows = (((payload.get("record") or {}).get("contracts")) or []) if isinstance(payload, dict) else []
    return {
        str(row.get("contract_id", "")).strip()
        for row in rows
        if isinstance(row, dict) and str(row.get("contract_id", "")).strip()
    }


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    registry_ids = _load_registry_ids(repo_root)
    if not registry_ids:
        return [
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="compat.silent_semantic_change_smell",
                severity="RISK",
                confidence=0.98,
                file_path=REGISTRY_REL,
                line=1,
                evidence=["semantic contract registry missing or unreadable"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="RESTORE",
                related_invariants=["INV-NO-UNVERSIONED-BEHAVIOR-CHANGE", "INV-NEW-CONTRACT-REQUIRES-ENTRY"],
                related_paths=[REGISTRY_REL],
            )
        ]

    findings = []
    scan_roots = (
        os.path.join(repo_root, "docs"),
        os.path.join(repo_root, "src"),
        os.path.join(repo_root, "tools"),
        os.path.join(repo_root, "data"),
        os.path.join(repo_root, "schema"),
        os.path.join(repo_root, "schemas"),
    )
    for root in scan_roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [name for name in dirnames if name not in ("build", "dist", ".git", "__pycache__", ".xstack_cache")]
            for name in sorted(filenames):
                if not any(name.endswith(ext) for ext in SCAN_EXTS):
                    continue
                abs_path = os.path.join(dirpath, name)
                rel_path = os.path.relpath(abs_path, repo_root).replace("\\", "/")
                text = _read_text(abs_path)
                missing = sorted({token for token in TOKEN_RE.findall(text) if token not in registry_ids})
                if not missing:
                    continue
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="compat.silent_semantic_change_smell",
                        severity="RISK",
                        confidence=0.94,
                        file_path=rel_path,
                        line=1,
                        evidence=["semantic contract token(s) missing registry entry: {}".format(", ".join(missing[:4]))],
                        suggested_classification="TODO-BLOCKED",
                        recommended_action="REWRITE",
                        related_invariants=["INV-NO-UNVERSIONED-BEHAVIOR-CHANGE", "INV-NEW-CONTRACT-REQUIRES-ENTRY"],
                        related_paths=[REGISTRY_REL, rel_path],
                    )
                )
    return findings
