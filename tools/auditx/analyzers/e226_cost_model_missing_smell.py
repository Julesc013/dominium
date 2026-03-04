"""E226 cost-model missing smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E226_COST_MODEL_MISSING_SMELL"
_TIER_REGISTRY_REL = "data/registries/tier_contract_registry.json"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    abs_path = os.path.join(repo_root, _TIER_REGISTRY_REL.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.cost_model_missing_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=_TIER_REGISTRY_REL,
                line=1,
                evidence=["tier_contract_registry missing or invalid"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-COST-MODEL-REQUIRED"],
                related_paths=[_TIER_REGISTRY_REL],
            )
        )
        return findings

    rows = list((dict(payload.get("record") or {})).get("tier_contracts") or payload.get("tier_contracts") or [])
    for row in rows:
        if not isinstance(row, dict):
            continue
        subsystem_id = str(row.get("subsystem_id", "")).strip().upper() or "<unknown>"
        if str(row.get("cost_model_id", "")).strip():
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.cost_model_missing_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=_TIER_REGISTRY_REL,
                line=1,
                evidence=["missing cost_model_id for subsystem '{}'".format(subsystem_id)],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-COST-MODEL-REQUIRED"],
                related_paths=[_TIER_REGISTRY_REL],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
