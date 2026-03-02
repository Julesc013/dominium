"""E176 affordance gap smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E176_AFFORDANCE_GAP_SMELL"


class AffordanceGapSmell:
    analyzer_id = ANALYZER_ID


_REQUIRED_AFFORDANCE_IDS = {
    "matter_transformation",
    "motion_force_transmission",
    "containment_interfaces",
    "measurement_verification",
    "communication_coordination",
    "institutions_contracts",
    "environment_living_systems",
    "time_synchronization",
    "safety_protection",
}


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return payload


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    matrix_rel = "data/meta/real_world_affordance_matrix.json"
    template_rel = "data/registries/action_template_registry.json"

    matrix_payload = _load_json(repo_root, matrix_rel)
    if not matrix_payload:
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.affordance_gap_smell",
                severity="VIOLATION",
                confidence=0.95,
                file_path=matrix_rel,
                line=1,
                evidence=["RWAM metadata missing or invalid"],
                suggested_classification="INVALID",
                recommended_action="ADD_RULE",
                related_invariants=["INV-AFFORDANCE-DECLARED"],
                related_paths=[matrix_rel],
            )
        )
        return findings

    affordance_rows = list(matrix_payload.get("affordances") or [])
    affordance_ids = set()
    known_substrates = set()
    for row in affordance_rows:
        if not isinstance(row, dict):
            continue
        affordance_id = str(row.get("id", "")).strip()
        if affordance_id:
            affordance_ids.add(affordance_id)
        for substrate in list(row.get("substrates") or []):
            token = str(substrate).strip()
            if token:
                known_substrates.add(token)

    for affordance_id in sorted(_REQUIRED_AFFORDANCE_IDS - affordance_ids):
        findings.append(
            make_finding(
                analyzer_id=ANALYZER_ID,
                category="architecture.affordance_gap_smell",
                severity="RISK",
                confidence=0.93,
                file_path=matrix_rel,
                line=1,
                evidence=["missing canonical affordance id", affordance_id],
                suggested_classification="TODO-BLOCKED",
                recommended_action="REWRITE",
                related_invariants=["INV-AFFORDANCE-DECLARED"],
                related_paths=[matrix_rel],
            )
        )

    template_payload = _load_json(repo_root, template_rel)
    record = dict(template_payload.get("record") or template_payload)
    templates = list(record.get("templates") or [])
    for row in templates:
        if not isinstance(row, dict):
            continue
        template_id = str(row.get("action_template_id", "")).strip() or "<unknown_template>"
        affected = [str(item).strip() for item in (row.get("affected_substrates") or []) if str(item).strip()]
        for substrate in affected:
            if substrate in known_substrates:
                continue
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.affordance_gap_smell",
                    severity="RISK",
                    confidence=0.9,
                    file_path=template_rel,
                    line=1,
                    evidence=["action template touches substrate missing from RWAM", template_id, substrate],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-AFFORDANCE-DECLARED"],
                    related_paths=[template_rel, matrix_rel],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )
