#!/usr/bin/env python3
"""Verify CHEM-1 combustion replay windows reproduce deterministic hashes and balances."""

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


def _combustion_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("combustion_event_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _emission_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("combustion_emission_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    rows = payload.get("chem_emission_pool_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _impulse_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("combustion_impulse_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _ledger_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("energy_ledger_entries")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _hash_chains(payload: Mapping[str, object]) -> Dict[str, str]:
    combustion_rows = sorted(
        _combustion_rows(payload),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("event_id", "")),
        ),
    )
    emission_rows = sorted(
        _emission_rows(payload),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("event_id", "")),
        ),
    )
    impulse_rows = sorted(
        _impulse_rows(payload),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("event_id", "")),
        ),
    )
    return {
        "combustion_hash_chain": canonical_sha256(
            [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "target_id": str(row.get("target_id", "")).strip(),
                    "reaction_id": str(row.get("reaction_id", "")).strip(),
                    "chemical_energy_in": int(max(0, _as_int(row.get("chemical_energy_in", 0), 0))),
                    "thermal_energy_out": int(max(0, _as_int(row.get("thermal_energy_out", 0), 0))),
                    "efficiency_permille": int(max(0, _as_int(row.get("efficiency_permille", 0), 0))),
                }
                for row in combustion_rows
            ]
        ),
        "emission_hash_chain": canonical_sha256(
            [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "target_id": str(row.get("target_id", "")).strip(),
                    "material_id": str(row.get("material_id", "")).strip(),
                    "mass_value": int(max(0, _as_int(row.get("mass_value", 0), 0))),
                }
                for row in emission_rows
            ]
        ),
        "impulse_hash_chain": canonical_sha256(
            [
                {
                    "event_id": str(row.get("event_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "target_id": str(row.get("target_id", "")).strip(),
                    "target_assembly_id": str(row.get("target_assembly_id", "")).strip(),
                    "impulse_magnitude": int(max(0, _as_int(row.get("impulse_magnitude", 0), 0))),
                }
                for row in impulse_rows
            ]
        ),
    }


def _mass_conservation_violations(payload: Mapping[str, object]) -> List[str]:
    violations: List[str] = []
    for row in _combustion_rows(payload):
        event_id = str(row.get("event_id", "")).strip() or "event.unknown"
        fuel_consumed = int(max(0, _as_int(row.get("fuel_consumed", 0), 0)))
        oxidizer_consumed = int(max(0, _as_int(row.get("oxidizer_consumed", 0), 0)))
        pollutant_emission = int(max(0, _as_int(row.get("pollutant_emission", 0), 0)))
        if pollutant_emission > int(fuel_consumed + oxidizer_consumed):
            violations.append(
                "pollutant emission exceeds consumed mass for event_id='{}'".format(event_id)
            )
    return violations


def _energy_ledger_violations(payload: Mapping[str, object]) -> List[str]:
    violations: List[str] = []
    ledger_rows = _ledger_rows(payload)
    transform_ids = set(
        str(row.get("transformation_id", "")).strip()
        for row in ledger_rows
        if str(row.get("transformation_id", "")).strip()
    )
    if "transform.chemical_to_thermal" not in transform_ids:
        violations.append("missing transform.chemical_to_thermal ledger entry")
    for row in _combustion_rows(payload):
        event_id = str(row.get("event_id", "")).strip() or "event.unknown"
        chemical_energy_in = int(max(0, _as_int(row.get("chemical_energy_in", 0), 0)))
        thermal_energy_out = int(max(0, _as_int(row.get("thermal_energy_out", 0), 0)))
        electrical_energy_out = int(max(0, _as_int(row.get("electrical_energy_out", 0), 0)))
        irreversibility_loss = int(max(0, _as_int(row.get("irreversibility_loss", 0), 0)))
        if chemical_energy_in != int(thermal_energy_out + electrical_energy_out + irreversibility_loss):
            violations.append(
                "energy split mismatch for event_id='{}'".format(event_id)
            )
    return violations


def _efficiency_determinism_violations(payload: Mapping[str, object]) -> List[str]:
    violations: List[str] = []
    by_key: Dict[Tuple[str, int, int, int], set] = {}
    for row in _combustion_rows(payload):
        target_id = str(row.get("target_id", "")).strip()
        temperature_value = int(_as_int((dict(row.get("extensions") or {})).get("temperature_value", -1), -1))
        entropy_value = int(_as_int((dict(row.get("extensions") or {})).get("entropy_value", -1), -1))
        mixture_ratio_permille = int(_as_int((dict(row.get("extensions") or {})).get("mixture_ratio_permille", -1), -1))
        efficiency_permille = int(max(0, _as_int(row.get("efficiency_permille", 0), 0)))
        key = (target_id, temperature_value, entropy_value, mixture_ratio_permille)
        by_key.setdefault(key, set()).add(efficiency_permille)
    for key in sorted(by_key.keys()):
        values = sorted(by_key[key])
        if len(values) > 1:
            violations.append(
                "efficiency drift for target='{}' profile_tuple={} values={}".format(
                    key[0],
                    [key[1], key[2], key[3]],
                    values,
                )
            )
    return violations


def verify_combustion_window(
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
            "combustion_hash_chain": str(state_payload.get("combustion_hash_chain", "")).strip().lower(),
            "emission_hash_chain": str(state_payload.get("emission_hash_chain", "")).strip().lower(),
            "impulse_hash_chain": str(state_payload.get("impulse_hash_chain", "")).strip().lower(),
        },
        "counts": {
            "combustion_event_rows": len(_combustion_rows(state_payload)),
            "combustion_emission_rows": len(_emission_rows(state_payload)),
            "combustion_impulse_rows": len(_impulse_rows(state_payload)),
            "energy_ledger_entries": len(_ledger_rows(state_payload)),
        },
        "deterministic_fingerprint": "",
    }

    for key in ("combustion_hash_chain", "emission_hash_chain", "impulse_hash_chain"):
        recorded = str((dict(report.get("recorded") or {})).get(key, "")).strip().lower()
        if recorded and recorded != str(observed.get(key, "")).strip().lower():
            report["violations"].append("recorded {} does not match replay hash".format(key))

    report["violations"].extend(_mass_conservation_violations(state_payload))
    report["violations"].extend(_energy_ledger_violations(state_payload))
    report["violations"].extend(_efficiency_determinism_violations(state_payload))

    if expected_payload:
        expected = _hash_chains(dict(expected_payload))
        report["expected"] = dict(expected)
        for key in ("combustion_hash_chain", "emission_hash_chain", "impulse_hash_chain"):
            if str(expected.get(key, "")).strip().lower() != str(observed.get(key, "")).strip().lower():
                report["violations"].append("{} mismatch against expected replay baseline".format(key))

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify replay-window determinism for CHEM-1 combustion hashes.")
    parser.add_argument("--state-path", default="", help="JSON payload path containing combustion rows and energy ledger entries.")
    parser.add_argument("--expected-state-path", default="", help="Optional second payload for replay hash equality checks.")
    args = parser.parse_args()

    state_path = str(args.state_path or "").strip()
    if not state_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.chem.combustion.state_path_required",
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
                    "reason_code": "refusal.chem.combustion.state_payload_invalid",
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
                        "reason_code": "refusal.chem.combustion.expected_payload_invalid",
                        "message": expected_error,
                        "expected_state_path": os.path.normpath(os.path.abspath(expected_path)),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2

    report = verify_combustion_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
