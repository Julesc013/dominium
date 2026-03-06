"""FAST test: PROC-3 QC results remain traceable to run/batch and measurement artifacts."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_qc_results_traceable"
TEST_TAGS = ["fast", "proc", "qc", "traceability"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _trace_policy_payload() -> dict:
    return {
        "schema_id": "dominium.registry.qc_policy_registry",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.qc_policy_registry",
            "registry_version": "1.0.0",
            "qc_policies": [
                {
                    "schema_version": "1.0.0",
                    "qc_policy_id": "qc.trace_all",
                    "sampling_rate": 1000,
                    "sampling_strategy_id": "sample.hash_based",
                    "test_procedure_refs": ["test.dimensions_basic"],
                    "fail_action": "accept_with_warning",
                    "deterministic_fingerprint": "",
                    "extensions": {"source": "test.proc3"},
                }
            ],
            "extensions": {},
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc3_testlib import run_proc3_qc_case

    payload = run_proc3_qc_case(
        repo_root=repo_root,
        run_id="run.proc3.traceability",
        qc_policy_id="qc.trace_all",
        output_batch_ids=["batch.output.01", "batch.output.02", "batch.output.03"],
        qc_policy_registry_payload=_trace_policy_payload(),
    )
    if str((dict(payload.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process_run_end failed"}
    state = dict(payload.get("state") or {})
    run_id = str((dict(payload.get("run_record") or {})).get("run_id", "")).strip()
    if not run_id:
        return {"status": "fail", "message": "missing run_id in finalized run record"}

    qc_rows = [
        dict(row)
        for row in list(state.get("qc_result_record_rows") or [])
        if isinstance(row, dict)
    ]
    if not qc_rows:
        return {"status": "fail", "message": "missing qc_result_record_rows"}
    batch_ids = set()
    for row in qc_rows:
        batch_id = str(row.get("batch_id", "")).strip()
        if str(row.get("run_id", "")).strip() != run_id:
            return {"status": "fail", "message": "qc_result row run_id mismatch"}
        if not batch_id:
            return {"status": "fail", "message": "qc_result row missing batch_id"}
        batch_ids.add(batch_id)
        fingerprint = str(row.get("deterministic_fingerprint", "")).strip().lower()
        if not _HASH64.fullmatch(fingerprint):
            return {"status": "fail", "message": "qc_result deterministic_fingerprint missing/invalid"}
        ext = dict(row.get("extensions") or {})
        if str(ext.get("visibility_policy", "")).strip() != "policy.epistemic.inspector":
            return {"status": "fail", "message": "qc_result row missing inspector visibility policy"}

    decision_rows = [
        dict(row)
        for row in list(state.get("qc_sampling_decision_rows") or [])
        if isinstance(row, dict)
    ]
    decision_batch_ids = set(str(row.get("batch_id", "")).strip() for row in decision_rows if str(row.get("batch_id", "")).strip())
    if batch_ids - decision_batch_ids:
        return {"status": "fail", "message": "qc_result rows missing matching sampling decision rows"}

    measurement_rows = [
        dict(row)
        for row in list(state.get("qc_measurement_observation_rows") or [])
        if isinstance(row, dict)
    ]
    if not measurement_rows:
        return {"status": "fail", "message": "expected measurement observation rows for sampled qc policy"}
    for row in measurement_rows:
        if str(row.get("run_id", "")).strip() != run_id:
            return {"status": "fail", "message": "measurement row run_id mismatch"}
        if not str(row.get("batch_id", "")).strip():
            return {"status": "fail", "message": "measurement row missing batch_id"}

    return {"status": "pass", "message": "PROC-3 QC results and measurements are traceable"}
