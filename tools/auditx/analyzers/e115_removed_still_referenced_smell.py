"""E115 removed-still-referenced smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E115_REMOVED_STILL_REFERENCED_SMELL"
DEPRECATIONS_REL = "data/governance/deprecations.json"
TOPOLOGY_REL = "docs/audit/TOPOLOGY_MAP.json"


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
    removed_ids = sorted(
        set(
            str(row.get("deprecated_id", "")).strip()
            for row in rows
            if str(row.get("deprecated_id", "")).strip() and str(row.get("status", "")).strip() == "removed"
        )
    )
    if not removed_ids:
        return findings

    topology_payload = _read_json(os.path.join(repo_root, TOPOLOGY_REL.replace("/", os.sep)))
    topology_text = json.dumps(topology_payload, sort_keys=True) if topology_payload else ""

    for deprecated_id in removed_ids:
        if topology_text and deprecated_id in topology_text:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.removed_still_referenced_smell",
                    severity="VIOLATION",
                    confidence=0.94,
                    file_path=TOPOLOGY_REL,
                    line=1,
                    evidence=[deprecated_id, "removed identifier still appears in topology map"],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-DEPRECATION-REGISTRY-VALID"],
                    related_paths=[TOPOLOGY_REL, DEPRECATIONS_REL],
                )
            )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))

