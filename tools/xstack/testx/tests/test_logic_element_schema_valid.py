"""FAST test: LOGIC-2 element schemas and baseline pack definitions are present."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_logic_element_schema_valid"
TEST_TAGS = ["fast", "logic", "schema", "element"]


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8").read()
    except OSError:
        return ""


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic import (
        build_logic_behavior_model_row,
        build_logic_element_definition_row,
        build_state_machine_definition_row,
    )

    schema_checks = (
        (
            "schema/logic/logic_element_definition.schema",
            (
                "element_id",
                "description",
                "interface_signature_id",
                "state_vector_definition_id",
                "behavior_model_id",
                "compute_cost_units",
                "timing_policy_id",
                "deterministic_fingerprint",
            ),
        ),
        (
            "schema/logic/logic_behavior_model.schema",
            (
                "behavior_model_id",
                "model_kind",
                "model_ref",
                "deterministic_fingerprint",
            ),
        ),
        (
            "schema/logic/state_machine_definition.schema",
            (
                "sm_id",
                "states",
                "transition_rules",
                "output_rules",
                "deterministic_fingerprint",
            ),
        ),
    )
    for rel_path, required_tokens in schema_checks:
        text = _read_text(repo_root, rel_path)
        if not text:
            return {"status": "fail", "message": "{} missing".format(rel_path)}
        for token in required_tokens:
            if token not in text:
                return {"status": "fail", "message": "{} missing token '{}'".format(rel_path, token)}

    element_payload = _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_element_registry.json")
    behavior_payload = _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_behavior_model_registry.json")
    state_machine_payload = _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_state_machine_registry.json")
    element_rows = list(element_payload.get("logic_elements") or [])
    behavior_rows = list(behavior_payload.get("logic_behavior_models") or [])
    state_machine_rows = list(state_machine_payload.get("state_machine_definitions") or [])
    if not element_rows or not behavior_rows or not state_machine_rows:
        return {"status": "fail", "message": "logic base pack definitions missing"}

    sample_element = build_logic_element_definition_row(
        element_id=str(element_rows[0].get("element_id", "")).strip(),
        description=str(element_rows[0].get("description", "")).strip(),
        interface_signature_id=str(element_rows[0].get("interface_signature_id", "")).strip(),
        state_vector_definition_id=str(element_rows[0].get("state_vector_definition_id", "")).strip(),
        behavior_model_id=str(element_rows[0].get("behavior_model_id", "")).strip(),
        compute_cost_units=int(element_rows[0].get("compute_cost_units", 0) or 0),
        timing_policy_id=str(element_rows[0].get("timing_policy_id", "")).strip(),
        deterministic_fingerprint=str(element_rows[0].get("deterministic_fingerprint", "")).strip(),
        extensions=dict(element_rows[0].get("extensions") or {}),
    )
    if str(sample_element.get("element_id", "")).strip() != str(element_rows[0].get("element_id", "")).strip():
        return {"status": "fail", "message": "logic element row builder failed"}
    sample_behavior = build_logic_behavior_model_row(
        behavior_model_id=str(behavior_rows[0].get("behavior_model_id", "")).strip(),
        model_kind=str(behavior_rows[0].get("model_kind", "")).strip(),
        model_ref=behavior_rows[0].get("model_ref"),
        deterministic_fingerprint=str(behavior_rows[0].get("deterministic_fingerprint", "")).strip(),
        extensions=dict(behavior_rows[0].get("extensions") or {}),
    )
    if str(sample_behavior.get("behavior_model_id", "")).strip() != str(behavior_rows[0].get("behavior_model_id", "")).strip():
        return {"status": "fail", "message": "logic behavior model row builder failed"}
    sample_state_machine = build_state_machine_definition_row(
        sm_id=str(state_machine_rows[0].get("sm_id", "")).strip(),
        states=list(state_machine_rows[0].get("states") or []),
        transition_rules=list(state_machine_rows[0].get("transition_rules") or []),
        output_rules=list(state_machine_rows[0].get("output_rules") or []),
        deterministic_fingerprint=str(state_machine_rows[0].get("deterministic_fingerprint", "")).strip(),
        extensions=dict(state_machine_rows[0].get("extensions") or {}),
    )
    if str(sample_state_machine.get("sm_id", "")).strip() != str(state_machine_rows[0].get("sm_id", "")).strip():
        return {"status": "fail", "message": "state machine row builder failed"}

    return {"status": "pass", "message": "LOGIC-2 schemas and baseline pack rows are valid"}
