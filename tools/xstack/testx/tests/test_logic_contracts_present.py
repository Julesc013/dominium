"""FAST test: LOGIC tier, coupling, and explain contracts are declared."""

from __future__ import annotations

import json
import os


TEST_ID = "test_logic_contracts_present"
TEST_TAGS = ["fast", "logic", "contracts"]


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
        return {"status": "fail", "message": "LOGIC contract registries missing or invalid"}

    if not any(str(row.get("subsystem_id", "")).strip().upper() == "LOGIC" for row in tier_rows if isinstance(row, dict)):
        return {"status": "fail", "message": "missing LOGIC tier contract"}

    required_couplings = {
        "coupling.logic.command_to_proc.actuator",
        "coupling.sys.transducer_to_logic.signal",
        "coupling.sig.receipt_to_logic.message",
    }
    declared_couplings = {
        str(row.get("contract_id", "")).strip()
        for row in coupling_rows
        if isinstance(row, dict) and str(row.get("contract_id", "")).strip()
    }
    missing_couplings = sorted(required_couplings - declared_couplings)
    if missing_couplings:
        return {"status": "fail", "message": "missing LOGIC coupling contracts: {}".format(",".join(missing_couplings))}

    required_events = {
        "logic.loop_detected",
        "logic.oscillation",
        "logic.timing_violation",
        "logic.compute_throttle",
        "logic.command_refused",
    }
    declared_events = {
        str(row.get("event_kind_id", "")).strip()
        for row in explain_rows
        if isinstance(row, dict) and str(row.get("event_kind_id", "")).strip()
    }
    missing_events = sorted(required_events - declared_events)
    if missing_events:
        return {"status": "fail", "message": "missing LOGIC explain events: {}".format(",".join(missing_events))}

    return {"status": "pass", "message": "LOGIC contracts present"}
