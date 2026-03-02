"""E163 substrate bypass smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E163_SUBSTRATE_BYPASS_SMELL"


class SubstrateBypassSmell:
    analyzer_id = ANALYZER_ID


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _load_registry(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return dict(payload.get("record") or payload)


def _declared_substrates(row: dict) -> set[str]:
    values = row.get("affected_substrates")
    if not isinstance(values, list):
        return set()
    out = set()
    for value in values:
        token = str(value or "").strip()
        if token:
            out.add(token)
    return out


def _infer_expected_substrates(template_row: dict) -> set[str]:
    tokens = " ".join(
        [
            str(template_row.get("action_template_id", "")),
            str((dict(template_row.get("extensions") or {})).get("process_id", "")),
            str((dict(template_row.get("extensions") or {})).get("action_id", "")),
            str((dict(template_row.get("extensions") or {})).get("interaction_action_id", "")),
            str((dict(template_row.get("extensions") or {})).get("task_type_id", "")),
        ]
    ).lower()
    expected: set[str] = set()
    if any(token in tokens for token in ("flow", "flood", "smoke", "pressure", "vent")):
        expected.add("Flow")
    if any(token in tokens for token in ("field", "wind", "temperature", "moisture", "friction", "visibility", "radiation")):
        expected.add("Field")
    if any(token in tokens for token in ("struct", "geometry", "mount", "pose", "vehicle", "fracture", "wear", "maintenance", "terrain")):
        expected.add("Mechanics")
    if any(token in tokens for token in ("schedule", "itinerary", "commitment", "reservation", "timetable", "plan_execute")):
        expected.add("Schedule")
    if any(token in tokens for token in ("spec", "gauge", "clearance", "curvature", "compliance", "formalization")):
        expected.add("Spec")
    if any(token in tokens for token in ("interior", "portal", "cabin", "compartment", "airlock")):
        expected.add("Interior")
    if any(token in tokens for token in ("network", "route", "switch", "signal", "edge", "junction")):
        expected.add("Network")
    return expected


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    templates = _load_registry(repo_root, "data/registries/action_template_registry.json")
    for row in sorted(
        (item for item in list(templates.get("templates") or []) if isinstance(item, dict)),
        key=lambda item: str(item.get("action_template_id", "")),
    ):
        template_id = str(row.get("action_template_id", "")).strip()
        if not template_id:
            continue
        declared = _declared_substrates(row)
        expected = _infer_expected_substrates(row)
        process_id = str((dict(row.get("extensions") or {})).get("process_id", "")).strip()
        if process_id and not declared:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.substrate_bypass_smell",
                    severity="RISK",
                    confidence=0.8,
                    file_path="data/registries/action_template_registry.json",
                    line=1,
                    evidence=["process-backed action_template has no affected_substrates declaration", template_id, process_id],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-ACTION-MUST-HAVE-FAMILY"],
                    related_paths=["data/registries/action_template_registry.json"],
                )
            )
            continue
        if expected and not expected.issubset(declared):
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.substrate_bypass_smell",
                    severity="RISK",
                    confidence=0.75,
                    file_path="data/registries/action_template_registry.json",
                    line=1,
                    evidence=[
                        "template likely touches substrate(s) not declared",
                        template_id,
                        "expected={}".format(",".join(sorted(expected))),
                        "declared={}".format(",".join(sorted(declared))),
                    ],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-ACTION-MUST-HAVE-FAMILY"],
                    related_paths=["data/registries/action_template_registry.json"],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

