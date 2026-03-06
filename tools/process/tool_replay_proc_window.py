#!/usr/bin/env python3
"""Verify deterministic replay hashes for PROC-9 process windows."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Mapping, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.process.tool_replay_capsule_window import verify_capsule_replay_window  # noqa: E402
from tools.process.tool_replay_drift_window import verify_drift_replay_window  # noqa: E402
from tools.process.tool_replay_maturity_window import verify_maturity_replay_window  # noqa: E402
from tools.process.tool_replay_pipeline_window import verify_pipeline_replay_window  # noqa: E402
from tools.process.tool_replay_process_window import verify_process_replay_window  # noqa: E402
from tools.process.tool_replay_qc_window import verify_qc_replay_window  # noqa: E402
from tools.process.tool_replay_quality_window import verify_quality_replay_window  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, Mapping):
        return {}, "json root must be an object"
    return dict(payload), ""


def _state_payload(payload: Mapping[str, object]) -> dict:
    ext = _as_map(payload.get("extensions"))
    snap = _as_map(ext.get("final_state_snapshot"))
    return snap if snap else dict(payload)


def _promotion_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("candidate_promotion_record_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda row: (
            int(max(0, int(row.get("tick", 0) or 0))),
            str(row.get("record_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "record_id": str(row.get("record_id", "")).strip(),
                "candidate_id": str(row.get("candidate_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "tick": int(max(0, int(row.get("tick", 0) or 0))),
            }
            for row in rows
        ]
    )


def verify_proc_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    state = _state_payload(state_payload)
    expected_state = _state_payload(expected_payload) if expected_payload else None

    process_report = verify_process_replay_window(state_payload=state)
    quality_report = verify_quality_replay_window(state_payload=state)
    qc_report = verify_qc_replay_window(state_payload=state)
    maturity_report = verify_maturity_replay_window(state_payload=state)
    drift_report = verify_drift_replay_window(state_payload=state)
    capsule_report = verify_capsule_replay_window(state_payload=state)
    pipeline_report = verify_pipeline_replay_window(state_payload=state)

    observed = {
        "process_run_record_hash_chain": str(
            _as_map(process_report.get("observed")).get("process_run_record_hash_chain", "")
        ).strip(),
        "process_step_record_hash_chain": str(
            _as_map(process_report.get("observed")).get("process_step_record_hash_chain", "")
        ).strip(),
        "process_quality_hash_chain": str(
            _as_map(quality_report.get("observed")).get("process_quality_hash_chain", "")
        ).strip(),
        "qc_result_hash_chain": str(
            _as_map(qc_report.get("observed")).get("qc_result_hash_chain", "")
        ).strip(),
        "process_maturity_hash_chain": str(
            _as_map(maturity_report.get("observed")).get("process_maturity_hash_chain", "")
        ).strip(),
        "drift_event_hash_chain": str(
            _as_map(drift_report.get("observed")).get("drift_event_hash_chain", "")
        ).strip(),
        "capsule_execution_hash_chain": str(
            _as_map(capsule_report.get("observed")).get("capsule_execution_hash_chain", "")
        ).strip(),
        "compiled_model_hash_chain": str(
            _as_map(capsule_report.get("observed")).get("compiled_model_hash_chain", "")
        ).strip()
        or str(_as_map(pipeline_report.get("observed")).get("compiled_model_hash_chain", "")).strip(),
        "candidate_promotion_hash_chain": _promotion_hash(state),
        "deployment_hash_chain": str(
            _as_map(pipeline_report.get("observed")).get("deployment_hash_chain", "")
        ).strip(),
    }
    recorded = {
        key: str(state.get(key, "")).strip().lower()
        for key in observed.keys()
    }
    violations = []
    for key in observed.keys():
        if recorded.get(key) and recorded.get(key) != str(observed.get(key, "")).strip().lower():
            violations.append("recorded {} does not match replay hash".format(key))

    report = {
        "result": "complete" if not violations else "violation",
        "observed": observed,
        "recorded": recorded,
        "violations": violations,
    }
    if expected_state:
        expected = verify_proc_replay_window(state_payload=expected_state).get("observed", {})
        report["expected"] = expected
        for key in observed.keys():
            if str(expected.get(key, "")).strip().lower() != str(observed.get(key, "")).strip().lower():
                report["violations"].append("{} mismatch against expected replay baseline".format(key))
        if report["violations"]:
            report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(
        dict(report, deterministic_fingerprint="")
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify deterministic replay hashes for PROC-9 windows."
    )
    parser.add_argument("--state-path", default="build/process/proc9_report.json")
    parser.add_argument("--expected-state-path", default="")
    args = parser.parse_args()

    state_payload, state_err = _read_json(os.path.normpath(os.path.abspath(str(args.state_path))))
    if state_err:
        print(json.dumps({"result": "error", "reason": "state_read_failed", "details": state_err}, indent=2, sort_keys=True))
        return 2
    expected_payload = None
    expected_path = str(args.expected_state_path or "").strip()
    if expected_path:
        expected_payload, expected_err = _read_json(os.path.normpath(os.path.abspath(expected_path)))
        if expected_err:
            print(json.dumps({"result": "error", "reason": "expected_state_read_failed", "details": expected_err}, indent=2, sort_keys=True))
            return 2

    report = verify_proc_replay_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
