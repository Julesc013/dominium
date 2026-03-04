"""FAST test: THERM action templates include thermal maintenance/sensing mappings."""

from __future__ import annotations

import json
import os


TEST_ID = "test_action_grammar_entries_present_for_thermal_measure"
TEST_TAGS = ["fast", "meta", "thermal", "action_grammar"]


_EXPECTED = {
    "action.therm.insulate": "action_family.maintain",
    "action.therm.cool": "action_family.maintain",
    "action.therm.vent_heat": "action_family.store_contain",
    "action.therm.measure_temperature": "action_family.sense_measure",
}


def run(repo_root: str):
    rel_path = "data/registries/action_template_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        return {"status": "fail", "message": "{} missing".format(rel_path)}

    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"status": "fail", "message": "failed to parse {}: {}".format(rel_path, exc)}

    record = dict((payload if isinstance(payload, dict) else {}).get("record") or {})
    rows = list(record.get("templates") or [])
    by_id = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        template_id = str(row.get("action_template_id", "")).strip()
        if template_id:
            by_id[template_id] = dict(row)

    missing = []
    wrong_family = []
    for action_id, expected_family in sorted(_EXPECTED.items()):
        row = dict(by_id.get(action_id) or {})
        if not row:
            missing.append(action_id)
            continue
        actual_family = str(row.get("action_family_id", "")).strip()
        if actual_family != expected_family:
            wrong_family.append("{}->{}".format(action_id, actual_family or "<missing>"))

    if missing:
        return {"status": "fail", "message": "missing THERM action templates: {}".format(",".join(missing))}
    if wrong_family:
        return {
            "status": "fail",
            "message": "THERM action template family mismatch: {}".format(",".join(wrong_family)),
        }
    return {"status": "pass", "message": "THERM action templates present with canonical family mappings"}

