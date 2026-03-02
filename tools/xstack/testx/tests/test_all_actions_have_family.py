"""STRICT test: all control/interaction/task/process actions map to action families."""

from __future__ import annotations

import json
import os


TEST_ID = "test_all_actions_have_family"
TEST_TAGS = ["strict", "meta", "action_grammar"]


def _load_record(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return dict(payload.get("record") or payload)


def run(repo_root: str):
    control = _load_record(repo_root, "data/registries/control_action_registry.json")
    interaction = _load_record(repo_root, "data/registries/interaction_action_registry.json")
    task_types = _load_record(repo_root, "data/registries/task_type_registry.json")
    processes = _load_record(repo_root, "data/registries/process_registry.json")
    templates = _load_record(repo_root, "data/registries/action_template_registry.json")
    families = _load_record(repo_root, "data/registries/action_family_registry.json")

    family_ids = set()
    for row in list(families.get("families") or []):
        if not isinstance(row, dict):
            continue
        family_id = str(row.get("action_family_id", "")).strip()
        if family_id:
            family_ids.add(family_id)

    template_by_id = {}
    for row in list(templates.get("templates") or []):
        if not isinstance(row, dict):
            continue
        template_id = str(row.get("action_template_id", "")).strip()
        if template_id:
            template_by_id.setdefault(template_id, dict(row))

    source_ids = set()
    for row in list(control.get("actions") or []):
        if isinstance(row, dict):
            action_id = str(row.get("action_id", "")).strip()
            if action_id:
                source_ids.add(action_id)
    for row in list(interaction.get("actions") or []):
        if isinstance(row, dict):
            action_id = str(row.get("action_id", "")).strip()
            if action_id:
                source_ids.add(action_id)
    for row in list(task_types.get("task_types") or []):
        if isinstance(row, dict):
            task_type_id = str(row.get("task_type_id", "")).strip()
            if task_type_id:
                source_ids.add(task_type_id)
    for row in list(processes.get("processes") or []):
        if isinstance(row, dict):
            process_id = str(row.get("process_id", "")).strip()
            if process_id:
                source_ids.add(process_id)

    missing_templates = []
    missing_families = []
    unknown_families = []
    for source_id in sorted(source_ids):
        template_row = dict(template_by_id.get(source_id) or {})
        if not template_row:
            missing_templates.append(source_id)
            continue
        family_id = str(template_row.get("action_family_id", "")).strip()
        if not family_id:
            missing_families.append(source_id)
            continue
        if family_ids and family_id not in family_ids:
            unknown_families.append("{}->{}".format(source_id, family_id))

    if missing_templates:
        return {
            "status": "fail",
            "message": "missing action_template mappings for {} source ids (sample: {})".format(
                len(missing_templates),
                ",".join(missing_templates[:8]),
            ),
        }
    if missing_families:
        return {
            "status": "fail",
            "message": "missing action_family_id for {} mapped source ids (sample: {})".format(
                len(missing_families),
                ",".join(missing_families[:8]),
            ),
        }
    if unknown_families:
        return {
            "status": "fail",
            "message": "unknown action_family_id references detected (sample: {})".format(",".join(unknown_families[:8])),
        }
    return {"status": "pass", "message": "all source actions/processes/tasks map to canonical action families"}

