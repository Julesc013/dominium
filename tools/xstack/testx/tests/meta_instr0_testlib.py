"""Shared META-INSTR0 TestX fixtures/helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def instrumentation_inputs(repo_root: str) -> dict:
    return {
        "instrumentation_surface_registry_payload": _load_json(
            repo_root, "data/registries/instrumentation_surface_registry.json"
        ),
        "access_policy_registry_payload": _load_json(repo_root, "data/registries/access_policy_registry.json"),
        "measurement_model_registry_payload": _load_json(
            repo_root, "data/registries/measurement_model_registry.json"
        ),
        "explain_contract_registry_payload": _load_json(
            repo_root, "data/registries/explain_contract_registry.json"
        ),
    }


def authority_context(*, privilege_level: str, entitlements: object) -> dict:
    return {
        "authority_origin": "testx",
        "experience_id": "profile.test.meta_instr0",
        "law_profile_id": "law.test.meta_instr0",
        "privilege_level": str(privilege_level or "").strip().lower() or "observer",
        "entitlements": sorted(set(str(item).strip() for item in list(entitlements or []) if str(item).strip())),
    }


def run_measurement_case(
    *,
    repo_root: str,
    owner_kind: str,
    owner_id: str,
    measurement_point_id: str,
    raw_value: int,
    current_tick: int,
    authority_context_row: Mapping[str, object],
    has_physical_access: bool,
    available_instrument_type_ids: object,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from meta.instrumentation import generate_measurement_observation

    payloads = instrumentation_inputs(repo_root)
    return generate_measurement_observation(
        owner_kind=str(owner_kind),
        owner_id=str(owner_id),
        measurement_point_id=str(measurement_point_id),
        raw_value=int(raw_value),
        current_tick=int(current_tick),
        authority_context=dict(authority_context_row or {}),
        has_physical_access=bool(has_physical_access),
        available_instrument_type_ids=list(available_instrument_type_ids or []),
        instrumentation_surface_registry_payload=payloads["instrumentation_surface_registry_payload"],
        access_policy_registry_payload=payloads["access_policy_registry_payload"],
        measurement_model_registry_payload=payloads["measurement_model_registry_payload"],
    )


def run_forensics_case(
    *,
    repo_root: str,
    owner_kind: str,
    owner_id: str,
    forensics_point_id: str,
    authority_context_row: Mapping[str, object],
    has_physical_access: bool,
    event_id: str,
    target_id: str,
    event_kind_id: str,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from meta.instrumentation import route_forensics_request

    payloads = instrumentation_inputs(repo_root)
    return route_forensics_request(
        owner_kind=str(owner_kind),
        owner_id=str(owner_id),
        forensics_point_id=str(forensics_point_id),
        authority_context=dict(authority_context_row or {}),
        has_physical_access=bool(has_physical_access),
        instrumentation_surface_registry_payload=payloads["instrumentation_surface_registry_payload"],
        access_policy_registry_payload=payloads["access_policy_registry_payload"],
        explain_contract_registry_payload=payloads["explain_contract_registry_payload"],
        event_id=str(event_id),
        target_id=str(target_id),
        event_kind_id=str(event_kind_id),
        truth_hash_anchor="truth.meta_instr0.fixture",
        epistemic_policy_id="ep.policy.meta_instr0.fixture",
        decision_log_rows=[
            {"decision_id": "decision.meta_instr0.001", "kind_id": "decision"},
        ],
        safety_event_rows=[
            {"event_id": "safety.meta_instr0.001", "event_kind_id": str(event_kind_id)},
        ],
        hazard_rows=[{"event_id": "hazard.meta_instr0.001", "event_kind_id": str(event_kind_id)}],
        compliance_rows=[],
        model_result_rows=[],
    )

