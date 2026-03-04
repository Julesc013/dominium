"""FAST test: mandatory baseline domains declare tier contracts."""

from __future__ import annotations

import json
import os


TEST_ID = "test_all_domains_have_tier_contract"
TEST_TAGS = ["fast", "meta", "contracts", "tier"]


_REQUIRED_SUBSYSTEMS = {"ELEC", "THERM", "MOB", "SIG", "PHYS", "FLUID"}


def run(repo_root: str):
    rel_path = "data/registries/tier_contract_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "tier contract registry missing or invalid"}

    rows = list((dict(payload.get("record") or {})).get("tier_contracts") or payload.get("tier_contracts") or [])
    if not rows:
        return {"status": "fail", "message": "tier contract registry has no rows"}

    declared = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        subsystem_id = str(row.get("subsystem_id", "")).strip().upper()
        if subsystem_id:
            declared.add(subsystem_id)
        if not str(row.get("contract_id", "")).strip():
            return {"status": "fail", "message": "tier contract row missing contract_id"}
        if not str(row.get("cost_model_id", "")).strip():
            return {
                "status": "fail",
                "message": "tier contract '{}' missing cost_model_id".format(subsystem_id or "<unknown>"),
            }
        if not list(row.get("supported_tiers") or []):
            return {"status": "fail", "message": "tier contract '{}' missing supported_tiers".format(subsystem_id or "<unknown>")}
        if not list(row.get("deterministic_degradation_order") or []):
            return {
                "status": "fail",
                "message": "tier contract '{}' missing deterministic_degradation_order".format(subsystem_id or "<unknown>"),
            }
        if "shard_safe" not in row:
            return {"status": "fail", "message": "tier contract '{}' missing shard_safe declaration".format(subsystem_id or "<unknown>")}
        tiers = [str(token).strip() for token in list(row.get("supported_tiers") or []) if str(token).strip()]
        if "micro" in tiers and not isinstance(row.get("micro_roi_requirements"), dict):
            return {
                "status": "fail",
                "message": "micro-capable tier contract '{}' missing micro_roi_requirements".format(subsystem_id or "<unknown>"),
            }

    missing = sorted(_REQUIRED_SUBSYSTEMS - declared)
    if missing:
        return {"status": "fail", "message": "missing tier contracts for subsystems: {}".format(",".join(missing))}
    return {"status": "pass", "message": "baseline tier contracts present"}
