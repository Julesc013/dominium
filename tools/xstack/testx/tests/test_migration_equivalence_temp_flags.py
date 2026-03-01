"""FAST test: CTRL-8 migration replaces temp flags with deterministic effects."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.control.effects.migration_equivalence_temp_flags"
TEST_TAGS = ["fast", "control", "effects", "migration", "interior", "maintenance"]


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "subject_id": "subject.test",
        "law_profile_id": "law.test.ctrl8.migration",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.test", "visibility_level": "nondiegetic"},
        "privilege_level": "observer",
    }


def _law_profile(allowed_processes: list[str]) -> dict:
    allowed = sorted(set(str(item).strip() for item in list(allowed_processes or []) if str(item).strip()))
    return {
        "law_profile_id": "law.test.ctrl8.migration",
        "allowed_processes": allowed,
        "forbidden_processes": [],
        "allow_maintenance": True,
        "process_entitlement_requirements": dict((process_id, "session.boot") for process_id in allowed),
        "process_privilege_requirements": dict((process_id, "observer") for process_id in allowed),
    }


def _run_interior_fixture(repo_root: str) -> dict:
    del repo_root
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.interior_testlib import interior_graph, portal_rows, portal_state_rows, volume_rows
    from tools.xstack.testx.tests.maintenance_testlib import base_state, policy_context

    state = base_state()
    state["interior_graphs"] = [interior_graph()]
    state["interior_volumes"] = volume_rows()
    state["interior_portals"] = portal_rows()
    state["interior_portal_state_machines"] = portal_state_rows(state_id="open")
    state["portal_flow_params"] = []
    state["interior_leak_hazards"] = []
    state["compartment_hazard_models"] = []
    state["compartment_states"] = [
        {
            "schema_version": "1.0.0",
            "volume_id": "volume.a",
            "air_mass": 400,
            "water_volume": 900,
            "temperature": None,
            "oxygen_fraction": 180,
            "smoke_density": 350,
            "derived_pressure": 0,
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "volume_id": "volume.b",
            "air_mass": 800,
            "water_volume": 0,
            "temperature": None,
            "oxygen_fraction": 210,
            "smoke_density": 0,
            "derived_pressure": 0,
            "extensions": {},
        },
    ]
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.ctrl8.interior.001",
            "process_id": "process.compartment_flow_tick",
            "inputs": {"graph_id": "interior.graph.test.alpha", "dt_ticks": 1},
        },
        law_profile=_law_profile(["process.compartment_flow_tick"]),
        authority_context=_authority_context(),
        navigation_indices={},
        policy_context=policy_context(),
    )
    return {"result": result, "state": state}


def _run_decay_fixture(repo_root: str) -> dict:
    del repo_root
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.maintenance_testlib import base_state, law_profile, policy_context, with_asset_health

    state = with_asset_health(
        base_state(),
        asset_id="asset.health.ctrl8.alpha",
        failure_mode_ids=["failure.wear.general"],
        maintenance_backlog=120,
        wear_by_mode={"failure.wear.general": 20_000},
    )
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.ctrl8.maintenance.001",
            "process_id": "process.decay_tick",
            "inputs": {"dt_ticks": 3},
        },
        law_profile=law_profile(["process.decay_tick"]),
        authority_context=_authority_context(),
        navigation_indices={},
        policy_context=policy_context(failure_threshold_raw=2_000_000, failure_base_rate_raw=1_000),
    )
    return {"result": result, "state": state}


def _effect_hash(rows: list[dict]) -> str:
    from tools.xstack.compatx.canonical_json import canonical_sha256

    normalized = sorted(
        (dict(row) for row in list(rows or []) if isinstance(row, dict)),
        key=lambda row: (
            str(row.get("target_id", "")),
            str(row.get("effect_type_id", "")),
            int(row.get("applied_tick", 0) or 0),
            str(row.get("effect_id", "")),
        ),
    )
    return canonical_sha256(normalized)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first_interior = _run_interior_fixture(repo_root)
    second_interior = _run_interior_fixture(repo_root)
    if str((dict(first_interior.get("result") or {})).get("result", "")) != "complete":
        return {"status": "fail", "message": "interior migration fixture failed to execute"}
    if str((dict(second_interior.get("result") or {})).get("result", "")) != "complete":
        return {"status": "fail", "message": "second interior migration fixture failed to execute"}

    first_interior_state = dict(first_interior.get("state") or {})
    second_interior_state = dict(second_interior.get("state") or {})
    if "interior_movement_constraints" in first_interior_state:
        return {"status": "fail", "message": "legacy interior_movement_constraints temp flag should be removed"}
    interior_effect_rows = [dict(row) for row in list(first_interior_state.get("effect_rows") or []) if isinstance(row, dict)]
    interior_types = sorted(set(str(row.get("effect_type_id", "")).strip() for row in interior_effect_rows if str(row.get("effect_type_id", "")).strip()))
    if "effect.access_restricted" not in interior_types:
        return {"status": "fail", "message": "interior migration did not emit effect.access_restricted"}
    if "effect.visibility_reduction" not in interior_types:
        return {"status": "fail", "message": "interior migration did not emit effect.visibility_reduction"}
    if _effect_hash(interior_effect_rows) != _effect_hash(list(second_interior_state.get("effect_rows") or [])):
        return {"status": "fail", "message": "interior effect migration is not deterministic"}

    first_decay = _run_decay_fixture(repo_root)
    second_decay = _run_decay_fixture(repo_root)
    if str((dict(first_decay.get("result") or {})).get("result", "")) != "complete":
        return {"status": "fail", "message": "maintenance migration fixture failed to execute"}
    if str((dict(second_decay.get("result") or {})).get("result", "")) != "complete":
        return {"status": "fail", "message": "second maintenance migration fixture failed to execute"}

    first_decay_state = dict(first_decay.get("state") or {})
    second_decay_state = dict(second_decay.get("state") or {})
    decay_effect_rows = [
        dict(row)
        for row in list(first_decay_state.get("effect_rows") or [])
        if isinstance(row, dict) and str(row.get("effect_type_id", "")).strip() == "effect.machine_degraded"
    ]
    if not decay_effect_rows:
        return {"status": "fail", "message": "maintenance migration did not emit effect.machine_degraded"}
    if _effect_hash(decay_effect_rows) != _effect_hash(
        [
            dict(row)
            for row in list(second_decay_state.get("effect_rows") or [])
            if isinstance(row, dict) and str(row.get("effect_type_id", "")).strip() == "effect.machine_degraded"
        ]
    ):
        return {"status": "fail", "message": "maintenance effect migration is not deterministic"}

    return {"status": "pass", "message": "temp flag migration equivalence preserved via deterministic effects"}

