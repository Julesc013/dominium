#!/usr/bin/env python3
"""Verify CHEM stress entropy monotonicity (except explicit reset events)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List, Mapping, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.physics.tool_verify_entropy_monotonicity import verify_entropy_monotonicity  # noqa: E402
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


def verify_chem_entropy(*, report_payload: dict) -> dict:
    metrics = dict(report_payload.get("metrics") or {})
    extensions = dict(report_payload.get("extensions") or {})
    per_tick_increment = [int(_as_int(value, 0)) for value in list(metrics.get("per_tick_entropy_increment") or [])]
    reset_rows = [dict(row) for row in list(extensions.get("entropy_reset_event_rows") or []) if isinstance(row, Mapping)]
    event_rows = [dict(row) for row in list(extensions.get("entropy_event_rows") or []) if isinstance(row, Mapping)]
    state_rows = [dict(row) for row in list(extensions.get("entropy_state_rows") or []) if isinstance(row, Mapping)]

    violations: List[dict] = []
    cumulative: List[int] = []
    running = 0
    for tick, delta in enumerate(per_tick_increment):
        if delta < 0:
            reset_for_tick = any(int(max(0, _as_int(row.get("tick", 0), 0))) == int(tick) for row in reset_rows)
            if not reset_for_tick:
                violations.append(
                    {
                        "code": "entropy_negative_increment_without_reset",
                        "tick": int(tick),
                        "delta": int(delta),
                    }
                )
        running += int(delta)
        cumulative.append(int(running))
    monotonic_ok = all(cumulative[idx] >= cumulative[idx - 1] for idx in range(1, len(cumulative)))
    if not monotonic_ok:
        violations.append(
            {
                "code": "entropy_cumulative_not_monotonic",
                "message": "cumulative entropy increments decreased without explicit reset accounting",
            }
        )

    entropy_by_equipment = dict(extensions.get("entropy_by_equipment") or {})
    observed_total = int(sum(int(max(0, _as_int(value, 0))) for value in entropy_by_equipment.values()))
    expected_total = int(sum(per_tick_increment))
    if event_rows or state_rows:
        physics_result = verify_entropy_monotonicity(
            payload={
                "entropy_event_rows": list(event_rows),
                "entropy_reset_events": list(reset_rows),
                "entropy_state_rows": list(state_rows),
            }
        )
        if str(physics_result.get("result", "")).strip() != "complete":
            violations.extend(list(physics_result.get("violations") or []))
    elif observed_total != expected_total:
        violations.append(
            {
                "code": "entropy_total_mismatch",
                "observed_total": int(observed_total),
                "expected_total": int(expected_total),
            }
        )

    report = {
        "schema_version": "1.0.0",
        "result": "complete" if not violations else "violation",
        "scenario_id": str(report_payload.get("scenario_id", "")).strip(),
        "tick_count": int(len(per_tick_increment)),
        "entropy_increment_total": int(expected_total),
        "entropy_reset_event_count": int(len(reset_rows)),
        "violation_count": int(len(violations)),
        "violations": list(violations),
        "summary": {
            "per_tick_entropy_increment_hash": canonical_sha256(list(per_tick_increment)),
            "entropy_by_equipment_hash": canonical_sha256(dict((str(key), int(max(0, _as_int(entropy_by_equipment[key], 0)))) for key in sorted(entropy_by_equipment.keys()))),
        },
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify CHEM stress entropy monotonicity rules.")
    parser.add_argument("--report-path", default="", help="Path to CHEM stress report JSON.")
    args = parser.parse_args()

    report_path = str(args.report_path or "").strip()
    if not report_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.chem.entropy.report_required",
                    "message": "provide --report-path for CHEM entropy verification",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    if not os.path.isabs(report_path):
        report_path = os.path.normpath(os.path.join(REPO_ROOT_HINT, report_path))
    report_path = os.path.normpath(os.path.abspath(report_path))

    report_payload, err = _read_json(report_path)
    if err:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.chem.entropy.invalid_report",
                    "message": "invalid report payload: {}".format(err),
                    "report_path": report_path,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    result = verify_chem_entropy(report_payload=report_payload)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
