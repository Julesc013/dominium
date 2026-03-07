"""FAST test: LOGIC signal observation refuses reads without instrumentation."""

from __future__ import annotations

import json
import os


TEST_ID = "test_no_truth_leak_without_instrument"
TEST_TAGS = ["fast", "logic", "instrumentation", "epistemics"]


def _load(repo_root: str, rel_path: str) -> dict:
    return json.load(open(os.path.join(repo_root, rel_path.replace("/", os.sep)), "r", encoding="utf-8"))


def run(repo_root: str):
    from src.logic.signal import observe_signal_row

    signal_row = {
        "signal_id": "signal.logic.observe",
        "signal_type_id": "signal.boolean",
        "carrier_type_id": "carrier.electrical",
        "value_ref": {"value_kind": "boolean", "value": 1},
        "valid_from_tick": 2,
        "valid_until_tick": None,
        "extensions": {
            "slot": {"network_id": "net.logic", "element_id": "elem.observe", "port_id": "port.tap"},
            "delay_policy_id": "delay.none",
            "noise_policy_id": "noise.none",
        },
    }
    surfaces = _load(repo_root, "data/registries/instrumentation_surface_registry.json")
    access = _load(repo_root, "data/registries/access_policy_registry.json")
    models = _load(repo_root, "data/registries/measurement_model_registry.json")
    denied = observe_signal_row(
        signal_row=signal_row,
        current_tick=6,
        authority_context={"privilege_level": "operator", "entitlements": ["entitlement.inspect"]},
        has_physical_access=False,
        available_instrument_type_ids=[],
        instrumentation_surface_registry_payload=surfaces,
        access_policy_registry_payload=access,
        measurement_model_registry_payload=models,
    )
    if str(denied.get("result", "")) != "refused":
        return {"status": "fail", "message": "logic observation should refuse reads without instrument access"}
    allowed = observe_signal_row(
        signal_row=signal_row,
        current_tick=6,
        authority_context={"privilege_level": "operator", "entitlements": ["entitlement.inspect"]},
        has_physical_access=False,
        available_instrument_type_ids=["instrument.logic_probe"],
        instrumentation_surface_registry_payload=surfaces,
        access_policy_registry_payload=access,
        measurement_model_registry_payload=models,
    )
    if str(allowed.get("result", "")) != "complete":
        return {"status": "fail", "message": "logic observation should succeed with required instrumentation"}
    artifact = dict(allowed.get("signal_observation_artifact") or {})
    if str(artifact.get("signal_id", "")).strip() != "signal.logic.observe":
        return {"status": "fail", "message": "logic observation artifact lost signal identity"}
    return {"status": "pass", "message": "logic signal observation requires instrumentation and access"}
