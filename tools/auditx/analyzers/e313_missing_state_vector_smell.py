"""E313 missing-state-vector smell analyzer for LOGIC elements."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E313_MISSING_STATE_VECTOR_SMELL"
WATCH_PREFIXES = (
    "tools/auditx/analyzers/e313_missing_state_vector_smell.py",
    "tools/auditx/analyzers/__init__.py",
    "packs/core/pack.core.logic_base/data/logic_element_registry.json",
    "packs/core/pack.core.logic_base/data/logic_state_vectors.json",
)


class MissingStateVectorSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    element_rel = "packs/core/pack.core.logic_base/data/logic_element_registry.json"
    statevec_rel = "packs/core/pack.core.logic_base/data/logic_state_vectors.json"
    element_payload = _load_json(repo_root, element_rel)
    statevec_payload = _load_json(repo_root, statevec_rel)
    element_rows = list(element_payload.get("logic_elements") or [])
    statevec_rows = list(statevec_payload.get("state_vector_definitions") or [])
    statevec_by_owner = {}
    for row in statevec_rows:
        if not isinstance(row, dict):
            continue
        owner_id = str(row.get("owner_id", "")).strip()
        if owner_id:
            statevec_by_owner[owner_id] = dict(row)

    for row in element_rows:
        if not isinstance(row, dict):
            continue
        element_id = str(row.get("element_id", "")).strip()
        declared_id = str(row.get("state_vector_definition_id", "")).strip()
        statevec_row = dict(statevec_by_owner.get(element_id) or {})
        observed_id = str(dict(statevec_row.get("extensions") or {}).get("state_vector_definition_id", "")).strip()
        if declared_id and statevec_row and declared_id == observed_id:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="logic.missing_state_vector_smell",
                severity="VIOLATION",
                confidence=0.97,
                file_path=statevec_rel,
                line=1,
                evidence=["logic element missing or mismatched explicit state vector declaration", element_id or "<missing>"],
                suggested_classification="INVALID",
                recommended_action="DECLARE_STATE_VECTOR",
                related_invariants=["INV-LOGIC-ELEMENT-STATEVEC-DECLARED"],
                related_paths=[element_rel, statevec_rel],
            )
        )

    return sorted(findings, key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity))
