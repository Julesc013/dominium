"""FAST test: PROC-3 every-N QC sampling decisions are deterministic and stable."""

from __future__ import annotations

import sys


TEST_ID = "test_every_n_sampling_deterministic"
TEST_TAGS = ["fast", "proc", "qc", "sampling"]


def _every_n_policy_payload() -> dict:
    return {
        "schema_id": "dominium.registry.qc_policy_registry",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.qc_policy_registry",
            "registry_version": "1.0.0",
            "qc_policies": [
                {
                    "schema_version": "1.0.0",
                    "qc_policy_id": "qc.every_n_test",
                    "sampling_rate": 500,
                    "sampling_strategy_id": "sample.every_n",
                    "test_procedure_refs": ["test.dimensions_basic"],
                    "fail_action": "accept_with_warning",
                    "deterministic_fingerprint": "",
                    "extensions": {
                        "source": "test.proc3",
                        "every_n": 2,
                    },
                }
            ],
            "extensions": {},
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.proc3_testlib import run_proc3_qc_case

    batch_ids = [
        "batch.output.01",
        "batch.output.02",
        "batch.output.03",
        "batch.output.04",
        "batch.output.05",
    ]
    expected_sampled = ["batch.output.01", "batch.output.03", "batch.output.05"]
    payload = _every_n_policy_payload()

    first = run_proc3_qc_case(
        repo_root=repo_root,
        run_id="run.proc3.every_n",
        qc_policy_id="qc.every_n_test",
        output_batch_ids=batch_ids,
        qc_policy_registry_payload=payload,
    )
    second = run_proc3_qc_case(
        repo_root=repo_root,
        run_id="run.proc3.every_n",
        qc_policy_id="qc.every_n_test",
        output_batch_ids=batch_ids,
        qc_policy_registry_payload=payload,
    )
    if str((dict(first.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first process_run_end failed"}
    if str((dict(second.get("end") or {})).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second process_run_end failed"}

    first_rows = [
        dict(row)
        for row in list((dict(first.get("state") or {})).get("qc_result_record_rows") or [])
        if isinstance(row, dict)
    ]
    sampled_first = sorted(
        str(row.get("batch_id", "")).strip()
        for row in first_rows
        if bool(row.get("sampled", False))
    )
    if sampled_first != expected_sampled:
        return {"status": "fail", "message": "every-N sampled batch set mismatch: {}".format(sampled_first)}

    first_hash = str((dict(first.get("state") or {})).get("sampling_decision_hash_chain", "")).strip()
    second_hash = str((dict(second.get("state") or {})).get("sampling_decision_hash_chain", "")).strip()
    if not first_hash or first_hash != second_hash:
        return {"status": "fail", "message": "every-N sampling decision hash mismatch across equivalent runs"}

    return {"status": "pass", "message": "PROC-3 every-N sampling is deterministic"}
