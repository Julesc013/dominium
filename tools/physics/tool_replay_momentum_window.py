#!/usr/bin/env python3
"""Verify PHYS momentum replay windows reproduce deterministic hash chains."""

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

from physics import normalize_impulse_application_rows, normalize_momentum_state_rows  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, Mapping):
        return {}, "json root must be an object"
    return dict(payload), ""


def _momentum_hash_chains(payload: Mapping[str, object]) -> dict:
    momentum_rows = normalize_momentum_state_rows(payload.get("momentum_states") or [])
    impulse_rows = normalize_impulse_application_rows(payload.get("impulse_application_rows") or [])
    return {
        "momentum_hash_chain": canonical_sha256([dict(row) for row in momentum_rows]),
        "impulse_event_hash_chain": canonical_sha256([dict(row) for row in impulse_rows]),
    }


def verify_replay_window(*, state_payload: Mapping[str, object], expected_payload: Mapping[str, object] | None = None) -> dict:
    observed = _momentum_hash_chains(state_payload)
    report = {
        "result": "complete",
        "violations": [],
        "observed": dict(observed),
        "recorded": {
            "momentum_hash_chain": str(state_payload.get("momentum_hash_chain", "")).strip().lower(),
            "impulse_event_hash_chain": str(state_payload.get("impulse_event_hash_chain", "")).strip().lower(),
        },
        "deterministic_fingerprint": "",
    }

    recorded_momentum = str(report["recorded"]["momentum_hash_chain"]).strip().lower()
    recorded_impulse = str(report["recorded"]["impulse_event_hash_chain"]).strip().lower()
    if recorded_momentum and recorded_momentum != str(observed["momentum_hash_chain"]).strip().lower():
        report["violations"].append("recorded momentum_hash_chain does not match replay window hash")
    if recorded_impulse and recorded_impulse != str(observed["impulse_event_hash_chain"]).strip().lower():
        report["violations"].append("recorded impulse_event_hash_chain does not match replay window hash")

    expected_state = dict(expected_payload or {})
    if expected_state:
        expected = _momentum_hash_chains(expected_state)
        report["expected"] = dict(expected)
        if str(expected["momentum_hash_chain"]).strip().lower() != str(observed["momentum_hash_chain"]).strip().lower():
            report["violations"].append("momentum_hash_chain mismatch against expected replay baseline")
        if str(expected["impulse_event_hash_chain"]).strip().lower() != str(observed["impulse_event_hash_chain"]).strip().lower():
            report["violations"].append("impulse_event_hash_chain mismatch against expected replay baseline")

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify replay-window determinism for PHYS momentum hashes.")
    parser.add_argument("--state-path", default="", help="JSON payload path containing momentum states/impulse rows.")
    parser.add_argument("--expected-state-path", default="", help="Optional second payload to compare replay hash equality.")
    args = parser.parse_args()

    state_path = str(args.state_path or "").strip()
    if not state_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.momentum.state_path_required",
                    "message": "provide --state-path",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    state_payload, state_error = _read_json(os.path.normpath(os.path.abspath(state_path)))
    if state_error:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.momentum.state_payload_invalid",
                    "message": state_error,
                    "state_path": os.path.normpath(os.path.abspath(state_path)),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    expected_payload = None
    expected_path = str(args.expected_state_path or "").strip()
    if expected_path:
        expected_payload, expected_error = _read_json(os.path.normpath(os.path.abspath(expected_path)))
        if expected_error:
            print(
                json.dumps(
                    {
                        "result": "refusal",
                        "reason_code": "refusal.momentum.expected_payload_invalid",
                        "message": expected_error,
                        "expected_state_path": os.path.normpath(os.path.abspath(expected_path)),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2

    report = verify_replay_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
