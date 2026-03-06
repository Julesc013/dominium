#!/usr/bin/env python3
"""Verify deterministic process-run replay hashes over a state payload window."""

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


def _process_run_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in list(state.get("process_run_record_rows") or [])
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            str(item.get("run_id", "")),
            int(max(0, _as_int(item.get("start_tick", 0), 0))),
            int(max(0, _as_int(item.get("end_tick", 0), 0))),
        ),
    )
    return canonical_sha256(
        [
            {
                "run_id": str(row.get("run_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "start_tick": int(max(0, _as_int(row.get("start_tick", 0), 0))),
                "end_tick": (
                    None
                    if row.get("end_tick") is None
                    else int(max(0, _as_int(row.get("end_tick", 0), 0)))
                ),
                "status": str(row.get("status", "")).strip(),
            }
            for row in rows
        ]
    )


def _process_step_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in list(state.get("process_step_record_rows") or [])
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            str(item.get("run_id", "")),
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("step_id", "")),
            str(item.get("status", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "run_id": str(row.get("run_id", "")).strip(),
                "step_id": str(row.get("step_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "status": str(row.get("status", "")).strip(),
            }
            for row in rows
        ]
    )


def verify_process_replay_window(*, state_payload: Mapping[str, object], expected_payload: Mapping[str, object] | None = None) -> dict:
    state = _state_payload(state_payload)
    observed = {
        "process_run_record_hash_chain": _process_run_hash(state),
        "process_step_record_hash_chain": _process_step_hash(state),
    }
    recorded = {
        "process_run_record_hash_chain": str(
            state.get("process_run_record_hash_chain", state.get("process_run_hash_chain", ""))
        ).strip().lower(),
        "process_step_record_hash_chain": str(
            state.get("process_step_record_hash_chain", "")
        ).strip().lower(),
    }
    violations = []
    for key in ("process_run_record_hash_chain", "process_step_record_hash_chain"):
        if recorded.get(key) and recorded.get(key) != observed.get(key):
            violations.append("recorded {} does not match replay hash".format(key))

    report = {
        "result": "complete" if not violations else "violation",
        "observed": observed,
        "recorded": recorded,
        "violations": violations,
    }
    if expected_payload:
        expected = {
            "process_run_record_hash_chain": _process_run_hash(_state_payload(expected_payload)),
            "process_step_record_hash_chain": _process_step_hash(_state_payload(expected_payload)),
        }
        report["expected"] = expected
        for key in ("process_run_record_hash_chain", "process_step_record_hash_chain"):
            if expected[key] != observed[key]:
                report["violations"].append("{} mismatch against expected replay baseline".format(key))
        if report["violations"]:
            report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify deterministic replay hashes for PROC process-run windows.")
    parser.add_argument("--state-path", default="build/process/proc1_report.json")
    parser.add_argument("--expected-state-path", default="")
    args = parser.parse_args()

    state_path = os.path.normpath(os.path.abspath(str(args.state_path)))
    state_payload, state_err = _read_json(state_path)
    if state_err:
        print(json.dumps({"result": "error", "reason": "state_read_failed", "details": state_err}, indent=2, sort_keys=True))
        return 2

    expected_payload = None
    expected_path = str(args.expected_state_path or "").strip()
    if expected_path:
        expected_abs = os.path.normpath(os.path.abspath(expected_path))
        expected_payload, expected_err = _read_json(expected_abs)
        if expected_err:
            print(json.dumps({"result": "error", "reason": "expected_state_read_failed", "details": expected_err}, indent=2, sort_keys=True))
            return 2

    report = verify_process_replay_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
