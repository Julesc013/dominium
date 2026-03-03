"""FAST test: THERM-2 cure progress process is deterministic."""

from __future__ import annotations

import copy
import sys

from tools.xstack.compatx.canonical_json import canonical_sha256


TEST_ID = "test_cure_progress_deterministic"
TEST_TAGS = ["fast", "thermal", "curing", "determinism"]


def _law_profile() -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile as construction_law_profile

    return construction_law_profile(["process.cure_state_tick"])


def _authority_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import authority_context as construction_authority_context

    return construction_authority_context(["session.boot", "entitlement.inspect"], privilege_level="operator")


def _policy_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import policy_context as construction_policy_context

    return construction_policy_context(max_compute_units_per_tick=4096)


def _seed_state() -> dict:
    from tools.xstack.testx.tests.construction_testlib import base_state as construction_base_state

    state = copy.deepcopy(construction_base_state())
    state["simulation_time"] = {
        "schema_version": "1.0.0",
        "tick": 100,
        "sim_time_us": 100_000,
        "tick_rate": 1,
        "deterministic_clock": {"tick_duration_ms": 1000},
    }
    state["cure_states"] = [
        {
            "schema_version": "1.0.0",
            "target_id": "structure.cure.pad.001",
            "cure_progress": 100,
            "last_update_tick": 99,
            "defect_flags": [],
            "deterministic_fingerprint": "",
            "extensions": {
                "material_id": "material.concrete_basic",
                "cure_temp_min": 27815,
                "cure_temp_max": 30815,
                "cure_rate_permille": 25,
                "defect_rate": 5,
            },
        }
    ]
    return state


def _run_once(state: dict) -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent

    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.therm2.cure.tick.001",
            "process_id": "process.cure_state_tick",
            "inputs": {
                "target_id": "structure.cure.pad.001",
                "temperature_by_target": {"structure.cure.pad.001": 29315},
                "cure_rate_permille": 25,
                "defect_rate": 5,
            },
        },
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        navigation_indices={},
        policy_context=_policy_context(),
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first_state = _seed_state()
    second_state = _seed_state()

    first_result = _run_once(first_state)
    second_result = _run_once(second_state)
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.cure_state_tick refused in deterministic fixture"}

    first_rows = [dict(row) for row in list(first_state.get("cure_states") or []) if isinstance(row, dict)]
    second_rows = [dict(row) for row in list(second_state.get("cure_states") or []) if isinstance(row, dict)]
    if canonical_sha256(first_rows) != canonical_sha256(second_rows):
        return {"status": "fail", "message": "cure_states diverged across identical deterministic runs"}

    row = next((r for r in first_rows if str(r.get("target_id", "")).strip() == "structure.cure.pad.001"), {})
    if not row:
        return {"status": "fail", "message": "missing cure state row for fixture target"}
    progress = int(row.get("cure_progress", 0))
    if progress <= 100:
        return {"status": "fail", "message": "cure progress did not advance inside cure window"}
    return {"status": "pass", "message": "cure progress deterministic and monotonic in fixture"}

