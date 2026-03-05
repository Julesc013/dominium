"""FAST test: POLL-2 measurement process emits observation artifact + knowledge receipt."""

from __future__ import annotations

import sys


TEST_ID = "test_measurement_artifact_created"
TEST_TAGS = ["fast", "pollution", "measurement", "epistemics"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.pollution.dispersion_engine import concentration_field_id_for_pollutant
    from src.fields import build_field_cell
    from tools.xstack.testx.tests.pollution_testlib import (
        execute_pollution_measure,
        seed_pollution_state,
    )

    pollutant_id = "pollutant.smoke_particulate"
    cell_id = "cell.sensor.0"
    state = seed_pollution_state()
    state["field_cells"] = [
        build_field_cell(
            field_id=concentration_field_id_for_pollutant(pollutant_id),
            cell_id=cell_id,
            value=37,
            last_updated_tick=0,
            value_kind="scalar",
        )
    ]

    out = execute_pollution_measure(
        repo_root=repo_root,
        state=state,
        inputs={
            "pollutant_id": pollutant_id,
            "spatial_scope_id": cell_id,
            "sensor_type_id": "sensor.air_quality_basic",
            "subject_id": "subject.operator.pollution",
            "instrument_id": "instrument.sensor.alpha",
        },
    )
    if str(out.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "pollution measure failed: {}".format(out)}

    measurement_rows = [
        dict(row)
        for row in list(state.get("pollution_measurement_rows") or [])
        if isinstance(row, dict)
    ]
    if not measurement_rows:
        return {"status": "fail", "message": "pollution_measurement_rows missing after process.pollution_measure"}
    if not any(int(row.get("measured_concentration", 0) or 0) == 37 for row in measurement_rows):
        return {"status": "fail", "message": "expected measured concentration not captured in measurement row"}

    info_rows = [
        dict(row)
        for row in list(state.get("info_artifact_rows") or [])
        if isinstance(row, dict)
        and str(row.get("artifact_family_id", "")).strip() == "OBSERVATION"
        and str(dict(row.get("extensions") or {}).get("artifact_type_id", "")).strip()
        == "artifact.pollution.measurement"
    ]
    if not info_rows:
        return {"status": "fail", "message": "measurement OBSERVATION artifact missing"}

    receipt_rows = [
        dict(row)
        for row in list(state.get("knowledge_receipt_rows") or [])
        if isinstance(row, dict)
        and str(row.get("subject_id", "")).strip() == "subject.operator.pollution"
    ]
    if not receipt_rows:
        return {"status": "fail", "message": "knowledge receipt missing for measuring subject"}
    if not str(state.get("pollution_measurement_hash_chain", "")).strip():
        return {"status": "fail", "message": "pollution_measurement_hash_chain missing"}
    return {"status": "pass", "message": "measurement produced observation artifact and knowledge receipt"}
