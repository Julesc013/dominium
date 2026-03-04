#!/usr/bin/env python3
"""Verify PHYS energy replay windows reproduce deterministic hash chains."""

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


def _ledger_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("energy_ledger_entries")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    rows = (dict(payload.get("record") or {})).get("energy_ledger_entries")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _boundary_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("boundary_flux_events")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    rows = (dict(payload.get("record") or {})).get("boundary_flux_events")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _energy_hash_chains(payload: Mapping[str, object]) -> Dict[str, str]:
    ledger_rows = sorted(
        _ledger_rows(payload),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("transformation_id", "")),
            str(row.get("source_id", "")),
            str(row.get("entry_id", "")),
        ),
    )
    boundary_rows = sorted(
        _boundary_rows(payload),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("flux_id", "")),
        ),
    )
    ledger_chain = canonical_sha256(
        [
            {
                "entry_id": str(row.get("entry_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "transformation_id": str(row.get("transformation_id", "")).strip(),
                "source_id": str(row.get("source_id", "")).strip(),
                "energy_total_delta": int(_as_int(row.get("energy_total_delta", 0), 0)),
                "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            }
            for row in ledger_rows
        ]
    )
    boundary_chain = canonical_sha256(
        [
            {
                "flux_id": str(row.get("flux_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "quantity_id": str(row.get("quantity_id", "")).strip(),
                "value": int(_as_int(row.get("value", 0), 0)),
                "direction": str(row.get("direction", "in")).strip().lower(),
                "reason_code": str(row.get("reason_code", "")).strip(),
                "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            }
            for row in boundary_rows
        ]
    )
    return {
        "energy_ledger_hash_chain": str(ledger_chain),
        "boundary_flux_hash_chain": str(boundary_chain),
    }


def verify_replay_window(*, state_payload: Mapping[str, object], expected_payload: Mapping[str, object] | None = None) -> dict:
    observed = _energy_hash_chains(state_payload)
    expected_state = dict(expected_payload or {})
    report = {
        "result": "complete",
        "violations": [],
        "observed": dict(observed),
        "recorded": {
            "energy_ledger_hash_chain": str(state_payload.get("energy_ledger_hash_chain", "")).strip().lower(),
            "boundary_flux_hash_chain": str(state_payload.get("boundary_flux_hash_chain", "")).strip().lower(),
        },
        "deterministic_fingerprint": "",
    }

    recorded_ledger = str(report["recorded"]["energy_ledger_hash_chain"]).strip().lower()
    recorded_flux = str(report["recorded"]["boundary_flux_hash_chain"]).strip().lower()
    if recorded_ledger and recorded_ledger != str(observed["energy_ledger_hash_chain"]).strip().lower():
        report["violations"].append("recorded energy_ledger_hash_chain does not match replay window hash")
    if recorded_flux and recorded_flux != str(observed["boundary_flux_hash_chain"]).strip().lower():
        report["violations"].append("recorded boundary_flux_hash_chain does not match replay window hash")

    if expected_state:
        expected = _energy_hash_chains(expected_state)
        report["expected"] = dict(expected)
        if str(expected["energy_ledger_hash_chain"]).strip().lower() != str(observed["energy_ledger_hash_chain"]).strip().lower():
            report["violations"].append("energy_ledger_hash_chain mismatch against expected replay baseline")
        if str(expected["boundary_flux_hash_chain"]).strip().lower() != str(observed["boundary_flux_hash_chain"]).strip().lower():
            report["violations"].append("boundary_flux_hash_chain mismatch against expected replay baseline")

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify replay-window determinism for PHYS energy hashes.")
    parser.add_argument("--state-path", default="", help="JSON payload path containing energy_ledger_entries and boundary_flux_events.")
    parser.add_argument("--expected-state-path", default="", help="Optional second payload to compare replay hash equality.")
    args = parser.parse_args()

    state_path = str(args.state_path or "").strip()
    if not state_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.energy.state_path_required",
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
                    "reason_code": "refusal.energy.state_payload_invalid",
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
                        "reason_code": "refusal.energy.expected_payload_invalid",
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
