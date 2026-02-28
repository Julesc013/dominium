"""E113 deprecated usage smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E113_DEPRECATED_USAGE_SMELL"
DEPRECATIONS_REL = "data/governance/deprecations.json"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json(path: str):
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []
    payload = _read_json(os.path.join(repo_root, DEPRECATIONS_REL.replace("/", os.sep)))
    rows = [row for row in list(payload.get("entries") or []) if isinstance(row, dict)]

    deprecated_ids = sorted(
        set(
            str(row.get("deprecated_id", "")).strip()
            for row in rows
            if str(row.get("deprecated_id", "")).strip()
            and str(row.get("status", "")).strip() in {"deprecated", "quarantined", "removed"}
        )
    )
    adapter_paths = sorted(
        set(
            _norm(str(row.get("adapter_path", "")).strip())
            for row in rows
            if str(row.get("adapter_path", "")).strip()
        )
    )
    if not deprecated_ids:
        return findings

    scan_roots = ("src", "engine", "game", "client", "server", "platform", "tools")
    scan_exts = (".py", ".c", ".cc", ".cpp", ".h", ".hh", ".hpp", ".json", ".schema", ".schema.json")
    skip_prefixes = (
        "docs/",
        "build/",
        "dist/",
        "tools/xstack/testx/tests/",
        "tools/auditx/analyzers/",
    )

    for root in scan_roots:
        abs_root = os.path.join(repo_root, root)
        if not os.path.isdir(abs_root):
            continue
        for walk_root, dirs, files in os.walk(abs_root):
            dirs[:] = sorted(token for token in dirs if not token.startswith(".") and token != "__pycache__")
            for name in sorted(files):
                if not name.endswith(scan_exts):
                    continue
                abs_path = os.path.join(walk_root, name)
                rel_path = _norm(os.path.relpath(abs_path, repo_root))
                if rel_path == DEPRECATIONS_REL or rel_path in adapter_paths:
                    continue
                if rel_path.startswith(skip_prefixes):
                    continue
                try:
                    text = open(abs_path, "r", encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                if not text:
                    continue
                for deprecated_id in deprecated_ids:
                    if deprecated_id not in text:
                        continue
                    findings.append(
                        make_finding(
                            analyzer_id=ANALYZER_ID,
                            category="architecture.deprecated_usage_smell",
                            severity="RISK",
                            confidence=0.9,
                            file_path=rel_path,
                            line=1,
                            evidence=[deprecated_id, "reference to deprecated/quarantined/removed identifier"],
                            suggested_classification="NEEDS_REVIEW",
                            recommended_action="REWRITE",
                            related_invariants=["INV-NO-NEW-USE-OF-DEPRECATED"],
                            related_paths=[rel_path, DEPRECATIONS_REL],
                        )
                    )
                    break

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))

