"""E237 missing tolerance smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E237_MISSING_TOLERANCE_SMELL"


class MissingToleranceSmell:
    analyzer_id = ANALYZER_ID


WATCH_PREFIXES = (
    "data/registries/quantity_registry.json",
    "data/registries/quantity_tolerance_registry.json",
)


def _read_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _quantity_ids(payload: dict):
    rows = list((dict(payload.get("record") or {})).get("quantities") or [])
    return sorted(
        str(row.get("quantity_id", "")).strip()
        for row in rows
        if isinstance(row, dict) and str(row.get("quantity_id", "")).strip()
    )


def _tolerance_ids(payload: dict):
    rows = list((dict(payload.get("record") or {})).get("quantity_tolerances") or [])
    if not rows:
        rows = list(payload.get("quantity_tolerances") or [])
    return sorted(
        str(row.get("quantity_id", "")).strip()
        for row in rows
        if isinstance(row, dict) and str(row.get("quantity_id", "")).strip()
    )


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files

    quantity_rel = "data/registries/quantity_registry.json"
    tolerance_rel = "data/registries/quantity_tolerance_registry.json"
    quantity_payload = _read_json(repo_root, quantity_rel)
    tolerance_payload = _read_json(repo_root, tolerance_rel)
    quantity_ids = _quantity_ids(quantity_payload)
    tolerance_ids = set(_tolerance_ids(tolerance_payload))

    findings = []
    if not quantity_ids:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_tolerance_smell",
                severity="RISK",
                confidence=0.95,
                file_path=quantity_rel,
                line=1,
                evidence=["quantity registry missing or empty; tolerance coverage cannot be validated"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="DOC_FIX",
                related_invariants=["INV-QUANTITY-TOLERANCE-DECLARED"],
                related_paths=[quantity_rel, tolerance_rel],
            )
        )
        return findings
    if not tolerance_ids:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_tolerance_smell",
                severity="RISK",
                confidence=0.95,
                file_path=tolerance_rel,
                line=1,
                evidence=["quantity tolerance registry missing or empty"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-QUANTITY-TOLERANCE-DECLARED"],
                related_paths=[quantity_rel, tolerance_rel],
            )
        )
        return findings

    missing = sorted(quantity_id for quantity_id in quantity_ids if quantity_id not in tolerance_ids)
    if missing:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_tolerance_smell",
                severity="RISK",
                confidence=0.98,
                file_path=tolerance_rel,
                line=1,
                evidence=[
                    "quantity tolerance declarations missing for registered quantities (count={})".format(len(missing)),
                    ",".join(missing[:8]),
                ],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-QUANTITY-TOLERANCE-DECLARED"],
                related_paths=[quantity_rel, tolerance_rel],
            )
        )
    return findings
