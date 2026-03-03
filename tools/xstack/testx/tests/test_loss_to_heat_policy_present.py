"""FAST test: loss-to-heat policy registry includes PHYS-0 required policies."""

from __future__ import annotations

import json
import os


TEST_ID = "testx.physics.loss_to_heat_policy_present"
TEST_TAGS = ["fast", "physics", "registry"]


_REQUIRED_POLICIES = {
    "loss_to_heat.required",
    "loss_to_heat.optional",
    "loss_to_heat.disabled",
}


def run(repo_root: str):
    rel_path = "data/registries/loss_to_heat_policy_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "loss_to_heat policy registry missing or invalid"}

    rows = list(((payload.get("record") or {}).get("loss_to_heat_policies") or []))
    ids = {
        str(row.get("loss_to_heat_policy_id", "")).strip()
        for row in rows
        if isinstance(row, dict) and str(row.get("loss_to_heat_policy_id", "")).strip()
    }
    missing = sorted(_REQUIRED_POLICIES - ids)
    if missing:
        return {"status": "fail", "message": "missing loss_to_heat policies: {}".format(",".join(missing))}

    required_row = next(
        (
            row
            for row in rows
            if isinstance(row, dict) and str(row.get("loss_to_heat_policy_id", "")).strip() == "loss_to_heat.required"
        ),
        {},
    )
    if not bool(required_row.get("map_loss_to_heat", False)):
        return {"status": "fail", "message": "loss_to_heat.required must set map_loss_to_heat=true"}
    if not bool(required_row.get("require_exception_log", False)):
        return {"status": "fail", "message": "loss_to_heat.required must require exception logging"}
    return {"status": "pass", "message": "loss_to_heat policy registry valid"}
