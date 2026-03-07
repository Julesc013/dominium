"""FAST test: LOGIC-2 element definitions must declare non-zero compute cost."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_compute_cost_required"
TEST_TAGS = ["fast", "logic", "compute", "validator"]


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _record_rows(payload: dict, key: str) -> list[dict]:
    rows = list((dict(payload.get("record") or {})).get(key) or payload.get(key) or [])
    return [dict(row) for row in rows if isinstance(row, dict)]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.logic import validate_logic_element_definitions

    logic_element_rows = _record_rows(
        _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_element_registry.json"),
        "logic_elements",
    )
    logic_behavior_model_rows = _record_rows(
        _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_behavior_model_registry.json"),
        "logic_behavior_models",
    )
    state_machine_definition_rows = _record_rows(
        _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_state_machine_registry.json"),
        "state_machine_definitions",
    )
    assembly_rows = _record_rows(
        _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_assemblies.json"),
        "assemblies",
    )
    interface_signature_rows = _record_rows(
        _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_interface_signatures.json"),
        "logic_interface_signatures",
    )
    state_vector_definition_rows = _record_rows(
        _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_state_vectors.json"),
        "state_vector_definitions",
    )
    quantity_bundle_registry_payload = _load_json(repo_root, "data/registries/quantity_bundle_registry.json")
    spec_type_registry_payload = _load_json(repo_root, "data/registries/spec_type_registry.json")
    signal_channel_type_registry_payload = _load_json(repo_root, "data/registries/signal_channel_type_registry.json")
    port_type_registry_payload = _load_json(repo_root, "data/registries/port_type_registry.json")

    baseline = validate_logic_element_definitions(
        logic_element_rows=logic_element_rows,
        logic_behavior_model_rows=logic_behavior_model_rows,
        state_machine_definition_rows=state_machine_definition_rows,
        assembly_rows=assembly_rows,
        interface_signature_rows=interface_signature_rows,
        state_vector_definition_rows=state_vector_definition_rows,
        quantity_bundle_registry_payload=quantity_bundle_registry_payload,
        spec_type_registry_payload=spec_type_registry_payload,
        signal_channel_type_registry_payload=signal_channel_type_registry_payload,
        port_type_registry_payload=port_type_registry_payload,
    )
    if str(baseline.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "baseline logic element pack must validate before mutation"}

    mutated = [dict(row) for row in logic_element_rows]
    target_id = ""
    for row in mutated:
        target_id = str(row.get("element_id", "")).strip()
        if target_id:
            row["compute_cost_units"] = 0
            break
    if not target_id:
        return {"status": "fail", "message": "logic element pack has no mutable baseline row"}

    refused = validate_logic_element_definitions(
        logic_element_rows=mutated,
        logic_behavior_model_rows=logic_behavior_model_rows,
        state_machine_definition_rows=state_machine_definition_rows,
        assembly_rows=assembly_rows,
        interface_signature_rows=interface_signature_rows,
        state_vector_definition_rows=state_vector_definition_rows,
        quantity_bundle_registry_payload=quantity_bundle_registry_payload,
        spec_type_registry_payload=spec_type_registry_payload,
        signal_channel_type_registry_payload=signal_channel_type_registry_payload,
        port_type_registry_payload=port_type_registry_payload,
    )
    if str(refused.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "missing compute cost must refuse logic element validation"}
    if target_id not in set(str(item).strip() for item in list(refused.get("failed_element_ids") or [])):
        return {"status": "fail", "message": "missing compute cost was not attributed to {}".format(target_id)}

    checks = {
        str(row.get("element_id", "")).strip(): list(row.get("failures") or [])
        for row in list(refused.get("checks") or [])
        if isinstance(row, dict)
    }
    if "compute_cost_missing" not in set(str(item).strip() for item in checks.get(target_id, [])):
        return {"status": "fail", "message": "compute-cost refusal reason missing for {}".format(target_id)}

    return {"status": "pass", "message": "LOGIC-2 validator refuses elements without compute cost"}
