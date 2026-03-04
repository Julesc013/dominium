#!/usr/bin/env python3
"""Verify CHEM stress mass conservation residuals against declared tolerance."""

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


def _mass_tolerance_abs(*, repo_root: str, override: int = 0) -> int:
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
        if str(row.get("quantity_id", "")).strip() != "quantity.mass":
            continue
        return int(max(0, _as_int(row.get("tolerance_abs", 1), 1)))
    return 1


def verify_mass_conservation(*, report_payload: dict, tolerance_abs: int) -> dict:
    threshold = int(max(0, _as_int(tolerance_abs, 0)))
    metrics = dict(report_payload.get("metrics") or {})
    extensions = dict(report_payload.get("extensions") or {})
    reaction_rows = [dict(row) for row in list(extensions.get("reaction_event_rows") or []) if isinstance(row, Mapping)]
    per_tick_residual = [int(_as_int(value, 0)) for value in list(metrics.get("per_tick_mass_residual") or [])]

    violations: List[dict] = []
    for row in reaction_rows:
        residual = int(_as_int(row.get("mass_residual", 0), 0))
        if abs(residual) <= threshold:
            continue
        violations.append(
            {
                "code": "reaction_mass_residual_exceeded",
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "run_id": str(row.get("run_id", "")).strip(),
                "reaction_id": str(row.get("reaction_id", "")).strip(),
                "event_id": str(row.get("event_id", "")).strip(),
                "residual": int(residual),
                "tolerance_abs": int(threshold),
            }
        )

    for tick, residual in enumerate(per_tick_residual):
        if abs(int(residual)) <= threshold:
            continue
        violations.append(
            {
                "code": "tick_mass_residual_exceeded",
                "tick": int(tick),
                "residual": int(residual),
                "tolerance_abs": int(threshold),
            }
        )

    stats = dict(metrics.get("mass_residual_stats") or {})
    stats_max_abs = int(max(0, _as_int(stats.get("max_abs", 0), 0)))
    if stats_max_abs > threshold:
        violations.append(
            {
                "code": "mass_residual_stats_exceeded",
                "max_abs": int(stats_max_abs),
                "tolerance_abs": int(threshold),
            }
        )

    report = {
        "schema_version": "1.0.0",
        "result": "complete" if not violations else "violation",
        "scenario_id": str(report_payload.get("scenario_id", "")).strip(),
        "tolerance_abs": int(threshold),
        "reaction_row_count": int(len(reaction_rows)),
        "tick_count": int(len(per_tick_residual)),
        "violation_count": int(len(violations)),
        "violations": list(violations),
        "summary": {
            "mass_residual_stats": dict(stats),
            "mass_residual_hash": canonical_sha256(list(per_tick_residual)),
        },
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify CHEM stress mass conservation residuals.")
    parser.add_argument("--report-path", default="", help="Path to CHEM stress report JSON.")
    parser.add_argument("--tolerance-abs", type=int, default=0)
    args = parser.parse_args()

    report_path = str(args.report_path or "").strip()
    if not report_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.chem.mass.report_required",
                    "message": "provide --report-path for CHEM mass verification",
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
                    "reason_code": "refusal.chem.mass.invalid_report",
                    "message": "invalid report payload: {}".format(err),
                    "report_path": report_path,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    tolerance_abs = _mass_tolerance_abs(repo_root=REPO_ROOT_HINT, override=int(args.tolerance_abs))
    result = verify_mass_conservation(report_payload=report_payload, tolerance_abs=int(tolerance_abs))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
