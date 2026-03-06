#!/usr/bin/env python3
"""Verify deterministic replay hashes for PROC-7 experiment/result windows."""

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


def _sorted_tokens(values: list[object]) -> list[str]:
    return sorted(
        {
            str(item).strip()
            for item in list(values or [])
            if str(item).strip()
        }
    )


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


def _experiment_result_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("experiment_result_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: str(item.get("result_id", "")),
    )
    return canonical_sha256(
        [
            {
                "result_id": str(row.get("result_id", "")).strip(),
                "experiment_id": str(row.get("experiment_id", "")).strip(),
                "run_id": str(row.get("run_id", "")).strip(),
                "measured_values": (
                    dict(row.get("measured_values") or {})
                    if isinstance(row.get("measured_values"), Mapping)
                    else {}
                ),
                "confidence_bounds": (
                    dict(row.get("confidence_bounds") or {})
                    if isinstance(row.get("confidence_bounds"), Mapping)
                    else {}
                ),
            }
            for row in rows
        ]
    )


def _experiment_binding_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("experiment_run_binding_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: str(item.get("run_id", "")),
    )
    return canonical_sha256(
        [
            {
                "experiment_id": str(row.get("experiment_id", "")).strip(),
                "run_id": str(row.get("run_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "status": str(row.get("status", "")).strip(),
                "start_tick": int(max(0, _as_int(row.get("start_tick", 0), 0))),
                "end_tick": (
                    None
                    if row.get("end_tick") is None
                    else int(max(0, _as_int(row.get("end_tick", 0), 0)))
                ),
            }
            for row in rows
        ]
    )


def _candidate_process_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("candidate_process_definition_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: str(item.get("candidate_id", "")),
    )
    return canonical_sha256(
        [
            {
                "candidate_id": str(row.get("candidate_id", "")).strip(),
                "proposed_process_definition_ref": str(
                    row.get("proposed_process_definition_ref", "")
                ).strip(),
                "confidence_score": int(
                    max(0, min(1000, _as_int(row.get("confidence_score", 0), 0)))
                ),
                "inferred_from_artifact_ids": _sorted_tokens(
                    list(row.get("inferred_from_artifact_ids") or [])
                ),
            }
            for row in rows
        ]
    )


def _candidate_binding_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("candidate_model_binding_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: str(item.get("candidate_binding_id", "")),
    )
    return canonical_sha256(
        [
            {
                "candidate_binding_id": str(
                    row.get("candidate_binding_id", "")
                ).strip(),
                "candidate_id": str(row.get("candidate_id", "")).strip(),
                "model_id": (
                    None
                    if row.get("model_id") is None
                    else str(row.get("model_id", "")).strip() or None
                ),
                "confidence_score": int(
                    max(0, min(1000, _as_int(row.get("confidence_score", 0), 0)))
                ),
            }
            for row in rows
        ]
    )


def verify_experiment_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    state = _state_payload(state_payload)
    observed = {
        "experiment_result_hash_chain": _experiment_result_hash(state),
        "experiment_run_binding_hash_chain": _experiment_binding_hash(state),
        "candidate_process_hash_chain": _candidate_process_hash(state),
        "candidate_model_binding_hash_chain": _candidate_binding_hash(state),
    }
    recorded = {
        "experiment_result_hash_chain": str(
            state.get("experiment_result_hash_chain", "")
        ).strip().lower(),
        "experiment_run_binding_hash_chain": str(
            state.get("experiment_run_binding_hash_chain", "")
        ).strip().lower(),
        "candidate_process_hash_chain": str(
            state.get("candidate_process_hash_chain", "")
        ).strip().lower(),
        "candidate_model_binding_hash_chain": str(
            state.get("candidate_model_binding_hash_chain", "")
        ).strip().lower(),
    }
    violations = []
    for key in (
        "experiment_result_hash_chain",
        "experiment_run_binding_hash_chain",
        "candidate_process_hash_chain",
        "candidate_model_binding_hash_chain",
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
            "experiment_result_hash_chain": _experiment_result_hash(expected_state),
            "experiment_run_binding_hash_chain": _experiment_binding_hash(
                expected_state
            ),
            "candidate_process_hash_chain": _candidate_process_hash(expected_state),
            "candidate_model_binding_hash_chain": _candidate_binding_hash(
                expected_state
            ),
        }
        report["expected"] = expected
        for key in (
            "experiment_result_hash_chain",
            "experiment_run_binding_hash_chain",
            "candidate_process_hash_chain",
            "candidate_model_binding_hash_chain",
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
        description="Verify deterministic replay hashes for PROC-7 experiment windows."
    )
    parser.add_argument("--state-path", default="build/process/proc7_experiment_report.json")
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

    report = verify_experiment_replay_window(
        state_payload=state_payload,
        expected_payload=expected_payload,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
