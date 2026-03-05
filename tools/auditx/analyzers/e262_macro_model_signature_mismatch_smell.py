"""E262 macro model signature mismatch smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E262_MACRO_MODEL_SIGNATURE_MISMATCH_SMELL"


class MacroModelSignatureMismatchSmell:
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

    macro_set_schema_rel = "schema/system/macro_model_set.schema"
    macro_capsule_schema_rel = "schema/system/macro_capsule.schema"
    macro_registry_rel = "data/registries/macro_model_set_registry.json"
    validation_rel = "src/system/system_validation_engine.py"

    macro_set_schema_text = _read_text(repo_root, macro_set_schema_rel)
    for token in (
        '"macro_model_set_id"',
        '"model_bindings"',
        '"error_bound_policy_id"',
    ):
        if token in macro_set_schema_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.macro_model_signature_mismatch_smell",
                severity="RISK",
                confidence=0.95,
                file_path=macro_set_schema_rel,
                line=1,
                evidence=["macro model set schema missing required token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-MACRO-MODEL-SET-REQUIRED-FOR-CAPSULE"],
                related_paths=[macro_set_schema_rel, macro_capsule_schema_rel, validation_rel],
            )
        )

    macro_capsule_schema_text = _read_text(repo_root, macro_capsule_schema_rel)
    for token in ('"macro_model_set_id"', '"model_error_bounds_ref"'):
        if token in macro_capsule_schema_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.macro_model_signature_mismatch_smell",
                severity="RISK",
                confidence=0.93,
                file_path=macro_capsule_schema_rel,
                line=1,
                evidence=["macro capsule schema missing required macro signature token", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-MACRO-MODEL-SET-REQUIRED-FOR-CAPSULE"],
                related_paths=[macro_capsule_schema_rel, macro_set_schema_rel, validation_rel],
            )
        )

    registry_payload = _read_json(repo_root, macro_registry_rel)
    macro_sets = (dict(registry_payload.get("record") or {})).get("macro_model_sets")
    if not isinstance(macro_sets, list):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.macro_model_signature_mismatch_smell",
                severity="RISK",
                confidence=0.9,
                file_path=macro_registry_rel,
                line=1,
                evidence=["macro_model_sets list missing from registry", "record.macro_model_sets"],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-MACRO-MODEL-SET-REQUIRED-FOR-CAPSULE"],
                related_paths=[macro_registry_rel, validation_rel],
            )
        )

    validation_text = _read_text(repo_root, validation_rel)
    for token in (
        "def validate_macro_model_set(",
        "macro.model_set.present",
        "macro.error_bound_policy.registered",
        "macro.binding.input_port.match",
        "macro.binding.output_port.match",
    ):
        if token in validation_text:
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.macro_model_signature_mismatch_smell",
                severity="RISK",
                confidence=0.9,
                file_path=validation_rel,
                line=1,
                evidence=["macro model signature validation token missing", token],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="REWRITE",
                related_invariants=["INV-MACRO-MODEL-SET-REQUIRED-FOR-CAPSULE"],
                related_paths=[validation_rel, macro_set_schema_rel, macro_registry_rel],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
