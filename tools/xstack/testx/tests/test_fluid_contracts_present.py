"""FAST test: FLUID tier/coupling/explain contracts are declared."""

from __future__ import annotations

import json
import os


TEST_ID = "test_fluid_contracts_present"
TEST_TAGS = ["fast", "fluid", "contracts"]


def _load_rows(repo_root: str, rel_path: str, key: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    payload = json.load(open(abs_path, "r", encoding="utf-8"))
    return list(((payload.get("record") or {}).get(key) or []))


def run(repo_root: str):
    try:
        tier_rows = _load_rows(repo_root, "data/registries/tier_contract_registry.json", "tier_contracts")
        coupling_rows = _load_rows(repo_root, "data/registries/coupling_contract_registry.json", "coupling_contracts")
        explain_rows = _load_rows(repo_root, "data/registries/explain_contract_registry.json", "explain_contracts")
    except (OSError, ValueError):
        return {"status": "fail", "message": "contract registries missing or invalid"}

    has_tier = any(str(row.get("subsystem_id", "")).strip().upper() == "FLUID" for row in tier_rows if isinstance(row, dict))
    if not has_tier:
        return {"status": "fail", "message": "missing FLUID tier contract"}

    required_couplings = {
        ("FLUID", "THERM", "model.fluid_heat_exchanger_stub"),
        ("FLUID", "INT", "model.fluid_leak_flood_stub"),
        ("FLUID", "MECH", "model.fluid_pressure_load_stub"),
    }
    declared = {
        (
            str(row.get("from_domain_id", "")).strip().upper(),
            str(row.get("to_domain_id", "")).strip().upper(),
            str(row.get("mechanism_id", "")).strip(),
        )
        for row in coupling_rows
        if isinstance(row, dict)
    }
    missing = sorted(required_couplings - declared)
    if missing:
        tokens = ["{}->{}:{}".format(item[0], item[1], item[2]) for item in missing]
        return {"status": "fail", "message": "missing FLUID coupling contracts: {}".format(",".join(tokens))}

    required_events = {"fluid.leak", "fluid.overpressure", "fluid.cavitation", "fluid.burst"}
    declared_events = {
        str(row.get("event_kind_id", "")).strip()
        for row in explain_rows
        if isinstance(row, dict)
    }
    missing_events = sorted(required_events - declared_events)
    if missing_events:
        return {"status": "fail", "message": "missing FLUID explain contracts for events: {}".format(",".join(missing_events))}

    return {"status": "pass", "message": "FLUID contracts present"}
