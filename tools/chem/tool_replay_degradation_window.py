#!/usr/bin/env python3
"""Verify CHEM-3 degradation replay windows reproduce deterministic hashes and threshold logic."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Mapping, Tuple


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


def _read_json(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, str(exc)
    if not isinstance(payload, Mapping):
        return {}, "json root must be an object"
    return dict(payload), ""


def _degradation_state_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("chem_degradation_state_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    rows = payload.get("degradation_state_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _degradation_event_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("chem_degradation_event_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    rows = payload.get("degradation_event_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _maintenance_action_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("chem_maintenance_action_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    rows = payload.get("maintenance_action_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _hash_chains(payload: Mapping[str, object]) -> Dict[str, str]:
    state_rows = sorted(
        _degradation_state_rows(payload),
        key=lambda row: (
            str(row.get("target_id", "")),
            str(row.get("degradation_kind_id", "")),
        ),
    )
    event_rows = sorted(
        _degradation_event_rows(payload),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("event_id", "")),
        ),
    )
    maintenance_rows = sorted(
        _maintenance_action_rows(payload),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("event_id", "")),
        ),
    )
    return {
        "degradation_hash_chain": canonical_sha256(
            [
                {
                    "target_id": str(row.get("target_id", "")).strip(),
                    "degradation_kind_id": str(row.get("degradation_kind_id", "")).strip(),
                    "level_value": int(max(0, _as_int(row.get("level_value", 0), 0))),
                    "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
                }
                for row in state_rows
            ]
        ),
        "degradation_event_hash_chain": canonical_sha256(
            [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "target_id": str(row.get("target_id", "")).strip(),
                    "degradation_kind_id": str(row.get("degradation_kind_id", "")).strip(),
                    "delta": int(max(0, _as_int(row.get("delta", 0), 0))),
                }
                for row in event_rows
            ]
        ),
        "maintenance_action_hash_chain": canonical_sha256(
            [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "target_id": str(row.get("target_id", "")).strip(),
                    "action_kind_id": str(row.get("action_kind_id", "")).strip(),
                    "degradation_kind_id": str(row.get("degradation_kind_id", "")).strip(),
                    "reduction_delta": int(max(0, _as_int(row.get("reduction_delta", 0), 0))),
                }
                for row in maintenance_rows
            ]
        ),
    }


def _state_violations(payload: Mapping[str, object]) -> List[str]:
    violations: List[str] = []
    for row in _degradation_state_rows(payload):
        target_id = str(row.get("target_id", "")).strip() or "target.unknown"
        kind_id = str(row.get("degradation_kind_id", "")).strip() or "kind.unknown"
        level = int(_as_int(row.get("level_value", 0), 0))
        if level < 0 or level > 1000:
            violations.append(
                "degradation level out of bounds for target='{}' kind='{}'".format(target_id, kind_id)
            )
    return violations


def _threshold_violations(payload: Mapping[str, object]) -> List[str]:
    violations: List[str] = []
    for row in _degradation_event_rows(payload):
        event_kind = str(row.get("event_kind_id", "")).strip()
        if event_kind != "event.chem.corrosion_leak_threshold":
            continue
        event_id = str(row.get("event_id", "")).strip() or "event.unknown"
        threshold_value = int(max(0, _as_int(row.get("threshold_value", 0), 0)))
        level_before = int(max(0, _as_int(row.get("level_before", 0), 0)))
        level_after = int(max(0, _as_int(row.get("level_after", 0), 0)))
        if threshold_value <= 0:
            violations.append("threshold event '{}' has non-positive threshold_value".format(event_id))
            continue
        if not (level_before < threshold_value <= level_after):
            violations.append(
                "threshold event '{}' does not reflect deterministic crossing".format(event_id)
            )
    return violations


def verify_degradation_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    observed = _hash_chains(state_payload)
    report = {
        "result": "complete",
        "violations": [],
        "observed": dict(observed),
        "recorded": {
            "degradation_hash_chain": str(state_payload.get("degradation_hash_chain", "")).strip().lower(),
            "degradation_event_hash_chain": str(state_payload.get("degradation_event_hash_chain", "")).strip().lower(),
            "maintenance_action_hash_chain": str(state_payload.get("maintenance_action_hash_chain", "")).strip().lower(),
        },
        "counts": {
            "degradation_state_rows": len(_degradation_state_rows(state_payload)),
            "degradation_event_rows": len(_degradation_event_rows(state_payload)),
            "maintenance_action_rows": len(_maintenance_action_rows(state_payload)),
        },
        "deterministic_fingerprint": "",
    }

    for key in ("degradation_hash_chain", "degradation_event_hash_chain", "maintenance_action_hash_chain"):
        recorded = str((dict(report.get("recorded") or {})).get(key, "")).strip().lower()
        if recorded and recorded != str(observed.get(key, "")).strip().lower():
            report["violations"].append("recorded {} does not match replay hash".format(key))

    report["violations"].extend(_state_violations(state_payload))
    report["violations"].extend(_threshold_violations(state_payload))

    if expected_payload:
        expected = _hash_chains(dict(expected_payload))
        report["expected"] = dict(expected)
        for key in ("degradation_hash_chain", "degradation_event_hash_chain", "maintenance_action_hash_chain"):
            if str(expected.get(key, "")).strip().lower() != str(observed.get(key, "")).strip().lower():
                report["violations"].append("{} mismatch against expected replay baseline".format(key))

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify replay-window determinism for CHEM-3 degradation hashes.")
    parser.add_argument("--state-path", default="", help="JSON payload path containing degradation rows and hash chains.")
    parser.add_argument("--expected-state-path", default="", help="Optional second payload for replay hash equality checks.")
    args = parser.parse_args()

    state_path = str(args.state_path or "").strip()
    if not state_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.chem.degradation.state_path_required",
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
                    "reason_code": "refusal.chem.degradation.state_payload_invalid",
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
                        "reason_code": "refusal.chem.degradation.expected_payload_invalid",
                        "message": expected_error,
                        "expected_state_path": os.path.normpath(os.path.abspath(expected_path)),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2

    report = verify_degradation_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
