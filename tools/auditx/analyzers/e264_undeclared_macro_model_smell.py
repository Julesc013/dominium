"""E264 undeclared macro model smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E264_UNDECLARED_MACRO_MODEL_SMELL"


class UndeclaredMacroModelSmell:
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

    macro_registry_rel = "data/registries/macro_model_set_registry.json"
    macro_schema_rel = "schema/system/macro_capsule.schema"
    collapse_rel = "src/system/system_collapse_engine.py"
    validation_rel = "src/system/system_validation_engine.py"

    required_ids = {
        "macro.engine_stub",
        "macro.pump_stub",
        "macro.generator_stub",
        "macro.heat_exchanger_stub",
    }

    registry_payload = _read_json(repo_root, macro_registry_rel)
    macro_sets = (dict(registry_payload.get("record") or {})).get("macro_model_sets")
    if not isinstance(macro_sets, list):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.undeclared_macro_model_smell",
                severity="RISK",
                confidence=0.96,
                file_path=macro_registry_rel,
                line=1,
                evidence=["macro model set registry payload missing list", "record.macro_model_sets"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-CAPSULE-BEHAVIOR-MODEL-ONLY"],
                related_paths=[macro_registry_rel, validation_rel],
            )
        )
        macro_ids = set()
    else:
        macro_ids = set(
            str(row.get("macro_model_set_id", "")).strip()
            for row in macro_sets
            if isinstance(row, dict) and str(row.get("macro_model_set_id", "")).strip()
        )
    for macro_model_set_id in sorted(required_ids):
        if macro_model_set_id in macro_ids:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.undeclared_macro_model_smell",
                severity="RISK",
                confidence=0.9,
                file_path=macro_registry_rel,
                line=1,
                evidence=["required SYS-2 starter macro model set missing", macro_model_set_id],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-CAPSULE-BEHAVIOR-MODEL-ONLY"],
                related_paths=[macro_registry_rel],
            )
        )

    for rel_path, token in (
        (macro_schema_rel, "macro_model_set_id:"),
        (macro_schema_rel, "model_error_bounds_ref:"),
        (collapse_rel, "macro_model_set_id"),
        (collapse_rel, "model_error_bounds_ref"),
        (validation_rel, "def validate_macro_model_set("),
        (validation_rel, "macro.model_set.present"),
    ):
        if token in _read_text(repo_root, rel_path):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.undeclared_macro_model_smell",
                severity="RISK",
                confidence=0.9,
                file_path=rel_path,
                line=1,
                evidence=["macro model declaration token missing", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-CAPSULE-BEHAVIOR-MODEL-ONLY"],
                related_paths=[macro_schema_rel, collapse_rel, validation_rel],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

