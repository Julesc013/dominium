"""FAST test: POLL-2 threshold crossing emits deterministic health-risk events."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_threshold_crossing_event"
TEST_TAGS = ["fast", "pollution", "exposure", "threshold"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from pollution.dispersion_engine import concentration_field_id_for_pollutant
    from tools.xstack.testx.tests.pollution_dispersion_testlib import (
        build_pollution_field_inputs,
        execute_pollution_dispersion_tick,
        seed_state_with_pollution_emission,
    )

    pollutant_id = "pollutant.smoke_particulate"
    cell_id = "cell.0.0.0"
    state = seed_state_with_pollution_emission(
        repo_root=repo_root,
        pollutant_id=pollutant_id,
        emitted_mass=40,
        source_cell_id=cell_id,
    )
    inputs = build_pollution_field_inputs(
        repo_root=repo_root,
        pollutant_id=pollutant_id,
        cell_ids=[cell_id],
    )
    concentration_field_id = concentration_field_id_for_pollutant(pollutant_id)
    for row in list(inputs.get("field_cells") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("field_id", "")).strip() != concentration_field_id:
            continue
        if str(row.get("cell_id", "")).strip() != cell_id:
            continue
        row["value"] = 50
    inputs["subjects"] = [
        {
            "subject_id": "subject.pollution.threshold",
            "spatial_scope_id": cell_id,
            "exposure_factor_permille": 1000,
            "extensions": {},
        }
    ]
    policy_overrides = {
        "exposure_threshold_registry": {
            "record": {
                "exposure_thresholds": [
                    {
                        "pollutant_id": pollutant_id,
                        "warning_threshold": 10,
                        "critical_threshold": 20,
                    }
                ]
            }
        }
    }
    out = execute_pollution_dispersion_tick(
        repo_root=repo_root,
        state=state,
        inputs=copy.deepcopy(inputs),
        policy_overrides=policy_overrides,
    )
    if str(out.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "dispersion tick failed: {}".format(out)}

    threshold_events = [
        dict(row)
        for row in list(state.get("pollution_health_risk_event_rows") or [])
        if isinstance(row, dict)
        and str(row.get("subject_id", "")).strip() == "subject.pollution.threshold"
        and str(row.get("pollutant_id", "")).strip() == pollutant_id
    ]
    if not threshold_events:
        return {"status": "fail", "message": "threshold crossing did not emit health risk event"}
    if not any(str(row.get("threshold_crossed", "")).strip() == "critical" for row in threshold_events):
        return {"status": "fail", "message": "critical threshold crossing event missing"}

    hazard_rows = [
        dict(row)
        for row in list(state.get("pollution_hazard_hook_rows") or [])
        if isinstance(row, dict)
        and str(row.get("subject_id", "")).strip() == "subject.pollution.threshold"
        and str(row.get("pollutant_id", "")).strip() == pollutant_id
        and str(row.get("hazard_hook_id", "")).strip() == "hazard.health_risk_stub"
    ]
    if not hazard_rows:
        return {"status": "fail", "message": "hazard.health_risk_stub hook row missing for threshold crossing"}
    return {"status": "pass", "message": "threshold crossing emits deterministic health risk + hazard rows"}
