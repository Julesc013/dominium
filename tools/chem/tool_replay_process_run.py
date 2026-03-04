#!/usr/bin/env python3
"""Verify CHEM-2 process-run replay windows for deterministic mass/energy/yield outcomes."""

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


def _run_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("chem_process_run_state_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    rows = payload.get("process_run_state_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _quality_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("batch_quality_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _yield_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("chem_yield_model_rows")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _batch_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("material_batches")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _ledger_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("energy_ledger_entries")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def _hash_chains(payload: Mapping[str, object]) -> Dict[str, str]:
    run_rows = sorted(
        _run_rows(payload),
        key=lambda row: str(row.get("run_id", "")),
    )
    quality_rows = sorted(
        _quality_rows(payload),
        key=lambda row: str(row.get("batch_id", "")),
    )
    yield_rows = sorted(
        _yield_rows(payload),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("run_id", "")),
            str(row.get("yield_model_id", "")),
        ),
    )
    return {
        "process_run_hash_chain": canonical_sha256(
            [
                {
                    "run_id": str(row.get("run_id", "")).strip(),
                    "reaction_id": str(row.get("reaction_id", "")).strip(),
                    "equipment_id": str(row.get("equipment_id", "")).strip(),
                    "progress": int(max(0, _as_int(row.get("progress", 0), 0))),
                    "status": str((dict(row.get("extensions") or {})).get("status", "")).strip() or "active",
                }
                for row in run_rows
            ]
        ),
        "batch_quality_hash_chain": canonical_sha256(
            [
                {
                    "batch_id": str(row.get("batch_id", "")).strip(),
                    "quality_grade": str(row.get("quality_grade", "")).strip(),
                    "yield_factor": int(max(0, _as_int(row.get("yield_factor", 0), 0))),
                    "defect_flags": sorted(set(str(token).strip() for token in list(row.get("defect_flags") or []) if str(token).strip())),
                    "contamination_tags": sorted(
                        set(str(token).strip() for token in list(row.get("contamination_tags") or []) if str(token).strip())
                    ),
                }
                for row in quality_rows
            ]
        ),
        "yield_model_hash_chain": canonical_sha256(
            [
                {
                    "run_id": str(row.get("run_id", "")).strip(),
                    "yield_model_id": str(row.get("yield_model_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "yield_factor_permille": int(max(0, _as_int(row.get("yield_factor_permille", 0), 0))),
                    "temperature": int(_as_int(row.get("temperature", 0), 0)),
                    "pressure_head": int(max(0, _as_int(row.get("pressure_head", 0), 0))),
                    "entropy_value": int(max(0, _as_int(row.get("entropy_value", 0), 0))),
                }
                for row in yield_rows
            ]
        ),
    }


def _mass_sanity_violations(payload: Mapping[str, object]) -> List[str]:
    violations: List[str] = []
    for row in _batch_rows(payload):
        batch_id = str(row.get("batch_id", "")).strip() or "batch.unknown"
        if _as_int(row.get("quantity_mass_raw", 0), 0) < 0:
            violations.append("negative batch mass for '{}'".format(batch_id))
    for row in _quality_rows(payload):
        batch_id = str(row.get("batch_id", "")).strip() or "batch.unknown"
        if _as_int(row.get("yield_factor", 0), 0) < 0:
            violations.append("negative yield_factor for '{}'".format(batch_id))
    return violations


def _ledger_violations(payload: Mapping[str, object]) -> List[str]:
    violations: List[str] = []
    run_ids = {
        str(row.get("run_id", "")).strip()
        for row in _run_rows(payload)
        if str(row.get("run_id", "")).strip()
    }
    by_source: Dict[str, int] = {}
    transform_ids = set()
    for row in _ledger_rows(payload):
        source_id = str(row.get("source_id", "")).strip()
        if source_id:
            by_source[source_id] = _as_int(by_source.get(source_id, 0), 0) + 1
        transform_id = str(row.get("transformation_id", "")).strip()
        if transform_id:
            transform_ids.add(transform_id)
    for run_id in sorted(run_ids):
        if _as_int(by_source.get(run_id, 0), 0) <= 0:
            violations.append("missing energy_ledger_entries for run_id='{}'".format(run_id))
    if run_ids and "transform.chemical_to_thermal" not in transform_ids:
        violations.append("missing transform.chemical_to_thermal in ledger rows")
    return violations


def _yield_determinism_violations(payload: Mapping[str, object]) -> List[str]:
    violations: List[str] = []
    buckets: Dict[Tuple[str, str, int, int, int], set] = {}
    for row in _yield_rows(payload):
        key = (
            str(row.get("run_id", "")).strip(),
            str(row.get("yield_model_id", "")).strip(),
            int(_as_int(row.get("temperature", 0), 0)),
            int(max(0, _as_int(row.get("pressure_head", 0), 0))),
            int(max(0, _as_int(row.get("entropy_value", 0), 0))),
        )
        value = int(max(0, _as_int(row.get("yield_factor_permille", 0), 0)))
        buckets.setdefault(key, set()).add(value)
    for key in sorted(buckets.keys()):
        values = sorted(buckets[key])
        if len(values) > 1:
            violations.append(
                "yield drift for run_id='{}' model='{}' context=({}, {}, {}) values={}".format(
                    key[0],
                    key[1],
                    key[2],
                    key[3],
                    key[4],
                    values,
                )
            )
    return violations


def verify_process_run_window(*, state_payload: Mapping[str, object], expected_payload: Mapping[str, object] | None = None) -> dict:
    observed = _hash_chains(state_payload)
    report = {
        "result": "complete",
        "violations": [],
        "observed": dict(observed),
        "recorded": {
            "process_run_hash_chain": str(state_payload.get("process_run_hash_chain", "")).strip().lower(),
            "batch_quality_hash_chain": str(state_payload.get("batch_quality_hash_chain", "")).strip().lower(),
            "yield_model_hash_chain": str(state_payload.get("yield_model_hash_chain", "")).strip().lower(),
        },
        "counts": {
            "process_run_rows": len(_run_rows(state_payload)),
            "batch_quality_rows": len(_quality_rows(state_payload)),
            "yield_model_rows": len(_yield_rows(state_payload)),
            "material_batches": len(_batch_rows(state_payload)),
            "energy_ledger_entries": len(_ledger_rows(state_payload)),
        },
        "deterministic_fingerprint": "",
    }

    for key in ("process_run_hash_chain", "batch_quality_hash_chain", "yield_model_hash_chain"):
        recorded = str((dict(report.get("recorded") or {})).get(key, "")).strip().lower()
        if recorded and recorded != str(observed.get(key, "")).strip().lower():
            report["violations"].append("recorded {} does not match replay hash".format(key))

    report["violations"].extend(_mass_sanity_violations(state_payload))
    report["violations"].extend(_ledger_violations(state_payload))
    report["violations"].extend(_yield_determinism_violations(state_payload))

    if expected_payload:
        expected = _hash_chains(dict(expected_payload))
        report["expected"] = dict(expected)
        for key in ("process_run_hash_chain", "batch_quality_hash_chain", "yield_model_hash_chain"):
            if str(expected.get(key, "")).strip().lower() != str(observed.get(key, "")).strip().lower():
                report["violations"].append("{} mismatch against expected replay baseline".format(key))

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify replay-window determinism for CHEM-2 process-run hashes.")
    parser.add_argument("--state-path", default="", help="JSON payload path containing process-run, quality, and ledger rows.")
    parser.add_argument("--expected-state-path", default="", help="Optional second payload for replay hash equality checks.")
    args = parser.parse_args()

    state_path = str(args.state_path or "").strip()
    if not state_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.chem.process_run.state_path_required",
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
                    "reason_code": "refusal.chem.process_run.state_payload_invalid",
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
                        "reason_code": "refusal.chem.process_run.expected_payload_invalid",
                        "message": expected_error,
                        "expected_state_path": os.path.normpath(os.path.abspath(expected_path)),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2

    report = verify_process_run_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())