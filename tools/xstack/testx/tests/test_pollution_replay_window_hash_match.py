"""FAST test: POLL-2 replay-window verifier produces stable hash matches."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_replay_window_hash_match"
TEST_TAGS = ["fast", "pollution", "proof", "replay"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.fields import build_field_cell
    from src.pollution.dispersion_engine import concentration_field_id_for_pollutant
    from tools.pollution.tool_replay_exposure_window import verify_exposure_replay_window
    from tools.xstack.testx.tests.pollution_dispersion_testlib import (
        build_pollution_field_inputs,
        execute_pollution_dispersion_tick,
        seed_state_with_pollution_emission,
    )
    from tools.xstack.testx.tests.pollution_testlib import (
        execute_pollution_compliance_tick,
        execute_pollution_measure,
    )

    pollutant_id = "pollutant.smoke_particulate"
    cell_id = "cell.replay.0"
    state = seed_state_with_pollution_emission(
        repo_root=repo_root,
        pollutant_id=pollutant_id,
        emitted_mass=40,
        source_cell_id=cell_id,
    )
    dispersion_inputs = build_pollution_field_inputs(
        repo_root=repo_root,
        pollutant_id=pollutant_id,
        cell_ids=[cell_id],
    )
    concentration_field_id = concentration_field_id_for_pollutant(pollutant_id)
    for row in list(dispersion_inputs.get("field_cells") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("field_id", "")).strip() != concentration_field_id:
            continue
        if str(row.get("cell_id", "")).strip() != cell_id:
            continue
        row["value"] = 25
    dispersion_inputs["subjects"] = [
        {
            "subject_id": "subject.pollution.replay",
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
                        "warning_threshold": 5,
                        "critical_threshold": 20,
                    }
                ]
            }
        }
    }
    out = execute_pollution_dispersion_tick(
        repo_root=repo_root,
        state=state,
        inputs=copy.deepcopy(dispersion_inputs),
        policy_overrides=copy.deepcopy(policy_overrides),
    )
    if str(out.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "dispersion step failed: {}".format(out)}

    state["field_cells"] = [
        build_field_cell(
            field_id=concentration_field_id,
            cell_id=cell_id,
            value=25,
            last_updated_tick=0,
            value_kind="scalar",
        )
    ]
    measure_out = execute_pollution_measure(
        repo_root=repo_root,
        state=state,
        inputs={
            "pollutant_id": pollutant_id,
            "spatial_scope_id": cell_id,
            "sensor_type_id": "sensor.air_quality_basic",
            "subject_id": "subject.pollution.replay",
        },
    )
    if str(measure_out.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "measurement step failed: {}".format(measure_out)}

    compliance_out = execute_pollution_compliance_tick(
        repo_root=repo_root,
        state=state,
        inputs={
            "observed_statistic": "max",
            "region_cell_map": {"region.replay": [cell_id]},
            "channel_id": "channel.pollution.missing",
        },
        policy_overrides=copy.deepcopy(policy_overrides),
    )
    if str(compliance_out.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "compliance step failed: {}".format(compliance_out)}

    report = verify_exposure_replay_window(
        state_payload=state,
        expected_payload=copy.deepcopy(state),
    )
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "replay verifier returned violation: {}".format(report)}
    if list(report.get("violations") or []):
        return {"status": "fail", "message": "replay verifier reported non-empty violations"}
    return {"status": "pass", "message": "replay window hash verification is stable"}
