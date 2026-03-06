#!/usr/bin/env python3
"""Verify deterministic replay hashes for PROC-5 process capsule windows."""

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


def _capsule_generation_hash(state: Mapping[str, object]) -> str:
    generated_rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("capsule_generated_record_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("event_id", "")),
        ),
    )
    if generated_rows:
        payload = [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "capsule_id": str(row.get("capsule_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            }
            for row in generated_rows
        ]
        return canonical_sha256(payload)

    capsule_rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("process_capsule_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: str(item.get("capsule_id", "")),
    )
    return canonical_sha256(
        [
            {
                "capsule_id": str(row.get("capsule_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "validity_domain_ref": str(row.get("validity_domain_ref", "")).strip(),
                "compiled_model_id": (
                    None
                    if row.get("compiled_model_id") is None
                    else str(row.get("compiled_model_id", "")).strip() or None
                ),
            }
            for row in capsule_rows
        ]
    )


def _capsule_execution_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("capsule_execution_record_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: str(item.get("exec_id", "")),
    )
    return canonical_sha256(
        [
            {
                "exec_id": str(row.get("exec_id", "")).strip(),
                "capsule_id": str(row.get("capsule_id", "")).strip(),
                "tick_range": _as_map(row.get("tick_range")),
                "inputs_hash": str(row.get("inputs_hash", "")).strip(),
                "outputs_hash": str(row.get("outputs_hash", "")).strip(),
                "qc_outcome_hash": (
                    None
                    if row.get("qc_outcome_hash") is None
                    else str(row.get("qc_outcome_hash", "")).strip() or None
                ),
            }
            for row in rows
        ]
    )


def _compiled_model_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("compiled_model_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: str(item.get("compiled_model_id", "")),
    )
    return canonical_sha256(
        [
            {
                "compiled_model_id": str(row.get("compiled_model_id", "")).strip(),
                "source_hash": str(row.get("source_hash", "")).strip(),
                "compiled_type_id": str(row.get("compiled_type_id", "")).strip(),
                "equivalence_proof_ref": str(row.get("equivalence_proof_ref", "")).strip(),
                "validity_domain_ref": str(row.get("validity_domain_ref", "")).strip(),
            }
            for row in rows
        ]
    )


def verify_capsule_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    state = _state_payload(state_payload)
    observed = {
        "capsule_generation_hash_chain": _capsule_generation_hash(state),
        "capsule_execution_hash_chain": _capsule_execution_hash(state),
        "compiled_model_hash_chain": _compiled_model_hash(state),
    }
    recorded = {
        "capsule_generation_hash_chain": str(
            state.get(
                "capsule_generation_hash_chain",
                state.get("process_capsule_generation_hash_chain", ""),
            )
        )
        .strip()
        .lower(),
        "capsule_execution_hash_chain": str(
            state.get(
                "capsule_execution_hash_chain",
                state.get("process_capsule_execution_hash_chain", ""),
            )
        )
        .strip()
        .lower(),
        "compiled_model_hash_chain": str(state.get("compiled_model_hash_chain", "")).strip().lower(),
    }
    violations = []
    for key in (
        "capsule_generation_hash_chain",
        "capsule_execution_hash_chain",
        "compiled_model_hash_chain",
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
            "capsule_generation_hash_chain": _capsule_generation_hash(expected_state),
            "capsule_execution_hash_chain": _capsule_execution_hash(expected_state),
            "compiled_model_hash_chain": _compiled_model_hash(expected_state),
        }
        report["expected"] = expected
        for key in (
            "capsule_generation_hash_chain",
            "capsule_execution_hash_chain",
            "compiled_model_hash_chain",
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
        description="Verify deterministic replay hashes for PROC-5 capsule windows."
    )
    parser.add_argument("--state-path", default="build/process/proc5_report.json")
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

    report = verify_capsule_replay_window(
        state_payload=state_payload, expected_payload=expected_payload
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
