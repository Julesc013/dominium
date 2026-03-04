"""FAST test: FLUID optional/null policy path is present for null-boot."""

from __future__ import annotations

import json
import os


TEST_ID = "test_fluid_null_boot_ok"
TEST_TAGS = ["fast", "fluid", "null_boot"]


def run(repo_root: str):
    policy_rel = "data/registries/fluid_network_policy_registry.json"
    policy_abs = os.path.join(repo_root, policy_rel.replace("/", os.sep))
    try:
        payload = json.load(open(policy_abs, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "fluid network policy registry missing or invalid"}

    rows = list(((payload.get("record") or {}).get("fluid_network_policies") or []))
    none_row = next(
        (
            row
            for row in rows
            if isinstance(row, dict) and str(row.get("policy_id", "")).strip() == "fluid.policy.none"
        ),
        {},
    )
    if not none_row:
        return {"status": "fail", "message": "fluid.policy.none is required for null-boot compatibility"}

    tier_mode = str(none_row.get("tier_mode", "")).strip()
    if tier_mode != "F0":
        return {"status": "fail", "message": "fluid.policy.none must use tier_mode=F0"}

    extensions = dict(none_row.get("extensions") or {})
    if not bool(extensions.get("null_boot_safe", False)):
        return {"status": "fail", "message": "fluid.policy.none must declare null_boot_safe=true"}
    return {"status": "pass", "message": "fluid null-boot policy present"}
