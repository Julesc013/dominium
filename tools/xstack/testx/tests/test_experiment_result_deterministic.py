"""FAST test: PROC-7 experiment results are deterministic across equivalent inputs."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_experiment_result_deterministic"
TEST_TAGS = ["fast", "proc", "proc7", "experiment", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _measurement_rows(reversed_order: bool) -> list[dict]:
    rows = [
        {
            "measurement_id": "measurement.proc7.b",
            "pollutant_id": "pollutant.pm25",
            "measured_concentration": 18,
            "calibration_cert_id": "cert.measurement.proc7",
        },
        {
            "measurement_id": "measurement.proc7.a",
            "pollutant_id": "pollutant.co2",
            "measured_concentration": 42,
        },
    ]
    if reversed_order:
        rows = list(reversed(rows))
    return rows


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc7_testlib import cloned_state, run_experiment_cycle

    first_state = cloned_state(repo_root)
    second_state = cloned_state(repo_root)

    first = run_experiment_cycle(
        repo_root=repo_root,
        state=first_state,
        run_id="run.proc7.det.001",
        measurement_rows=_measurement_rows(False),
    )
    second = run_experiment_cycle(
        repo_root=repo_root,
        state=second_state,
        run_id="run.proc7.det.001",
        measurement_rows=_measurement_rows(True),
    )

    first_complete = dict(first.get("complete") or {})
    second_complete = dict(second.get("complete") or {})
    if str(first_complete.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first experiment completion did not complete"}
    if str(second_complete.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second experiment completion did not complete"}

    first_result_rows = sorted(
        [
            dict(row)
            for row in list(first_state.get("experiment_result_rows") or [])
            if isinstance(row, dict)
        ],
        key=lambda row: str(row.get("result_id", "")),
    )
    second_result_rows = sorted(
        [
            dict(row)
            for row in list(second_state.get("experiment_result_rows") or [])
            if isinstance(row, dict)
        ],
        key=lambda row: str(row.get("result_id", "")),
    )
    if not first_result_rows or not second_result_rows:
        return {"status": "fail", "message": "experiment result rows were not emitted"}
    if first_result_rows != second_result_rows:
        return {"status": "fail", "message": "experiment result rows drifted across equivalent inputs"}

    for row in first_result_rows:
        fingerprint = str(row.get("deterministic_fingerprint", "")).strip().lower()
        if not _HASH64.fullmatch(fingerprint):
            return {"status": "fail", "message": "experiment result fingerprint missing/invalid"}

    for key in (
        "experiment_result_hash_chain",
        "experiment_run_binding_hash_chain",
        "candidate_process_hash_chain",
        "candidate_model_binding_hash_chain",
    ):
        one = str(first_state.get(key, "")).strip().lower()
        two = str(second_state.get(key, "")).strip().lower()
        if one != two:
            return {"status": "fail", "message": "{} drifted across equivalent runs".format(key)}
        if not _HASH64.fullmatch(one):
            return {"status": "fail", "message": "{} missing/invalid".format(key)}

    return {"status": "pass", "message": "PROC-7 experiment results are deterministic"}

