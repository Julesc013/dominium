"""E303 missing-instrumentation-surface smell analyzer."""

from __future__ import annotations

import json
import os
from typing import Mapping

from analyzers.base import make_finding


ANALYZER_ID = "E303_MISSING_INSTRUMENTATION_SURFACE_SMELL"
RULE_ID = "INV-SYSTEM-MUST-DECLARE-INSTRUMENTATION"
REGISTRY_REL = "data/registries/instrumentation_surface_registry.json"
REQUIRED_OWNERS = (
    ("domain", "domain.elec"),
    ("domain", "domain.therm"),
    ("domain", "domain.fluid"),
    ("domain", "domain.chem"),
    ("process", "process.proc.default"),
    ("capsule", "capsule.system.default"),
)


class MissingInstrumentationSurfaceSmell:
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
                category="meta.instrumentation.missing_surface_registry",
                severity="VIOLATION",
                confidence=0.95,
                file_path=REGISTRY_REL,
                line=1,
                evidence=["instrumentation surface registry missing or invalid: {}".format(err)],
                suggested_classification="BLOCKER",
                recommended_action="ADD_CONTRACT",
                related_invariants=[RULE_ID],
                related_paths=[REGISTRY_REL],
            )
        )
        return findings

    rows = list((dict(payload.get("record") or {})).get("instrumentation_surfaces") or payload.get("instrumentation_surfaces") or [])
    by_owner = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        owner_kind = str(row.get("owner_kind", "")).strip().lower()
        owner_id = str(row.get("owner_id", "")).strip()
        if owner_kind and owner_id:
            by_owner["{}::{}".format(owner_kind, owner_id)] = dict(row)

    for owner_kind, owner_id in REQUIRED_OWNERS:
        owner_key = "{}::{}".format(owner_kind, owner_id)
        row = dict(by_owner.get(owner_key) or {})
        if not row:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="meta.instrumentation.missing_owner_surface",
                    severity="RISK",
                    confidence=0.9,
                    file_path=REGISTRY_REL,
                    line=1,
                    evidence=["missing required instrumentation surface owner", owner_key],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="ADD_CONTRACT",
                    related_invariants=[RULE_ID],
                    related_paths=[REGISTRY_REL],
                )
            )
            continue
        for field_key in ("control_points", "measurement_points", "forensics_points"):
            if isinstance(row.get(field_key), list) and row.get(field_key):
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="meta.instrumentation.incomplete_owner_surface",
                    severity="RISK",
                    confidence=0.86,
                    file_path=REGISTRY_REL,
                    line=1,
                    evidence=["owner surface field missing/empty", "{} {}".format(owner_key, field_key)],
                    suggested_classification="NEEDS_REVIEW",
                    recommended_action="REWRITE",
                    related_invariants=[RULE_ID],
                    related_paths=[REGISTRY_REL],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
