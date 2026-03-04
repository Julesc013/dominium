#!/usr/bin/env python3
"""Verify CHEM stress energy conservation via ledger rows and residual tolerances."""

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

from tools.physics.tool_verify_energy_conservation import verify_energy_conservation  # noqa: E402
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


def _energy_tolerance_abs(*, repo_root: str, override: int = 0) -> int:
    if int(override) > 0:
        return int(max(0, _as_int(override, 0)))
    registry_rel = "data/registries/quantity_tolerance_registry.json"
    registry_abs = os.path.join(repo_root, registry_rel.replace("/", os.sep))
    payload, err = _read_json(registry_abs)
    if err:
        return 1
    rows = list((dict(payload.get("record") or {})).get("quantity_tolerances") or [])
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        if str(row.get("quantity_id", "")).strip() != "quantity.energy_total":
            continue
        return int(max(0, _as_int(row.get("tolerance_abs", 1), 1)))
    return 1


def verify_chem_energy(*, report_payload: dict, transformation_registry: dict, tolerance_abs: int) -> dict:
    extensions = dict(report_payload.get("extensions") or {})
    metrics = dict(report_payload.get("metrics") or {})
    ledger_rows = [dict(row) for row in list(extensions.get("energy_ledger_rows") or []) if isinstance(row, Mapping)]
    boundary_rows = [dict(row) for row in list(extensions.get("boundary_flux_event_rows") or []) if isinstance(row, Mapping)]

    ledger_result = verify_energy_conservation(
        registry_payload=dict(transformation_registry or {}),
        ledger_payload={
            "energy_ledger_entries": list(ledger_rows),
            "boundary_flux_events": list(boundary_rows),
        },
        tolerance=int(max(0, _as_int(tolerance_abs, 0))),
    )
    per_tick_residual = [int(_as_int(value, 0)) for value in list(metrics.get("per_tick_energy_residual") or [])]
    residual_violations: List[dict] = []
    for tick, residual in enumerate(per_tick_residual):
        if abs(int(residual)) <= int(tolerance_abs):
            continue
        residual_violations.append(
            {
                "code": "tick_energy_residual_exceeded",
                "tick": int(tick),
                "residual": int(residual),
                "tolerance_abs": int(tolerance_abs),
            }
        )

    combined_violation_count = int(_as_int(ledger_result.get("violation_count", 0), 0) + len(residual_violations))
    report = {
        "schema_version": "1.0.0",
        "result": "complete"
        if (str(ledger_result.get("result", "")).strip() == "complete" and not residual_violations)
        else "violation",
        "scenario_id": str(report_payload.get("scenario_id", "")).strip(),
        "tolerance_abs": int(tolerance_abs),
        "violation_count": int(combined_violation_count),
        "violations": list(ledger_result.get("violations") or []) + list(residual_violations),
        "summary": {
            "ledger_entry_count": int(_as_int(ledger_result.get("ledger_entry_count", 0), 0)),
            "boundary_flux_count": int(_as_int(ledger_result.get("boundary_flux_count", 0), 0)),
            "energy_residual_hash": canonical_sha256(list(per_tick_residual)),
            "ledger_deterministic_fingerprint": str(ledger_result.get("deterministic_fingerprint", "")).strip(),
            "energy_residual_stats": dict(metrics.get("energy_residual_stats") or {}),
        },
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify CHEM stress energy conservation and ledger consistency.")
    parser.add_argument("--report-path", default="", help="Path to CHEM stress report JSON.")
    parser.add_argument(
        "--registry-path",
        default=os.path.join("data", "registries", "energy_transformation_registry.json"),
        help="Path to energy transformation registry JSON.",
    )
    parser.add_argument("--tolerance-abs", type=int, default=0)
    args = parser.parse_args()

    report_path = str(args.report_path or "").strip()
    if not report_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.chem.energy.report_required",
                    "message": "provide --report-path for CHEM energy verification",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    if not os.path.isabs(report_path):
        report_path = os.path.normpath(os.path.join(REPO_ROOT_HINT, report_path))
    report_path = os.path.normpath(os.path.abspath(report_path))

    registry_path = str(args.registry_path or "").strip()
    if not os.path.isabs(registry_path):
        registry_path = os.path.normpath(os.path.join(REPO_ROOT_HINT, registry_path))
    registry_path = os.path.normpath(os.path.abspath(registry_path))

    report_payload, report_err = _read_json(report_path)
    if report_err:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.chem.energy.invalid_report",
                    "message": "invalid report payload: {}".format(report_err),
                    "report_path": report_path,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    registry_payload, registry_err = _read_json(registry_path)
    if registry_err:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.chem.energy.invalid_registry",
                    "message": "invalid energy transformation registry: {}".format(registry_err),
                    "registry_path": registry_path,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    tolerance_abs = _energy_tolerance_abs(repo_root=REPO_ROOT_HINT, override=int(args.tolerance_abs))
    result = verify_chem_energy(
        report_payload=report_payload,
        transformation_registry=registry_payload,
        tolerance_abs=int(tolerance_abs),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
