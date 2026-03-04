#!/usr/bin/env python3
"""Verify PHYS-4 entropy monotonicity and reset semantics from deterministic state payloads."""

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
    if not isinstance(payload, dict):
        return {}, "json root must be an object"
    return payload, ""


def _event_rows(payload: dict) -> List[dict]:
    rows = payload.get("entropy_event_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    rows = (dict(payload.get("record") or {})).get("entropy_event_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    return []


def _reset_rows(payload: dict) -> List[dict]:
    rows = payload.get("entropy_reset_events")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    rows = (dict(payload.get("record") or {})).get("entropy_reset_events")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    return []


def _state_rows(payload: dict) -> List[dict]:
    rows = payload.get("entropy_state_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    rows = (dict(payload.get("record") or {})).get("entropy_state_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    return []


def verify_entropy_monotonicity(*, payload: dict) -> dict:
    event_rows = sorted(
        _event_rows(payload),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("target_id", "")),
            "event",
            str(row.get("event_id", "")),
        ),
    )
    reset_rows = sorted(
        _reset_rows(payload),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("target_id", "")),
            "reset",
            str(row.get("event_id", "")),
        ),
    )
    timeline = sorted(
        [("event", dict(row)) for row in event_rows] + [("reset", dict(row)) for row in reset_rows],
        key=lambda item: (
            int(max(0, _as_int(item[1].get("tick", 0), 0))),
            str(item[1].get("target_id", "")),
            str(item[0]),
            str(item[1].get("event_id", "")),
        ),
    )

    violations: List[dict] = []
    by_target_current: Dict[str, int] = {}
    for row_kind, row in timeline:
        target_id = str(row.get("target_id", "")).strip()
        if not target_id:
            continue
        current_value = int(max(0, _as_int(by_target_current.get(target_id, 0), 0)))
        if row_kind == "event":
            delta = int(max(0, _as_int(row.get("entropy_delta", 0), 0)))
            after = int(max(0, _as_int(row.get("entropy_value_after", current_value + delta), current_value + delta)))
            if after < current_value:
                violations.append(
                    {
                        "code": "event_decreased_entropy",
                        "target_id": target_id,
                        "event_id": str(row.get("event_id", "")).strip(),
                        "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                        "before": int(current_value),
                        "after": int(after),
                    }
                )
            if after < int(current_value + delta):
                violations.append(
                    {
                        "code": "event_after_less_than_before_plus_delta",
                        "target_id": target_id,
                        "event_id": str(row.get("event_id", "")).strip(),
                        "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                        "before": int(current_value),
                        "delta": int(delta),
                        "after": int(after),
                    }
                )
            by_target_current[target_id] = int(after)
            continue

        before = int(max(0, _as_int(row.get("entropy_before", current_value), current_value)))
        after = int(max(0, _as_int(row.get("entropy_after", current_value), current_value)))
        if after > before:
            violations.append(
                {
                    "code": "reset_increased_entropy",
                    "target_id": target_id,
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "before": int(before),
                    "after": int(after),
                }
            )
        by_target_current[target_id] = int(after)

    state_rows = sorted(
        _state_rows(payload),
        key=lambda row: str(row.get("target_id", "")),
    )
    for row in state_rows:
        target_id = str(row.get("target_id", "")).strip()
        if not target_id:
            continue
        expected = int(max(0, _as_int(by_target_current.get(target_id, 0), 0)))
        actual = int(max(0, _as_int(row.get("entropy_value", 0), 0)))
        if actual != expected:
            violations.append(
                {
                    "code": "state_value_mismatch",
                    "target_id": target_id,
                    "expected": int(expected),
                    "actual": int(actual),
                    "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
                }
            )

    report = {
        "result": "complete" if not violations else "violation",
        "entropy_event_count": int(len(event_rows)),
        "entropy_reset_event_count": int(len(reset_rows)),
        "entropy_target_count": int(len(state_rows)),
        "violation_count": int(len(violations)),
        "violations": list(violations),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify PHYS-4 entropy monotonicity and reset semantics.")
    parser.add_argument(
        "--state-path",
        default="",
        help="Path to JSON payload with entropy_state_rows, entropy_event_rows, and entropy_reset_events.",
    )
    args = parser.parse_args()

    state_path = str(args.state_path or "").strip()
    if not state_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.entropy.state_path_required",
                    "message": "provide --state-path to verify PHYS-4 entropy monotonicity",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    if not os.path.isabs(state_path):
        state_path = os.path.normpath(os.path.join(REPO_ROOT_HINT, state_path))
    state_path = os.path.normpath(os.path.abspath(state_path))

    payload, err = _read_json(state_path)
    if err:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.entropy.invalid_payload",
                    "message": "invalid entropy state payload: {}".format(err),
                    "state_path": state_path,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    report = verify_entropy_monotonicity(payload=payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
