"""E261 missing invariant template smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E261_MISSING_INVARIANT_TEMPLATE_SMELL"


class MissingInvariantTemplateSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _read_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    schema_rel = "schema/system/boundary_invariant.schema"
    registry_rel = "data/registries/boundary_invariant_template_registry.json"
    validation_rel = "src/system/system_validation_engine.py"

    schema_text = _read_text(repo_root, schema_rel)
    for token in (
        "invariant_kind:",
        "tolerance_policy_id:",
        "boundary_flux_allowed:",
        "ledger_transform_required:",
    ):
        if token in schema_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_invariant_template_smell",
                severity="RISK",
                confidence=0.95,
                file_path=schema_rel,
                line=1,
                evidence=["missing required boundary invariant field token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SYSTEM-INVARIANTS-REQUIRED"],
                related_paths=[schema_rel, registry_rel, validation_rel],
            )
        )

    registry_payload = _read_json(repo_root, registry_rel)
    template_rows = list((dict(registry_payload.get("record") or {})).get("boundary_invariant_templates") or [])
    template_ids = set(
        str(row.get("boundary_invariant_template_id", "")).strip()
        for row in template_rows
        if isinstance(row, dict) and str(row.get("boundary_invariant_template_id", "")).strip()
    )
    for template_id in (
        "inv.mass_energy_basic",
        "inv.energy_pollution_basic",
        "inv.momentum_basic",
        "inv.safety_failsafe_required",
    ):
        if template_id in template_ids:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_invariant_template_smell",
                severity="RISK",
                confidence=0.93,
                file_path=registry_rel,
                line=1,
                evidence=["required boundary invariant template missing", template_id],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SYSTEM-INVARIANTS-REQUIRED"],
                related_paths=[registry_rel, schema_rel, validation_rel],
            )
        )

    validation_text = _read_text(repo_root, validation_rel)
    for token in (
        "def validate_boundary_invariants(",
        "invariant.template.present",
        "invariant.template.required",
        "invariant.required_safety_pattern.present",
        "invariant.required_safety_pattern.registered",
    ):
        if token in validation_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_invariant_template_smell",
                severity="RISK",
                confidence=0.9,
                file_path=validation_rel,
                line=1,
                evidence=["boundary invariant validation token missing", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-SYSTEM-INVARIANTS-REQUIRED"],
                related_paths=[validation_rel, registry_rel],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
