#!/usr/bin/env python3
"""Verify PHYS-3 energy ledger entries against registered transformation conservation rules."""

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


def _is_energy_quantity(quantity_id: str) -> bool:
    token = str(quantity_id or "").strip()
    return token.startswith("quantity.energy_") or token in {
        "quantity.energy_total",
        "quantity.mass_energy_total",
        "quantity.heat_loss",
    }


def _quantity_map(value: object) -> Dict[str, int]:
    if not isinstance(value, Mapping):
        return {}
    out: Dict[str, int] = {}
    for key, raw in sorted(value.items(), key=lambda item: str(item[0])):
        token = str(key or "").strip()
        if not token.startswith("quantity."):
            continue
        out[token] = int(_as_int(raw, 0))
    return out


def _energy_sum(values: Mapping[str, object]) -> int:
    return int(
        sum(int(_as_int(raw, 0)) for key, raw in sorted(values.items(), key=lambda item: str(item[0])) if _is_energy_quantity(str(key)))
    )


def _transformation_rows_by_id(payload: dict) -> Dict[str, dict]:
    rows = list(payload.get("energy_transformations") or [])
    if not rows:
        rows = list((dict(payload.get("record") or {})).get("energy_transformations") or [])
    out: Dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        token = str(row.get("transformation_id", "")).strip()
        if not token:
            continue
        out[token] = dict(row)
    return out


def _ledger_rows(payload: dict) -> List[dict]:
    rows = payload.get("energy_ledger_entries")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    rows = payload.get("entries")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    rows = (dict(payload.get("record") or {})).get("energy_ledger_entries")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    return []


def _boundary_rows(payload: dict) -> List[dict]:
    rows = payload.get("boundary_flux_events")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    rows = (dict(payload.get("record") or {})).get("boundary_flux_events")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    return []


def verify_energy_conservation(
    *,
    registry_payload: dict,
    ledger_payload: dict,
    tolerance: int = 0,
) -> dict:
    rows_by_id = _transformation_rows_by_id(registry_payload)
    ledger_rows = sorted(
        _ledger_rows(ledger_payload),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("transformation_id", "")),
            str(row.get("source_id", "")),
            str(row.get("entry_id", "")),
        ),
    )
    boundary_rows = sorted(
        _boundary_rows(ledger_payload),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("flux_id", "")),
        ),
    )

    threshold = int(max(0, _as_int(tolerance, 0)))
    violations = []
    per_source_delta: Dict[str, int] = {}
    per_tick_delta: Dict[int, int] = {}
    for row in ledger_rows:
        entry_id = str(row.get("entry_id", "")).strip()
        source_id = str(row.get("source_id", "")).strip()
        tick = int(max(0, _as_int(row.get("tick", 0), 0)))
        transformation_id = str(row.get("transformation_id", "")).strip()
        transform_row = dict(rows_by_id.get(transformation_id) or {})
        if not transform_row:
            violations.append(
                {
                    "code": "unregistered_transform",
                    "entry_id": entry_id,
                    "tick": tick,
                    "source_id": source_id,
                    "transformation_id": transformation_id,
                }
            )
            continue

        input_values = _quantity_map(row.get("input_values"))
        output_values = _quantity_map(row.get("output_values"))
        input_total = int(_energy_sum(input_values))
        output_total = int(_energy_sum(output_values))
        expected_delta = int(output_total - input_total)
        entry_delta = int(_as_int(row.get("energy_total_delta", 0), 0))
        if abs(int(entry_delta - expected_delta)) > threshold:
            violations.append(
                {
                    "code": "entry_delta_mismatch",
                    "entry_id": entry_id,
                    "tick": tick,
                    "source_id": source_id,
                    "transformation_id": transformation_id,
                    "entry_delta": int(entry_delta),
                    "expected_delta": int(expected_delta),
                }
            )
        if (not bool(transform_row.get("boundary_allowed", False))) and abs(int(input_total - output_total)) > threshold:
            violations.append(
                {
                    "code": "conservation_mismatch",
                    "entry_id": entry_id,
                    "tick": tick,
                    "source_id": source_id,
                    "transformation_id": transformation_id,
                    "input_total": int(input_total),
                    "output_total": int(output_total),
                }
            )
        per_source_delta[source_id] = int(_as_int(per_source_delta.get(source_id, 0), 0) + entry_delta)
        per_tick_delta[tick] = int(_as_int(per_tick_delta.get(tick, 0), 0) + entry_delta)

    flux_signed_total = int(
        sum(
            _as_int(row.get("value", 0), 0)
            if str(row.get("direction", "in")).strip().lower() == "in"
            else -_as_int(row.get("value", 0), 0)
            for row in boundary_rows
        )
    )
    report = {
        "result": "complete" if not violations else "violation",
        "ledger_entry_count": int(len(ledger_rows)),
        "boundary_flux_count": int(len(boundary_rows)),
        "violation_count": int(len(violations)),
        "violations": list(violations),
        "summary": {
            "ledger_energy_total_delta_sum": int(sum(_as_int(row.get("energy_total_delta", 0), 0) for row in ledger_rows)),
            "boundary_flux_signed_total": int(flux_signed_total),
            "source_deltas": dict((key, int(per_source_delta[key])) for key in sorted(per_source_delta.keys())),
            "tick_deltas": dict((str(key), int(per_tick_delta[key])) for key in sorted(per_tick_delta.keys())),
        },
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify PHYS-3 energy conservation from ledger entry payloads.")
    parser.add_argument(
        "--ledger-path",
        default="",
        help="Path to JSON payload with `energy_ledger_entries` and optional `boundary_flux_events`.",
    )
    parser.add_argument(
        "--registry-path",
        default=os.path.join("data", "registries", "energy_transformation_registry.json"),
        help="Path to energy transformation registry JSON.",
    )
    parser.add_argument("--tolerance", type=int, default=0)
    args = parser.parse_args()

    repo_root = REPO_ROOT_HINT
    registry_path = (
        os.path.normpath(os.path.abspath(str(args.registry_path)))
        if str(args.registry_path).strip()
        else os.path.join(repo_root, "data", "registries", "energy_transformation_registry.json")
    )
    if not os.path.isabs(registry_path):
        registry_path = os.path.normpath(os.path.join(repo_root, registry_path))

    ledger_path = str(args.ledger_path or "").strip()
    if not ledger_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.energy.ledger_path_required",
                    "message": "provide --ledger-path to verify PHYS-3 conservation entries",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    ledger_path = os.path.normpath(os.path.abspath(ledger_path))

    registry_payload, registry_error = _read_json(registry_path)
    if registry_error:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.energy.registry_invalid",
                    "message": "invalid registry payload: {}".format(registry_error),
                    "registry_path": registry_path,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    ledger_payload, ledger_error = _read_json(ledger_path)
    if ledger_error:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.energy.ledger_invalid",
                    "message": "invalid ledger payload: {}".format(ledger_error),
                    "ledger_path": ledger_path,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    report = verify_energy_conservation(
        registry_payload=registry_payload,
        ledger_payload=ledger_payload,
        tolerance=int(max(0, _as_int(args.tolerance, 0))),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
