"""FAST test: THERM-2 phase transform emits canonical event/provenance traces."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_phase_transform_emits_provenance"
TEST_TAGS = ["fast", "thermal", "phase", "provenance"]


def _law_profile() -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile as construction_law_profile

    return construction_law_profile(["process.material_transform_phase"])


def _authority_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import authority_context as construction_authority_context

    return construction_authority_context(["session.boot", "entitlement.inspect"], privilege_level="operator")


def _policy_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import policy_context as construction_policy_context

    return construction_policy_context(max_compute_units_per_tick=4096)


def _seed_state() -> dict:
    from src.materials.composition_engine import create_material_batch
    from tools.xstack.testx.tests.construction_testlib import base_state as construction_base_state

    state = copy.deepcopy(construction_base_state())
    state["simulation_time"] = {
        "schema_version": "1.0.0",
        "tick": 33,
        "sim_time_us": 33_000,
        "tick_rate": 1,
        "deterministic_clock": {"tick_duration_ms": 1000},
    }
    batch = create_material_batch(
        material_id="material.water",
        quantity_mass_raw=1000,
        origin_process_id="process.seed",
        origin_tick=0,
        parent_batch_ids=[],
        quality_distribution={},
    )
    batch["batch_id"] = "batch.therm2.water.001"
    batch_ext = dict(batch.get("extensions") or {})
    batch_ext["phase_tag"] = "liquid"
    batch["extensions"] = batch_ext
    state["material_batches"] = [dict(batch)]
    return state


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent

    state = _seed_state()
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.therm2.phase.transform.001",
            "process_id": "process.material_transform_phase",
            "inputs": {
                "batch_id": "batch.therm2.water.001",
                "temperature": 26000,
            },
        },
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        navigation_indices={},
        policy_context=_policy_context(),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.material_transform_phase refused in phase provenance fixture"}

    phase_events = [dict(row) for row in list(state.get("thermal_phase_events") or []) if isinstance(row, dict)]
    if not phase_events:
        return {"status": "fail", "message": "phase transform did not emit thermal_phase_events"}
    event = phase_events[-1]
    if str(event.get("from_phase", "")).strip() != "liquid" or str(event.get("to_phase", "")).strip() != "solid":
        return {"status": "fail", "message": "unexpected phase transition payload in emitted event"}
    if not str(event.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "phase event missing deterministic_fingerprint"}

    artifact_rows = [dict(row) for row in list(state.get("info_artifact_rows") or []) if isinstance(row, dict)]
    if not artifact_rows:
        return {"status": "fail", "message": "phase transform did not emit info artifact provenance"}
    if not any(
        str(dict(row.get("extensions") or {}).get("event_type", "")).strip() == "incident.phase_transition"
        for row in artifact_rows
    ):
        return {"status": "fail", "message": "phase transform missing incident.phase_transition record artifact"}
    return {"status": "pass", "message": "phase transform emits deterministic event and provenance artifact"}

