#!/usr/bin/env python3
"""Verify deterministic process quality replay hashes over a state payload window."""

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


def _tokens(values: object) -> list[str]:
    return sorted(set(str(item).strip() for item in _as_list(values) if str(item).strip()))


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


def _process_quality_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("process_quality_record_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (str(item.get("run_id", "")), str(item.get("deterministic_fingerprint", ""))),
    )
    return canonical_sha256(
        [
            {
                "run_id": str(row.get("run_id", "")).strip(),
                "yield_factor": int(max(0, min(1000, _as_int(row.get("yield_factor", 0), 0)))),
                "defect_flags": _tokens(row.get("defect_flags")),
                "quality_grade": str(row.get("quality_grade", "")).strip(),
            }
            for row in rows
        ]
    )


def _batch_quality_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("batch_quality_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: str(item.get("batch_id", "")),
    )
    return canonical_sha256(
        [
            {
                "batch_id": str(row.get("batch_id", "")).strip(),
                "quality_grade": str(row.get("quality_grade", "")).strip(),
                "defect_flags": _tokens(row.get("defect_flags")),
                "contamination_tags": _tokens(row.get("contamination_tags")),
                "yield_factor": int(max(0, min(1000, _as_int(row.get("yield_factor", 0), 0)))),
                "traceability_run_id": str(_as_map(_as_map(row.get("extensions")).get("traceability")).get("run_id", "")).strip(),
            }
            for row in rows
        ]
    )


def verify_quality_replay_window(*, state_payload: Mapping[str, object], expected_payload: Mapping[str, object] | None = None) -> dict:
    state = _state_payload(state_payload)
    observed = {
        "process_quality_hash_chain": _process_quality_hash(state),
        "batch_quality_hash_chain": _batch_quality_hash(state),
    }
    recorded = {
        "process_quality_hash_chain": str(state.get("process_quality_hash_chain", "")).strip().lower(),
        "batch_quality_hash_chain": str(state.get("batch_quality_hash_chain", "")).strip().lower(),
    }
    violations = []
    for key in ("process_quality_hash_chain", "batch_quality_hash_chain"):
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
            "process_quality_hash_chain": _process_quality_hash(expected_state),
            "batch_quality_hash_chain": _batch_quality_hash(expected_state),
        }
        report["expected"] = expected
        for key in ("process_quality_hash_chain", "batch_quality_hash_chain"):
            if expected.get(key) != observed.get(key):
                report["violations"].append("{} mismatch against expected replay baseline".format(key))
        if report["violations"]:
            report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify deterministic replay hashes for PROC-2 quality windows.")
    parser.add_argument("--state-path", default="build/process/proc2_report.json")
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

    report = verify_quality_replay_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
