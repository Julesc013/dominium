"""E162 action without family smell analyzer."""

from __future__ import annotations

import json
import os

from analyzers.base import make_finding


ANALYZER_ID = "E162_ACTION_WITHOUT_FAMILY_SMELL"


class ActionWithoutFamilySmell:
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


def run(graph, repo_root, changed_files=None):
    del graph
    del changed_files
    findings = []

    control = _load_registry(repo_root, "data/registries/control_action_registry.json")
    interaction = _load_registry(repo_root, "data/registries/interaction_action_registry.json")
    task_types = _load_registry(repo_root, "data/registries/task_type_registry.json")
    processes = _load_registry(repo_root, "data/registries/process_registry.json")
    templates = _load_registry(repo_root, "data/registries/action_template_registry.json")
    families = _load_registry(repo_root, "data/registries/action_family_registry.json")

    family_ids = set()
    for row in list(families.get("families") or []):
        if not isinstance(row, dict):
            continue
        family_id = str(row.get("action_family_id", "")).strip()
        if family_id:
            family_ids.add(family_id)

    source_ids = set()
    for row in list(control.get("actions") or []):
        if not isinstance(row, dict):
            continue
        action_id = str(row.get("action_id", "")).strip()
        if action_id:
            source_ids.add(action_id)
    for row in list(interaction.get("actions") or []):
        if not isinstance(row, dict):
            continue
        action_id = str(row.get("action_id", "")).strip()
        if action_id:
            source_ids.add(action_id)
    for row in list(task_types.get("task_types") or []):
        if not isinstance(row, dict):
            continue
        task_type_id = str(row.get("task_type_id", "")).strip()
        if task_type_id:
            source_ids.add(task_type_id)
    for row in list(processes.get("processes") or []):
        if not isinstance(row, dict):
            continue
        process_id = str(row.get("process_id", "")).strip()
        if process_id:
            source_ids.add(process_id)

    template_by_id = {}
    for row in list(templates.get("templates") or []):
        if not isinstance(row, dict):
            continue
        template_id = str(row.get("action_template_id", "")).strip()
        if not template_id:
            continue
        template_by_id.setdefault(template_id, dict(row))

    for source_id in sorted(source_ids):
        template_row = dict(template_by_id.get(source_id) or {})
        if not template_row:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.action_without_family_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path="data/registries/action_template_registry.json",
                    line=1,
                    evidence=["missing action_template mapping", source_id],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=[
                        "INV-ACTION-MUST-HAVE-FAMILY",
                        "INV-NO-UNREGISTERED-ACTION",
                    ],
                    related_paths=[
                        "data/registries/action_template_registry.json",
                        "data/registries/action_family_registry.json",
                    ],
                )
            )
            continue
        family_id = str(template_row.get("action_family_id", "")).strip()
        if not family_id:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.action_without_family_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path="data/registries/action_template_registry.json",
                    line=1,
                    evidence=["action_template missing action_family_id", source_id],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-ACTION-MUST-HAVE-FAMILY"],
                    related_paths=[
                        "data/registries/action_template_registry.json",
                        "docs/meta/ACTION_GRAMMAR_CONSTITUTION.md",
                    ],
                )
            )
            continue
        if family_ids and family_id not in family_ids:
            findings.append(
                make_finding(
                    analyzer_id=ANALYZER_ID,
                    category="architecture.action_without_family_smell",
                    severity="RISK",
                    confidence=0.95,
                    file_path="data/registries/action_template_registry.json",
                    line=1,
                    evidence=["action_template references unknown family", source_id, family_id],
                    suggested_classification="TODO-BLOCKED",
                    recommended_action="REWRITE",
                    related_invariants=["INV-ACTION-MUST-HAVE-FAMILY"],
                    related_paths=[
                        "data/registries/action_template_registry.json",
                        "data/registries/action_family_registry.json",
                    ],
                )
            )

    return sorted(
        findings,
        key=lambda item: (_norm(item.location.file_path), item.location.line_start, item.severity),
    )

