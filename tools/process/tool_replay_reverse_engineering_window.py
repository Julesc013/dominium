#!/usr/bin/env python3
"""Verify deterministic replay hashes for PROC-7 reverse-engineering windows."""

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


def _reverse_record_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("reverse_engineering_record_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("record_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "record_id": str(row.get("record_id", "")).strip(),
                "subject_id": str(row.get("subject_id", "")).strip(),
                "target_item_id": str(row.get("target_item_id", "")).strip(),
                "method": str(row.get("method", "")).strip(),
                "destroyed": bool(row.get("destroyed", False)),
                "produced_artifact_ids": _sorted_tokens(
                    list(row.get("produced_artifact_ids") or [])
                ),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            }
            for row in rows
        ]
    )


def _candidate_promotion_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("candidate_promotion_record_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("record_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "record_id": str(row.get("record_id", "")).strip(),
                "candidate_id": str(row.get("candidate_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "status": str(row.get("status", "")).strip(),
            }
            for row in rows
        ]
    )


def verify_reverse_engineering_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    state = _state_payload(state_payload)
    observed = {
        "reverse_engineering_record_hash_chain": _reverse_record_hash(state),
        "candidate_process_hash_chain": _candidate_process_hash(state),
        "candidate_model_binding_hash_chain": _candidate_binding_hash(state),
        "candidate_promotion_hash_chain": _candidate_promotion_hash(state),
    }
    recorded = {
        "reverse_engineering_record_hash_chain": str(
            state.get("reverse_engineering_record_hash_chain", "")
        ).strip().lower(),
        "candidate_process_hash_chain": str(
            state.get("candidate_process_hash_chain", "")
        ).strip().lower(),
        "candidate_model_binding_hash_chain": str(
            state.get("candidate_model_binding_hash_chain", "")
        ).strip().lower(),
        "candidate_promotion_hash_chain": str(
            state.get("candidate_promotion_hash_chain", "")
        ).strip().lower(),
    }
    violations = []
    for key in (
        "reverse_engineering_record_hash_chain",
        "candidate_process_hash_chain",
        "candidate_model_binding_hash_chain",
        "candidate_promotion_hash_chain",
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
            "reverse_engineering_record_hash_chain": _reverse_record_hash(expected_state),
            "candidate_process_hash_chain": _candidate_process_hash(expected_state),
            "candidate_model_binding_hash_chain": _candidate_binding_hash(
                expected_state
            ),
            "candidate_promotion_hash_chain": _candidate_promotion_hash(expected_state),
        }
        report["expected"] = expected
        for key in (
            "reverse_engineering_record_hash_chain",
            "candidate_process_hash_chain",
            "candidate_model_binding_hash_chain",
            "candidate_promotion_hash_chain",
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
        description="Verify deterministic replay hashes for PROC-7 reverse-engineering windows."
    )
    parser.add_argument("--state-path", default="build/process/proc7_reverse_report.json")
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

    report = verify_reverse_engineering_replay_window(
        state_payload=state_payload,
        expected_payload=expected_payload,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
