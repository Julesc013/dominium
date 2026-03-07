"""E301 missing-reference-evaluator smell analyzer for META-REF0 enforcement."""

from __future__ import annotations

import json
import os
from typing import Mapping

from analyzers.base import make_finding


ANALYZER_ID = "E301_MISSING_REFERENCE_EVALUATOR_SMELL"
RULE_ID = "INV-CRITICAL-SUBSYSTEM-REF-AVAILABLE"

REGISTRY_REL = "data/registries/reference_evaluator_registry.json"
REQUIRED_EVALUATOR_IDS = (
    "ref.energy_ledger",
    "ref.coupling_scheduler",
    "ref.system_invariant_check",
    "ref.compiled_model_verify",
)
REQUIRED_PATHS = (
    "src/meta/reference/reference_engine.py",
    "tools/meta/tool_run_reference_suite.py",
)


class MissingReferenceEvaluatorSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _load_json(repo_root: str, rel_path: str) -> tuple[dict, str]:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, Mapping):
        return {}, "json root must be object"
    return dict(payload), ""


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files

    findings = []
    payload, err = _load_json(repo_root, REGISTRY_REL)
    if err:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="meta.reference.missing_registry",
                severity="VIOLATION",
                confidence=0.95,
                file_path=REGISTRY_REL,
                line=1,
                evidence=["reference evaluator registry missing or invalid: {}".format(err)],
                suggested_classification="BLOCKER",
                recommended_action="ADD_CONTRACT",
                related_invariants=[RULE_ID],
                related_paths=[REGISTRY_REL],
            )
        )
        return findings

    rows = list((dict(payload.get("record") or {})).get("reference_evaluators") or payload.get("reference_evaluators") or [])
    by_id = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        evaluator_id = str(row.get("evaluator_id", "")).strip()
        if evaluator_id:
            by_id[evaluator_id] = dict(row)

    for evaluator_id in REQUIRED_EVALUATOR_IDS:
        row = dict(by_id.get(evaluator_id) or {})
        if not row:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="meta.reference.missing_evaluator",
                    severity="RISK",
                    confidence=0.9,
                    file_path=REGISTRY_REL,
                    line=1,
                    evidence=["missing evaluator registration: {}".format(evaluator_id)],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_CONTRACT",
                    related_invariants=[RULE_ID],
                    related_paths=[REGISTRY_REL],
                )
            )
            continue
        status = str((dict(row.get("extensions") or {})).get("status", "active")).strip().lower() or "active"
        if status != "active":
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="meta.reference.inactive_evaluator",
                    severity="RISK",
                    confidence=0.88,
                    file_path=REGISTRY_REL,
                    line=1,
                    evidence=["critical evaluator must be active: {} status={}".format(evaluator_id, status)],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="REWRITE",
                    related_invariants=[RULE_ID],
                    related_paths=[REGISTRY_REL],
                )
            )

    for rel_path in REQUIRED_PATHS:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if os.path.isfile(abs_path):
            continue
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="meta.reference.missing_runtime_surface",
                severity="RISK",
                confidence=0.86,
                file_path=rel_path,
                line=1,
                evidence=["required reference surface missing: {}".format(rel_path)],
                suggested_classification="NEEDS_REVIEW",
                recommended_action="ADD_CONTRACT",
                related_invariants=[RULE_ID],
                related_paths=[_norm(rel_path), REGISTRY_REL],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
