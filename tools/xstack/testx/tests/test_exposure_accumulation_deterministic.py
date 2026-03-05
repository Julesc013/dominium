"""FAST test: POLL-1 exposure accumulation is deterministic for equivalent inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_exposure_accumulation_deterministic"
TEST_TAGS = ["fast", "pollution", "exposure", "determinism"]


def _snapshot(state: dict) -> dict:
    return {
        "pollution_exposure_state_rows": [dict(row) for row in list(state.get("pollution_exposure_state_rows") or []) if isinstance(row, dict)],
        "pollution_exposure_increment_rows": [dict(row) for row in list(state.get("pollution_exposure_increment_rows") or []) if isinstance(row, dict)],
        "pollution_hazard_hook_rows": [dict(row) for row in list(state.get("pollution_hazard_hook_rows") or []) if isinstance(row, dict)],
        "pollution_exposure_hash_chain": str(state.get("pollution_exposure_hash_chain", "")).strip(),
        "pollution_exposure_increment_hash_chain": str(state.get("pollution_exposure_increment_hash_chain", "")).strip(),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.pollution_dispersion_testlib import (
        build_pollution_field_inputs,
        execute_pollution_dispersion_tick,
        seed_state_with_pollution_emission,
    )

    pollutant_id = "pollutant.smoke_particulate"
    state_a = seed_state_with_pollution_emission(
        repo_root=repo_root,
        pollutant_id=pollutant_id,
        emitted_mass=84,
        source_cell_id="cell.0.0.0",
    )
    state_b = copy.deepcopy(state_a)
    inputs = build_pollution_field_inputs(
        repo_root=repo_root,
        pollutant_id=pollutant_id,
        cell_ids=["cell.0.0.0"],
    )
    inputs["subjects"] = [
        {
            "subject_id": "subject.pollution.alpha",
            "spatial_scope_id": "cell.0.0.0",
            "exposure_factor_permille": 1000,
            "extensions": {},
        }
    ]

    out_a = execute_pollution_dispersion_tick(repo_root=repo_root, state=state_a, inputs=copy.deepcopy(inputs))
    out_b = execute_pollution_dispersion_tick(repo_root=repo_root, state=state_b, inputs=copy.deepcopy(inputs))
    if str(out_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first exposure accumulation run failed: {}".format(out_a)}
    if str(out_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second exposure accumulation run failed: {}".format(out_b)}

    snap_a = _snapshot(state_a)
    snap_b = _snapshot(state_b)
    if snap_a != snap_b:
        return {"status": "fail", "message": "exposure accumulation drifted across equivalent runs"}
    if not snap_a["pollution_hazard_hook_rows"]:
        return {"status": "fail", "message": "hazard health-risk hook rows were not produced"}
    return {"status": "pass", "message": "exposure accumulation remains deterministic with hazard hook"}
