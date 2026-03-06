#!/usr/bin/env python3
"""Verify deterministic replay hashes for PROC-6 drift/revalidation outcomes."""

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


def _drift_state_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("process_drift_state_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (str(item.get("process_id", "")), str(item.get("version", ""))),
    )
    return canonical_sha256(
        [
            {
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "drift_score": int(max(0, min(1000, _as_int(row.get("drift_score", 0), 0)))),
                "drift_band": str(row.get("drift_band", "")).strip(),
                "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
            }
            for row in rows
        ]
    )


def _drift_event_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("drift_event_record_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("event_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "drift_band": str(row.get("drift_band", "")).strip(),
                "drift_score": int(max(0, min(1000, _as_int(row.get("drift_score", 0), 0)))),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "action_taken": str(row.get("action_taken", "")).strip(),
            }
            for row in rows
        ]
    )


def _qc_policy_change_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("qc_policy_change_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("event_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "from_qc_policy_id": str(row.get("from_qc_policy_id", "")).strip(),
                "to_qc_policy_id": str(row.get("to_qc_policy_id", "")).strip(),
                "reason_code": str(row.get("reason_code", "")).strip(),
            }
            for row in rows
        ]
    )


def _revalidation_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("revalidation_run_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            str(item.get("process_id", "")),
            str(item.get("version", "")),
            int(max(1, _as_int(item.get("trial_index", 1), 1))),
            str(item.get("revalidation_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "revalidation_id": str(row.get("revalidation_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "trial_index": int(max(1, _as_int(row.get("trial_index", 1), 1))),
                "scheduled_tick": int(max(0, _as_int(row.get("scheduled_tick", 0), 0))),
                "status": str(row.get("status", "")).strip(),
            }
            for row in rows
        ]
    )


def verify_drift_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    state = _state_payload(state_payload)
    observed = {
        "drift_state_hash_chain": _drift_state_hash(state),
        "drift_event_hash_chain": _drift_event_hash(state),
        "qc_policy_change_hash_chain": _qc_policy_change_hash(state),
        "revalidation_run_hash_chain": _revalidation_hash(state),
    }
    recorded = {
        "drift_state_hash_chain": str(state.get("drift_state_hash_chain", "")).strip().lower(),
        "drift_event_hash_chain": str(state.get("drift_event_hash_chain", "")).strip().lower(),
        "qc_policy_change_hash_chain": str(
            state.get("qc_policy_change_hash_chain", "")
        ).strip().lower(),
        "revalidation_run_hash_chain": str(
            state.get("revalidation_run_hash_chain", "")
        ).strip().lower(),
    }
    violations = []
    for key in (
        "drift_state_hash_chain",
        "drift_event_hash_chain",
        "qc_policy_change_hash_chain",
        "revalidation_run_hash_chain",
    ):
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
            "drift_state_hash_chain": _drift_state_hash(expected_state),
            "drift_event_hash_chain": _drift_event_hash(expected_state),
            "qc_policy_change_hash_chain": _qc_policy_change_hash(expected_state),
            "revalidation_run_hash_chain": _revalidation_hash(expected_state),
        }
        report["expected"] = expected
        for key in (
            "drift_state_hash_chain",
            "drift_event_hash_chain",
            "qc_policy_change_hash_chain",
            "revalidation_run_hash_chain",
        ):
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
        description="Verify deterministic replay hashes for PROC-6 drift windows."
    )
    parser.add_argument("--state-path", default="build/process/proc6_report.json")
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

    report = verify_drift_replay_window(
        state_payload=state_payload, expected_payload=expected_payload
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
