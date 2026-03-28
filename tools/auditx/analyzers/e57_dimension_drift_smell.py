"""E57 dimension drift smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E57_DIMENSION_DRIFT_SMELL"
DIMENSION_REGISTRY_PATH = "data/registries/dimension_registry.json"
UNIT_REGISTRY_PATH = "data/registries/unit_registry.json"
QUANTITY_TYPE_REGISTRY_PATH = "data/registries/quantity_type_registry.json"
LEDGER_ENGINE_PATH = "reality/ledger/ledger_engine.py"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}


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

    dimension_payload = _read_json(repo_root, DIMENSION_REGISTRY_PATH)
    unit_payload = _read_json(repo_root, UNIT_REGISTRY_PATH)
    quantity_type_payload = _read_json(repo_root, QUANTITY_TYPE_REGISTRY_PATH)

    dimension_rows = list(((dimension_payload.get("record") or {}).get("dimensions") or []))
    unit_rows = list(((unit_payload.get("record") or {}).get("units") or []))
    quantity_type_rows = list(((quantity_type_payload.get("record") or {}).get("quantity_types") or []))

    dimension_ids = set(
        str(row.get("dimension_id", "")).strip()
        for row in dimension_rows
        if isinstance(row, dict) and str(row.get("dimension_id", "")).strip()
    )
    unit_ids = set(
        str(row.get("unit_id", "")).strip()
        for row in unit_rows
        if isinstance(row, dict) and str(row.get("unit_id", "")).strip()
    )
    unit_dimension_by_id = {
        str(row.get("unit_id", "")).strip(): str(row.get("dimension_id", "")).strip()
        for row in unit_rows
        if isinstance(row, dict) and str(row.get("unit_id", "")).strip()
    }

    if not dimension_ids or not unit_ids or not quantity_type_rows:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.dimension_drift_smell",
                severity="RISK",
                confidence=0.84,
                file_path=QUANTITY_TYPE_REGISTRY_PATH,
                line=1,
                evidence=["dimension/unit/quantity-type registries are missing or empty"],
                suggested_classification="TODO-BLOCKED",
                recommended_action="ADD_RULE",
                related_invariants=["INV-DIMENSION-COMPATIBILITY-ENFORCED", "INV-QUANTITY-TYPE-DECLARED"],
                related_paths=[DIMENSION_REGISTRY_PATH, UNIT_REGISTRY_PATH, QUANTITY_TYPE_REGISTRY_PATH],
            )
        )

    for row in sorted((item for item in quantity_type_rows if isinstance(item, dict)), key=lambda item: str(item.get("quantity_id", ""))):
        quantity_id = str(row.get("quantity_id", "")).strip()
        dimension_id = str(row.get("dimension_id", "")).strip()
        default_unit_id = str(row.get("default_unit_id", "")).strip()
        if dimension_id and dimension_id not in dimension_ids:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.dimension_drift_smell",
                    severity="VIOLATION",
                    confidence=0.96,
                    file_path=QUANTITY_TYPE_REGISTRY_PATH,
                    line=1,
                    evidence=["quantity type references unknown dimension_id", "quantity_id={},dimension_id={}".format(quantity_id, dimension_id)],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-DIMENSION-COMPATIBILITY-ENFORCED"],
                    related_paths=[QUANTITY_TYPE_REGISTRY_PATH, DIMENSION_REGISTRY_PATH],
                )
            )
        if default_unit_id and default_unit_id not in unit_ids:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="materials.dimension_drift_smell",
                    severity="VIOLATION",
                    confidence=0.96,
                    file_path=QUANTITY_TYPE_REGISTRY_PATH,
                    line=1,
                    evidence=["quantity type references unknown default_unit_id", "quantity_id={},default_unit_id={}".format(quantity_id, default_unit_id)],
                    suggested_classification="INVALID",
                    recommended_action="REWRITE",
                    related_invariants=["INV-DIMENSION-COMPATIBILITY-ENFORCED"],
                    related_paths=[QUANTITY_TYPE_REGISTRY_PATH, UNIT_REGISTRY_PATH],
                )
            )
        if default_unit_id in unit_dimension_by_id:
            unit_dimension_id = str(unit_dimension_by_id.get(default_unit_id, "")).strip()
            if unit_dimension_id and dimension_id and unit_dimension_id != dimension_id:
                findings.append(
                    make_finding(
                        analyzer_id=ANALYZER_ID,
                        category="materials.dimension_drift_smell",
                        severity="VIOLATION",
                        confidence=0.97,
                        file_path=QUANTITY_TYPE_REGISTRY_PATH,
                        line=1,
                        evidence=[
                            "quantity type dimension does not match default unit dimension",
                            "quantity_id={},dimension_id={},default_unit_id={},unit_dimension_id={}".format(
                                quantity_id,
                                dimension_id,
                                default_unit_id,
                                unit_dimension_id,
                            ),
                        ],
                        suggested_classification="INVALID",
                        recommended_action="REWRITE",
                        related_invariants=["INV-DIMENSION-COMPATIBILITY-ENFORCED"],
                        related_paths=[QUANTITY_TYPE_REGISTRY_PATH, UNIT_REGISTRY_PATH, DIMENSION_REGISTRY_PATH],
                    )
                )

    ledger_text = _read_text(repo_root, LEDGER_ENGINE_PATH)
    for token in ("quantity_type_registry", "refusal.dimension.mismatch"):
        if token in ledger_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="materials.dimension_drift_smell",
                severity="RISK",
                confidence=0.82,
                file_path=LEDGER_ENGINE_PATH,
                line=1,
                evidence=["ledger engine missing required dimension enforcement token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_RULE",
                related_invariants=["INV-DIMENSION-COMPATIBILITY-ENFORCED"],
                related_paths=[LEDGER_ENGINE_PATH],
            )
        )

    return sorted(
        findings,
        key=lambda item: (
            _norm(item.location.file_path),
            item.location.line_start,
            item.severity,
        ),
    )
