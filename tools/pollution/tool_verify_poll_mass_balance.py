#!/usr/bin/env python3
"""Verify POLL-3 mass accounting against declared proxy bounds."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, Mapping, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from pollution.dispersion_engine import concentration_field_id_for_pollutant  # noqa: E402
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


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and (not os.path.isdir(parent)):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _state_payload(payload: Mapping[str, object]) -> dict:
    report_extensions = _as_map(payload.get("extensions"))
    final_state = _as_map(report_extensions.get("final_state_snapshot"))
    if final_state:
        return final_state
    return dict(payload)


def verify_poll_mass_balance(
    *,
    state_payload: Mapping[str, object],
    proxy_error_permille: int,
) -> dict:
    state = _state_payload(state_payload)
    proxy_permille = int(max(0, _as_int(proxy_error_permille, 500)))

    source_rows = [dict(row) for row in list(state.get("pollution_source_event_rows") or []) if isinstance(row, Mapping)]
    field_rows = [dict(row) for row in list(state.get("field_cells") or []) if isinstance(row, Mapping)]
    deposition_rows = [dict(row) for row in list(state.get("pollution_deposition_rows") or []) if isinstance(row, Mapping)]
    dispersion_rows = [dict(row) for row in list(state.get("pollution_dispersion_step_rows") or []) if isinstance(row, Mapping)]

    pollutant_ids = sorted(
        set(
            [str(row.get("pollutant_id", "")).strip() for row in source_rows if str(row.get("pollutant_id", "")).strip()]
            + [str(row.get("pollutant_id", "")).strip() for row in deposition_rows if str(row.get("pollutant_id", "")).strip()]
            + [str(row.get("pollutant_id", "")).strip() for row in dispersion_rows if str(row.get("pollutant_id", "")).strip()]
            + [
                "pollutant.{}".format(str(row.get("field_id", "")).strip()[len("field.pollution.") : -len("_concentration")])
                for row in field_rows
                if str(row.get("field_id", "")).strip().startswith("field.pollution.")
                and str(row.get("field_id", "")).strip().endswith("_concentration")
            ]
        )
    )

    rows = []
    for pollutant_id in pollutant_ids:
        field_id = concentration_field_id_for_pollutant(pollutant_id)
        emitted_total = int(
            sum(
                int(max(0, _as_int(row.get("emitted_mass", 0), 0)))
                for row in source_rows
                if str(row.get("pollutant_id", "")).strip() == pollutant_id
            )
        )
        field_proxy_total = int(
            sum(
                int(max(0, _as_int(row.get("value", 0), 0)))
                for row in field_rows
                if str(row.get("field_id", "")).strip() == field_id
            )
        )
        deposited_total = int(
            sum(
                int(max(0, _as_int(row.get("deposited_mass", 0), 0)))
                for row in deposition_rows
                if str(row.get("pollutant_id", "")).strip() == pollutant_id
            )
        )
        decayed_total = int(
            sum(
                int(max(0, _as_int(row.get("decay_mass", 0), 0)))
                for row in dispersion_rows
                if str(row.get("pollutant_id", "")).strip() == pollutant_id
            )
        )
        accounted_total = int(field_proxy_total + deposited_total + decayed_total)
        residual = int(emitted_total - accounted_total)
        residual_abs = int(abs(residual))
        allowed_residual_abs = int(max(5, (emitted_total * proxy_permille) // 1000))
        rows.append(
            {
                "pollutant_id": pollutant_id,
                "emitted_mass_total": int(emitted_total),
                "field_mass_proxy_total": int(field_proxy_total),
                "deposited_total": int(deposited_total),
                "decayed_total": int(decayed_total),
                "accounted_total": int(accounted_total),
                "residual": int(residual),
                "residual_abs": int(residual_abs),
                "allowed_residual_abs": int(allowed_residual_abs),
                "within_declared_bounds": bool(residual_abs <= allowed_residual_abs),
                "concentration_proxy_mode": True,
            }
        )

    violations = [
        row for row in rows if not bool(row.get("within_declared_bounds", False))
    ]
    report = {
        "schema_version": "1.0.0",
        "result": "complete" if not violations else "violation",
        "proxy_error_permille": int(proxy_permille),
        "rows": [dict(row) for row in sorted(rows, key=lambda row: str(row.get("pollutant_id", "")))],
        "summary": {
            "pollutant_count": int(len(rows)),
            "violation_count": int(len(violations)),
            "max_residual_abs": int(max([int(row.get("residual_abs", 0)) for row in rows] or [0])),
            "max_allowed_residual_abs": int(max([int(row.get("allowed_residual_abs", 0)) for row in rows] or [0])),
        },
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify POLL-3 mass accounting within declared proxy bounds.")
    parser.add_argument("--state-path", default="build/pollution/poll3_stress_report.json")
    parser.add_argument("--proxy-error-permille", type=int, default=500)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    state_path = os.path.normpath(os.path.abspath(str(args.state_path)))
    payload, err = _read_json(state_path)
    if err:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.poll.mass_balance.state_payload_invalid",
                    "message": err,
                    "state_path": state_path,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    report = verify_poll_mass_balance(
        state_payload=payload,
        proxy_error_permille=int(args.proxy_error_permille),
    )
    output = str(args.output or "").strip()
    if output:
        output_abs = os.path.normpath(os.path.abspath(output))
        _write_json(output_abs, report)
        report = dict(report)
        report["output_path"] = output_abs
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
