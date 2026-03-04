"""FAST test: external impulse boundary flux is logged deterministically."""

from __future__ import annotations

import copy
import re
import sys


TEST_ID = "test_boundary_flux_logged"
TEST_TAGS = ["fast", "physics", "energy", "boundary_flux"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_once(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_free_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_free_state,
    )

    state = seed_free_state(initial_velocity_x=0)
    body_id = "body.vehicle.mob.free.alpha"
    law = law_profile(["process.apply_impulse"])
    authority = authority_context()
    policy = policy_context()
    policy["physics_profile_id"] = "phys.realistic.default"
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.phys.boundary_flux.001",
            "process_id": "process.apply_impulse",
            "inputs": {
                "application_id": "impulse.boundary.alpha.0001",
                "target_assembly_id": body_id,
                "impulse_vector": {"x": 1200, "y": 0, "z": 0},
                "torque_impulse": 0,
                "external_impulse_logged": True,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"result": dict(result), "state": dict(state)}


def run(repo_root: str):
    first = _run_once(repo_root=repo_root)
    second = _run_once(repo_root=repo_root)
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "first apply_impulse run refused: {}".format(first_result)}
    if str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "second apply_impulse run refused: {}".format(second_result)}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    flux_rows = [dict(row) for row in list(first_state.get("boundary_flux_events") or []) if isinstance(row, dict)]
    if len(flux_rows) != 1:
        return {"status": "fail", "message": "expected one boundary_flux_event for external impulse"}
    flux_row = dict(flux_rows[0])
    if str(flux_row.get("direction", "")).strip().lower() != "in":
        return {"status": "fail", "message": "external impulse boundary flux must be inbound"}
    if str(flux_row.get("quantity_id", "")).strip() != "quantity.energy_total":
        return {"status": "fail", "message": "boundary flux must target quantity.energy_total"}
    if int(flux_row.get("value", 0) or 0) <= 0:
        return {"status": "fail", "message": "boundary flux value must be positive"}

    chain_a = str(first_state.get("boundary_flux_hash_chain", "")).strip().lower()
    chain_b = str(second_state.get("boundary_flux_hash_chain", "")).strip().lower()
    if (not _HASH64.fullmatch(chain_a)) or (not _HASH64.fullmatch(chain_b)):
        return {"status": "fail", "message": "boundary_flux_hash_chain missing/invalid"}
    if chain_a != chain_b:
        return {"status": "fail", "message": "boundary_flux_hash_chain drifted across deterministic runs"}

    info_rows = [dict(row) for row in list(first_state.get("info_artifact_rows") or []) if isinstance(row, dict)]
    artifact_types = sorted(
        set(
            str((dict(row.get("extensions") or {})).get("artifact_type_id", "")).strip()
            for row in info_rows
            if str((dict(row.get("extensions") or {})).get("artifact_type_id", "")).strip()
        )
    )
    if "artifact.boundary_flux_event" not in set(artifact_types):
        return {"status": "fail", "message": "boundary_flux_event artifact was not emitted"}
    return {"status": "pass", "message": "boundary flux events are logged and hash-chained deterministically"}
