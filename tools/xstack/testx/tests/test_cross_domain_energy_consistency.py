"""FAST test: PHYS/ELEC energy pathways remain ledger-consistent across domains."""

from __future__ import annotations

import copy
import json
import os
import sys


TEST_ID = "test_cross_domain_energy_consistency"
TEST_TAGS = ["fast", "physics", "energy", "cross_domain"]


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _boundary_allowed_transform_ids(repo_root: str) -> set[str]:
    rel_path = "data/registries/energy_transformation_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    rows = list(payload.get("energy_transformations") or [])
    if not rows:
        rows = list((dict(payload.get("record") or {})).get("energy_transformations") or [])
    out: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        if not bool(row.get("boundary_allowed", False)):
            continue
        token = str(row.get("transformation_id", "")).strip()
        if token:
            out.add(token)
    return out


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.elec_testlib import (
        authority_context as elec_authority_context,
        build_power_graph,
        law_profile as elec_law_profile,
        model_binding_rows,
        policy_context as elec_policy_context,
    )
    from tools.xstack.testx.tests.mobility_free_testlib import seed_free_state

    state = seed_free_state(initial_velocity_x=0)
    state["power_network_graphs"] = [build_power_graph(edge_count=1, resistance_proxy=9, capacity_rating=220)]
    state["model_bindings"] = model_binding_rows(resistive_demand_p=120, motor_demand_p=80, motor_pf_permille=900)
    state.setdefault("elec_flow_channels", [])
    state.setdefault("elec_edge_status_rows", [])
    state.setdefault("elec_node_status_rows", [])
    state.setdefault("elec_network_runtime_state", {"extensions": {}})

    law = elec_law_profile(["process.apply_impulse", "process.elec.network_tick"])
    authority = elec_authority_context()
    policy = elec_policy_context(max_compute_units_per_tick=4096, e1_enabled=True)
    policy["physics_profile_id"] = "phys.realistic.default"

    impulse = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.phys.energy.cross_domain.impulse",
            "process_id": "process.apply_impulse",
            "inputs": {
                "application_id": "impulse.energy.cross_domain",
                "target_assembly_id": "body.vehicle.mob.free.alpha",
                "impulse_vector": {"x": 1000, "y": 0, "z": 0},
                "torque_impulse": 0,
                "external_impulse_logged": True,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(impulse.get("result", "")) != "complete":
        return {"status": "fail", "message": "apply_impulse failed in cross-domain energy test: {}".format(impulse)}

    elec_tick = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.phys.energy.cross_domain.elec",
            "process_id": "process.elec.network_tick",
            "inputs": {},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(elec_tick.get("result", "")) != "complete":
        return {"status": "fail", "message": "elec.network_tick failed in cross-domain energy test: {}".format(elec_tick)}

    ledger_rows = [dict(row) for row in list(state.get("energy_ledger_entries") or []) if isinstance(row, dict)]
    if len(ledger_rows) < 2:
        return {"status": "fail", "message": "expected cross-domain run to produce at least two energy ledger rows"}

    transforms = set(str(row.get("transformation_id", "")).strip() for row in ledger_rows if str(row.get("transformation_id", "")).strip())
    if "transform.impulse_to_kinetic" not in transforms:
        return {"status": "fail", "message": "missing impulse_to_kinetic transform entry"}
    if "transform.electrical_to_thermal" not in transforms:
        return {"status": "fail", "message": "missing electrical_to_thermal transform entry"}

    boundary_rows = [dict(row) for row in list(state.get("boundary_flux_events") or []) if isinstance(row, dict)]
    if not boundary_rows:
        return {"status": "fail", "message": "cross-domain run expected at least one boundary_flux_event"}

    boundary_allowed = _boundary_allowed_transform_ids(repo_root)
    ledger_total_delta = int(
        sum(
            _as_int(row.get("energy_total_delta", 0), 0)
            for row in ledger_rows
            if str(row.get("transformation_id", "")).strip() not in boundary_allowed
        )
    )
    flux_total_delta = int(
        sum(
            _as_int(row.get("value", 0), 0)
            if str(row.get("direction", "in")).strip().lower() == "in"
            else -_as_int(row.get("value", 0), 0)
            for row in boundary_rows
        )
    )
    expected_total = int(ledger_total_delta + flux_total_delta)
    totals = dict(state.get("energy_quantity_totals") or {})
    actual_total = int(_as_int(totals.get("quantity.energy_total", 0), 0))
    if expected_total != actual_total:
        return {
            "status": "fail",
            "message": "energy_total mismatch (expected {}, actual {})".format(expected_total, actual_total),
        }
    return {"status": "pass", "message": "cross-domain PHYS/ELEC energy ledger accounting is consistent"}
