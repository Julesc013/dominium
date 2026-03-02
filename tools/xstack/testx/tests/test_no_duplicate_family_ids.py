"""STRICT test: action family registry has unique family identifiers."""

from __future__ import annotations

import json
import os


TEST_ID = "test_no_duplicate_family_ids"
TEST_TAGS = ["strict", "meta", "action_grammar"]


def run(repo_root: str):
    rel_path = "data/registries/action_family_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "failed to load action_family_registry.json"}

    record = dict(payload.get("record") or payload) if isinstance(payload, dict) else {}
    rows = list(record.get("families") or [])
    seen = set()
    duplicates = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        family_id = str(row.get("action_family_id", "")).strip()
        if not family_id:
            continue
        if family_id in seen:
            duplicates.append(family_id)
            continue
        seen.add(family_id)
    if duplicates:
        return {
            "status": "fail",
            "message": "duplicate action_family_id values detected: {}".format(",".join(sorted(set(duplicates)))),
        }
    return {"status": "pass", "message": "action family identifiers are unique"}

