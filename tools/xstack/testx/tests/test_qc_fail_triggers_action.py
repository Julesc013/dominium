"""FAST test: PROC-3 QC failure deterministically triggers policy action."""

from __future__ import annotations

import sys


TEST_ID = "test_qc_fail_triggers_action"
TEST_TAGS = ["fast", "proc", "qc", "action"]


def _reject_policy_payload() -> dict:
    return {
        "schema_id": "dominium.registry.qc_policy_registry",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.qc_policy_registry",
            "registry_version": "1.0.0",
            "qc_policies": [
                {
                    "schema_version": "1.0.0",
                    "qc_policy_id": "qc.force_reject",
                    "sampling_rate": 1000,
                    "sampling_strategy_id": "sample.hash_based",
                    "test_procedure_refs": ["test.force_fail"],
                    "fail_action": "reject_batch",
                    "deterministic_fingerprint": "",
                    "extensions": {
                        "source": "test.proc3",
                        "drift_escalation_fail_rate_permille": 100,
                        "cert_invalidation_on_fail": True,
                    },
                }
            ],
            "extensions": {},
        },
    }


def _force_fail_test_payload() -> dict:
    return {
        "schema_id": "dominium.registry.test_procedure_registry",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.test_procedure_registry",
            "registry_version": "1.0.0",
            "test_procedures": [
                {
                    "schema_version": "1.0.0",
                    "test_id": "test.force_fail",
                    "measured_quantity_ids": ["quality.yield_factor"],
                    "thresholds": {
                        "quality.yield_factor": {"max": 0},
                    },
                    "tolerance_policy_id": "tol.strict",
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
        run_id="run.proc3.reject",
        qc_policy_id="qc.force_reject",
        output_batch_ids=["batch.output.01", "batch.output.02"],
        qc_policy_registry_payload=_reject_policy_payload(),
        test_procedure_registry_payload=_force_fail_test_payload(),
    )
    if str((dict(payload.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process_run_end failed"}
    state = dict(payload.get("state") or {})
    qc_rows = [
        dict(row)
        for row in list(state.get("qc_result_record_rows") or [])
        if isinstance(row, dict)
    ]
    if not qc_rows:
        return {"status": "fail", "message": "missing qc_result_record_rows"}
    if any(str(row.get("action_taken", "")).strip() != "reject" for row in qc_rows):
        return {"status": "fail", "message": "expected reject action for all failing sampled rows"}
    if any(bool(row.get("passed", True)) for row in qc_rows):
        return {"status": "fail", "message": "expected sampled rows to fail under force-fail test policy"}

    batch_rows = [
        dict(row)
        for row in list(state.get("batch_quality_rows") or [])
        if isinstance(row, dict)
    ]
    if not batch_rows:
        return {"status": "fail", "message": "missing batch_quality_rows"}
    for row in batch_rows:
        ext = dict(row.get("extensions") or {})
        if str(ext.get("qc_status", "")).strip() != "rejected":
            return {"status": "fail", "message": "batch row missing rejected qc_status"}
        if bool(ext.get("qc_usable", True)):
            return {"status": "fail", "message": "rejected batch row must be marked qc_usable=false"}

    return {"status": "pass", "message": "PROC-3 QC failures trigger deterministic reject action"}
