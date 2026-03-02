"""STRICT test: RWAM declares all canonical affordance categories."""

from __future__ import annotations

import json
import os


TEST_ID = "test_all_affordances_declared"
TEST_TAGS = ["strict", "meta", "affordance", "rwam"]


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


def run(repo_root: str):
    rel_path = "data/meta/real_world_affordance_matrix.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    if not os.path.isfile(abs_path):
        return {"status": "fail", "message": "{} missing".format(rel_path)}

    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"status": "fail", "message": "failed to parse {}: {}".format(rel_path, exc)}

    affordances = list((payload if isinstance(payload, dict) else {}).get("affordances") or [])
    declared = set()
    for row in affordances:
        if not isinstance(row, dict):
            continue
        affordance_id = str(row.get("id", "")).strip()
        if affordance_id:
            declared.add(affordance_id)

    missing = sorted(_REQUIRED_AFFORDANCE_IDS - declared)
    if missing:
        return {
            "status": "fail",
            "message": "RWAM missing canonical affordances: {}".format(",".join(missing)),
        }
    return {"status": "pass", "message": "RWAM declares all canonical affordance categories"}
