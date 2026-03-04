"""E218 missing explain contract smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E218_MISSING_EXPLAIN_CONTRACT_SMELL"
_EXPLAIN_REGISTRY_REL = "data/registries/explain_contract_registry.json"
_REQUIRED_EVENT_KINDS = (
    "elec.trip",
    "elec.fault",
    "therm.overheat",
    "therm.fire",
    "therm.runaway",
    "mob.derailment",
    "mob.collision",
    "mob.signal_violation",
    "sig.delivery_loss",
    "sig.jamming",
    "sig.decrypt_denied",
    "sig.trust_update",
    "mech.fracture",
    "fluid.relief",
    "fluid.leak",
    "fluid.burst",
    "fluid.cavitation",
    "phys.exception_event",
    "phys.energy_violation",
    "phys.momentum_violation",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    abs_path = os.path.join(repo_root, _EXPLAIN_REGISTRY_REL.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_explain_contract_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=_EXPLAIN_REGISTRY_REL,
                line=1,
                evidence=["explain_contract_registry missing or invalid"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-EXPLAIN-CONTRACT-REQUIRED"],
                related_paths=[_EXPLAIN_REGISTRY_REL],
            )
        )
        return findings

    rows = list((dict(payload.get("record") or {})).get("explain_contracts") or payload.get("explain_contracts") or [])
    declared_event_kinds = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        event_kind_id = str(row.get("event_kind_id", "")).strip()
        if event_kind_id:
            declared_event_kinds.add(event_kind_id)
        if not str(row.get("explain_artifact_type_id", "")).strip():
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.missing_explain_contract_smell",
                    severity="VIOLATION",
                    confidence=0.92,
                    file_path=_EXPLAIN_REGISTRY_REL,
                    line=1,
                    evidence=["explain contract missing explain_artifact_type_id", event_kind_id or "<unknown>"],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-EXPLAIN-CONTRACT-REQUIRED"],
                    related_paths=[_EXPLAIN_REGISTRY_REL],
                )
            )
            break
        if not list(row.get("required_inputs") or []):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.missing_explain_contract_smell",
                    severity="VIOLATION",
                    confidence=0.88,
                    file_path=_EXPLAIN_REGISTRY_REL,
                    line=1,
                    evidence=["explain contract missing required_inputs", event_kind_id or "<unknown>"],
                    suggested_classification="INVALID",
                    recommended_action="ADD_RULE",
                    related_invariants=["INV-EXPLAIN-CONTRACT-REQUIRED"],
                    related_paths=[_EXPLAIN_REGISTRY_REL],
                )
            )
            break

    for event_kind_id in sorted(set(_REQUIRED_EVENT_KINDS) - declared_event_kinds):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.missing_explain_contract_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=_EXPLAIN_REGISTRY_REL,
                line=1,
                evidence=["missing explain contract for event_kind_id '{}'".format(event_kind_id)],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-EXPLAIN-CONTRACT-REQUIRED"],
                related_paths=[_EXPLAIN_REGISTRY_REL],
            )
        )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
