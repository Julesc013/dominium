#!/usr/bin/env python3
"""Verify SYS-6 reliability replay hashes across deterministic state windows."""

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
    if final_state:
        return final_state
    return dict(payload)


def _system_health_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in list(state.get("system_health_state_rows") or [])
            if isinstance(item, Mapping)
        ),
        key=lambda item: str(item.get("system_id", "")),
    )
    return canonical_sha256(
        [
            {
                "system_id": str(row.get("system_id", "")).strip(),
                "aggregated_hazard_levels": dict(
                    (
                        str(key).strip(),
                        int(max(0, _as_int(value, 0))),
                    )
                    for key, value in sorted(
                        (dict(row.get("aggregated_hazard_levels") or {})).items(),
                        key=lambda item: str(item[0]),
                    )
                    if str(key).strip()
                ),
                "entropy_value": (
                    None
                    if row.get("entropy_value") is None
                    else int(max(0, _as_int(row.get("entropy_value", 0), 0)))
                ),
                "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
            }
            for row in rows
        ]
    )


def _failure_event_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in list(state.get("system_failure_event_rows") or [])
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("system_id", "")),
            str(item.get("failure_mode_id", "")),
            str(item.get("event_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "system_id": str(row.get("system_id", "")).strip(),
                "failure_mode_id": str(row.get("failure_mode_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            }
            for row in rows
        ]
    )


def _forced_expand_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in list(state.get("system_forced_expand_event_rows") or [])
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("capsule_id", "")),
            str(item.get("event_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "capsule_id": str(row.get("capsule_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "reason_code": str(row.get("reason_code", "")).strip(),
                "requested_fidelity": str(row.get("requested_fidelity", "")).strip(),
            }
            for row in rows
        ]
    )


def _stochastic_rng_hash(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in list(state.get("system_reliability_rng_outcome_rows") or [])
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("system_id", "")),
            str(item.get("failure_mode_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "system_id": str(row.get("system_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "reliability_profile_id": str(row.get("reliability_profile_id", "")).strip(),
                "failure_mode_id": str(row.get("failure_mode_id", "")).strip(),
                "rng_stream_name": str(row.get("rng_stream_name", "")).strip(),
                "roll_permille": int(max(0, min(1000, _as_int(row.get("roll_permille", 0), 0)))),
                "threshold_permille": int(max(0, min(1000, _as_int(row.get("threshold_permille", 0), 0)))),
                "hit": bool(row.get("hit", False)),
            }
            for row in rows
        ]
    )


def _observed_hashes(state: Mapping[str, object]) -> dict:
    return {
        "system_health_hash_chain": _system_health_hash(state),
        "system_failure_event_hash_chain": _failure_event_hash(state),
        "system_forced_expand_event_hash_chain": _forced_expand_hash(state),
        "system_reliability_rng_hash_chain": _stochastic_rng_hash(state),
    }


def verify_system_failure_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    state = _state_payload(state_payload)
    observed = _observed_hashes(state)
    report = {
        "result": "complete",
        "violations": [],
        "observed": dict(observed),
        "recorded": {
            "system_health_hash_chain": str(state.get("system_health_hash_chain", "")).strip().lower(),
            "system_failure_event_hash_chain": str(
                state.get("system_failure_event_hash_chain", state.get("failure_event_hash_chain", ""))
            )
            .strip()
            .lower(),
            "system_forced_expand_event_hash_chain": str(
                state.get("system_forced_expand_event_hash_chain", state.get("forced_expand_event_hash_chain", ""))
            )
            .strip()
            .lower(),
            "system_reliability_rng_hash_chain": str(state.get("system_reliability_rng_hash_chain", ""))
            .strip()
            .lower(),
        },
        "deterministic_fingerprint": "",
    }
    for key in (
        "system_health_hash_chain",
        "system_failure_event_hash_chain",
        "system_forced_expand_event_hash_chain",
        "system_reliability_rng_hash_chain",
    ):
        recorded = str(report["recorded"][key]).strip().lower()
        observed_value = str(observed[key]).strip().lower()
        if recorded and (recorded != observed_value):
            report["violations"].append("recorded {} does not match replay hash".format(key))

    if expected_payload:
        expected_state = _state_payload(expected_payload)
        expected = _observed_hashes(expected_state)
        report["expected"] = dict(expected)
        for key in (
            "system_health_hash_chain",
            "system_failure_event_hash_chain",
            "system_forced_expand_event_hash_chain",
            "system_reliability_rng_hash_chain",
        ):
            if str(expected[key]).strip().lower() != str(observed[key]).strip().lower():
                report["violations"].append("{} mismatch against expected replay baseline".format(key))

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify deterministic replay hashes for SYS-6 reliability failure windows."
    )
    parser.add_argument("--state-path", default="build/system/sys6_reliability_report.json")
    parser.add_argument("--expected-state-path", default="")
    args = parser.parse_args()

    state_path = os.path.normpath(os.path.abspath(str(args.state_path)))
    state_payload, state_err = _read_json(state_path)
    if state_err:
        print(
            json.dumps(
                {
                    "result": "error",
                    "reason": "state_read_failed",
                    "state_path": state_path,
                    "details": state_err,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    expected_payload = None
    expected_path = str(args.expected_state_path or "").strip()
    if expected_path:
        expected_abs = os.path.normpath(os.path.abspath(expected_path))
        loaded_expected, expected_err = _read_json(expected_abs)
        if expected_err:
            print(
                json.dumps(
                    {
                        "result": "error",
                        "reason": "expected_state_read_failed",
                        "expected_state_path": expected_abs,
                        "details": expected_err,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2
        expected_payload = loaded_expected

    report = verify_system_failure_replay_window(
        state_payload=state_payload,
        expected_payload=expected_payload,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if str(report.get("result", "")).strip() != "complete":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

