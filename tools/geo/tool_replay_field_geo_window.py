#!/usr/bin/env python3
"""Verify GEO-4 field replay windows preserve GEO-keyed field hash surfaces."""

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

from tools.physics.tool_replay_field_window import verify_field_replay_window  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, Mapping):
        return {}, "json root must be an object"
    return dict(payload), ""


def verify_geo_field_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    report = verify_field_replay_window(state_payload=state_payload, expected_payload=expected_payload)
    report = dict(report)
    report["geo_recorded"] = {
        "field_binding_registry_hash": str(state_payload.get("field_binding_registry_hash", "")).strip().lower(),
        "interpolation_policy_registry_hash": str(state_payload.get("interpolation_policy_registry_hash", "")).strip().lower(),
    }
    report["geo_observed"] = {
        "field_binding_registry_hash": canonical_sha256(dict(state_payload.get("field_binding_registry") or {}))
        if isinstance(state_payload.get("field_binding_registry"), Mapping)
        else str(state_payload.get("field_binding_registry_hash", "")).strip().lower(),
        "interpolation_policy_registry_hash": canonical_sha256(dict(state_payload.get("interpolation_policy_registry") or {}))
        if isinstance(state_payload.get("interpolation_policy_registry"), Mapping)
        else str(state_payload.get("interpolation_policy_registry_hash", "")).strip().lower(),
    }
    violations = list(report.get("violations") or [])
    for key in ("field_binding_registry_hash", "interpolation_policy_registry_hash"):
        recorded = str((dict(report.get("geo_recorded") or {})).get(key, "")).strip().lower()
        observed = str((dict(report.get("geo_observed") or {})).get(key, "")).strip().lower()
        if recorded and observed and recorded != observed:
            violations.append("recorded {} does not match GEO replay hash".format(key))
    report["violations"] = violations
    report["result"] = "violation" if violations else "complete"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify GEO-keyed field replay determinism.")
    parser.add_argument("--state-path", default="", help="JSON payload path containing field state/events.")
    parser.add_argument("--expected-state-path", default="", help="Optional second payload for replay equality checks.")
    args = parser.parse_args()

    state_path = str(args.state_path or "").strip()
    if not state_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.field.state_path_required",
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
                    "reason_code": "refusal.field.state_payload_invalid",
                    "message": state_error,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    expected_payload = None
    expected_state_path = str(args.expected_state_path or "").strip()
    if expected_state_path:
        expected_payload, expected_error = _read_json(os.path.normpath(os.path.abspath(expected_state_path)))
        if expected_error:
            print(
                json.dumps(
                    {
                        "result": "refusal",
                        "reason_code": "refusal.field.expected_payload_invalid",
                        "message": expected_error,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2

    report = verify_geo_field_replay_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
