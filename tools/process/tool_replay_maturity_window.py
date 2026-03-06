#!/usr/bin/env python3
"""Verify deterministic replay hashes for PROC-4 maturity outcomes."""

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


def _metrics_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("process_metrics_state_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            str(item.get("process_id", "")),
            str(item.get("version", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "runs_count": int(max(0, _as_int(row.get("runs_count", 0), 0))),
                "yield_mean": int(max(0, _as_int(row.get("yield_mean", 0), 0))),
                "yield_variance": int(max(0, _as_int(row.get("yield_variance", 0), 0))),
                "defect_rate": int(max(0, _as_int(row.get("defect_rate", 0), 0))),
                "qc_pass_rate": int(max(0, _as_int(row.get("qc_pass_rate", 0), 0))),
                "env_deviation_score": int(
                    max(0, _as_int(row.get("env_deviation_score", 0), 0))
                ),
                "calibration_deviation_score": int(
                    max(0, _as_int(row.get("calibration_deviation_score", 0), 0))
                ),
                "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
            }
            for row in rows
        ]
    )


def _maturity_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("process_maturity_record_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            str(item.get("process_id", "")),
            str(item.get("version", "")),
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("record_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "record_id": str(row.get("record_id", "")).strip(),
                "process_id": str(row.get("process_id", "")).strip(),
                "version": str(row.get("version", "")).strip(),
                "maturity_state": str(row.get("maturity_state", "")).strip(),
                "stabilization_score": int(
                    max(0, _as_int(row.get("stabilization_score", 0), 0))
                ),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            }
            for row in rows
        ]
    )


def _process_cert_hash(state: Mapping[str, object]) -> str:
    cert_rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("process_certification_artifact_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("issued_tick", 0), 0))),
            str(item.get("cert_id", "")),
        ),
    )
    revocation_rows = sorted(
        (
            dict(item)
            for item in _as_list(state.get("process_certification_revocation_rows"))
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("event_id", "")),
        ),
    )
    return canonical_sha256(
        {
            "certificates": [
                {
                    "cert_id": str(row.get("cert_id", "")).strip(),
                    "process_id": str(row.get("process_id", "")).strip(),
                    "version": str(row.get("version", "")).strip(),
                    "cert_type_id": str(row.get("cert_type_id", "")).strip(),
                    "issued_tick": int(max(0, _as_int(row.get("issued_tick", 0), 0))),
                    "valid_until_tick": (
                        None
                        if row.get("valid_until_tick") is None
                        else int(max(0, _as_int(row.get("valid_until_tick", 0), 0)))
                    ),
                }
                for row in cert_rows
            ],
            "revocations": [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "cert_id": str(row.get("cert_id", "")).strip(),
                    "process_id": str(row.get("process_id", "")).strip(),
                    "version": str(row.get("version", "")).strip(),
                    "reason_code": str(row.get("reason_code", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                }
                for row in revocation_rows
            ],
        }
    )


def verify_maturity_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    state = _state_payload(state_payload)
    observed = {
        "metrics_state_hash_chain": _metrics_hash(state),
        "process_maturity_hash_chain": _maturity_hash(state),
        "process_cert_hash_chain": _process_cert_hash(state),
    }
    recorded = {
        "metrics_state_hash_chain": str(state.get("metrics_state_hash_chain", "")).strip().lower(),
        "process_maturity_hash_chain": str(
            state.get("process_maturity_hash_chain", "")
        ).strip().lower(),
        "process_cert_hash_chain": str(state.get("process_cert_hash_chain", "")).strip().lower(),
    }
    violations = []
    for key in (
        "metrics_state_hash_chain",
        "process_maturity_hash_chain",
        "process_cert_hash_chain",
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
            "metrics_state_hash_chain": _metrics_hash(expected_state),
            "process_maturity_hash_chain": _maturity_hash(expected_state),
            "process_cert_hash_chain": _process_cert_hash(expected_state),
        }
        report["expected"] = expected
        for key in (
            "metrics_state_hash_chain",
            "process_maturity_hash_chain",
            "process_cert_hash_chain",
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
        description="Verify deterministic replay hashes for PROC-4 maturity windows."
    )
    parser.add_argument("--state-path", default="build/process/proc4_report.json")
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

    report = verify_maturity_replay_window(
        state_payload=state_payload, expected_payload=expected_payload
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
