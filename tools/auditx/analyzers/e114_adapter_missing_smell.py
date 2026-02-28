"""E114 adapter missing smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E114_ADAPTER_MISSING_SMELL"
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
    for row in rows:
        adapter_path = _norm(str(row.get("adapter_path", "")).strip())
        if not adapter_path:
            continue
        abs_adapter = os.path.join(repo_root, adapter_path.replace("/", os.sep))
        if os.path.isfile(abs_adapter):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.adapter_missing_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=DEPRECATIONS_REL,
                line=1,
                evidence=[adapter_path, "declared adapter_path missing on disk"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-DEPRECATION-REGISTRY-VALID", "INV-ADAPTER-ONLY-ACCESS"],
                related_paths=[DEPRECATIONS_REL, adapter_path],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))

