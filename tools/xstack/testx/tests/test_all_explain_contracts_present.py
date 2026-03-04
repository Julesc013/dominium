"""STRICT test: required explain contracts are present for enforced event families."""

from __future__ import annotations

import json
import os


TEST_ID = "test_all_explain_contracts_present"
TEST_TAGS = ["strict", "meta", "contracts", "explain"]


_REQUIRED_EVENT_IDS = {
    "elec.trip",
    "elec.fault",
    "therm.overheat",
    "therm.fire",
    "therm.runaway",
    "fluid.relief",
    "fluid.burst",
    "fluid.leak",
    "fluid.cavitation",
    "mob.derailment",
    "mob.collision",
    "mob.signal_violation",
    "sig.delivery_loss",
    "sig.jamming",
    "sig.decrypt_denied",
    "sig.trust_update",
    "phys.exception_event",
    "phys.energy_violation",
    "phys.momentum_violation",
}


def run(repo_root: str):
    rel_path = "data/registries/explain_contract_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "explain contract registry missing or invalid"}

    rows = list((dict(payload.get("record") or {})).get("explain_contracts") or payload.get("explain_contracts") or [])
    if not rows:
        return {"status": "fail", "message": "explain contract registry has no rows"}

    declared = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        event_kind_id = str(row.get("event_kind_id", "")).strip()
        if event_kind_id:
            declared.add(event_kind_id)
        if not str(row.get("contract_id", "")).strip():
            return {"status": "fail", "message": "explain contract row missing contract_id"}
        if not str(row.get("explain_artifact_type_id", "")).strip():
            return {
                "status": "fail",
                "message": "explain contract '{}' missing explain_artifact_type_id".format(event_kind_id or "<unknown>"),
            }
        if not list(row.get("required_inputs") or []):
            return {"status": "fail", "message": "explain contract '{}' missing required_inputs".format(event_kind_id or "<unknown>")}
        if not list(row.get("remediation_hint_keys") or []):
            return {
                "status": "fail",
                "message": "explain contract '{}' missing remediation_hint_keys".format(event_kind_id or "<unknown>"),
            }

    missing = sorted(_REQUIRED_EVENT_IDS - declared)
    if missing:
        return {"status": "fail", "message": "missing explain contracts for events: {}".format(",".join(missing))}
    return {"status": "pass", "message": "required explain contracts present"}
