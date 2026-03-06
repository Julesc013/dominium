#!/usr/bin/env python3
"""Verify deterministic replay hashes for PROC-3 QC sampling outcomes."""

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

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


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
    final_state = _as_map(ext.get("final_state_snapshot"))
    return final_state if final_state else dict(payload)


def _qc_result_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("qc_result_record_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            str(item.get("run_id", "")),
            str(item.get("batch_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "run_id": str(row.get("run_id", "")).strip(),
                "batch_id": str(row.get("batch_id", "")).strip(),
                "sampled": bool(row.get("sampled", False)),
                "passed": bool(row.get("passed", False)),
                "fail_reason": (
                    None
                    if row.get("fail_reason") is None
                    else str(row.get("fail_reason", "")).strip()
                ),
                "action_taken": str(row.get("action_taken", "")).strip(),
            }
            for row in rows
        ]
    )


def _sampling_decision_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("qc_sampling_decision_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            str(item.get("run_id", "")),
            str(item.get("batch_id", "")),
            str(item.get("sampling_strategy_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "run_id": str(row.get("run_id", "")).strip(),
                "batch_id": str(row.get("batch_id", "")).strip(),
                "sampled": bool(row.get("sampled", False)),
                "sampling_strategy_id": str(row.get("sampling_strategy_id", "")).strip(),
                "sampling_details": _as_map(row.get("sampling_details")),
            }
            for row in rows
        ]
    )


def verify_qc_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    state = _state_payload(state_payload)
    observed = {
        "qc_result_hash_chain": _qc_result_hash(state),
        "sampling_decision_hash_chain": _sampling_decision_hash(state),
    }
    recorded = {
        "qc_result_hash_chain": str(state.get("qc_result_hash_chain", "")).strip().lower(),
        "sampling_decision_hash_chain": str(
            state.get("sampling_decision_hash_chain", "")
        ).strip().lower(),
    }
    violations = []
    for key in ("qc_result_hash_chain", "sampling_decision_hash_chain"):
        if recorded.get(key) and recorded.get(key) != observed.get(key):
            violations.append("recorded {} does not match replay hash".format(key))

    report = {
        "result": "complete" if not violations else "violation",
        "observed": observed,
        "recorded": recorded,
        "violations": violations,
    }
    if expected_payload:
        expected_state = _state_payload(expected_payload)
        expected = {
            "qc_result_hash_chain": _qc_result_hash(expected_state),
            "sampling_decision_hash_chain": _sampling_decision_hash(expected_state),
        }
        report["expected"] = expected
        for key in ("qc_result_hash_chain", "sampling_decision_hash_chain"):
            if expected.get(key) != observed.get(key):
                report["violations"].append(
                    "{} mismatch against expected replay baseline".format(key)
                )
        if report["violations"]:
            report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(
        dict(report, deterministic_fingerprint="")
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify deterministic replay hashes for PROC-3 QC windows."
    )
    parser.add_argument("--state-path", default="build/process/proc3_report.json")
    parser.add_argument("--expected-state-path", default="")
    args = parser.parse_args()

    state_path = os.path.normpath(os.path.abspath(str(args.state_path)))
    state_payload, state_err = _read_json(state_path)
    if state_err:
        print(
            json.dumps(
                {"result": "error", "reason": "state_read_failed", "details": state_err},
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    expected_payload = None
    expected_path = str(args.expected_state_path or "").strip()
    if expected_path:
        expected_abs = os.path.normpath(os.path.abspath(expected_path))
        expected_payload, expected_err = _read_json(expected_abs)
        if expected_err:
            print(
                json.dumps(
                    {
                        "result": "error",
                        "reason": "expected_state_read_failed",
                        "details": expected_err,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2

    report = verify_qc_replay_window(
        state_payload=state_payload, expected_payload=expected_payload
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
