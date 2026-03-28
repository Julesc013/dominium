#!/usr/bin/env python3
"""Verify POLL-1 dispersion replay windows reproduce deterministic pollution hash chains."""

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

from pollution.dispersion_engine import (  # noqa: E402
    normalize_pollution_deposition_rows,
    normalize_pollution_dispersion_step_rows,
    normalize_pollution_exposure_state_rows,
    pollution_deposition_hash_chain,
    pollution_field_hash_chain,
)
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


def _pollutant_ids_from_payload(payload: Mapping[str, object]) -> List[str]:
    out = set()

    registry_payload = dict((dict(payload).get("pollutant_type_registry") or {}))
    registry_record = dict(registry_payload.get("record") or {})
    registry_rows = list(registry_record.get("pollutant_types") or [])
    for row in registry_rows:
        if not isinstance(row, Mapping):
            continue
        token = str(row.get("pollutant_id", "")).strip()
        if token:
            out.add(token)

    for key in (
        "pollution_source_event_rows",
        "pollution_dispersion_step_rows",
        "pollution_deposition_rows",
        "pollution_exposure_state_rows",
    ):
        for row in list(payload.get(key) or []):
            if not isinstance(row, Mapping):
                continue
            token = str(row.get("pollutant_id", "")).strip()
            if token:
                out.add(token)

    for row in list(payload.get("field_cells") or []):
        if not isinstance(row, Mapping):
            continue
        field_id = str(row.get("field_id", "")).strip()
        if not (field_id.startswith("field.pollution.") and field_id.endswith("_concentration")):
            continue
        suffix = field_id[len("field.pollution.") : -len("_concentration")]
        if suffix:
            out.add("pollutant.{}".format(suffix))

    return sorted(out)


def _dispersion_hash_chain(payload: Mapping[str, object]) -> str:
    rows = normalize_pollution_dispersion_step_rows(payload.get("pollution_dispersion_step_rows") or [])
    return canonical_sha256(
        [
            {
                "step_id": str(row.get("step_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "pollutant_id": str(row.get("pollutant_id", "")).strip(),
                "spatial_scope_id": str(row.get("spatial_scope_id", "")).strip(),
                "concentration_before": int(max(0, _as_int(row.get("concentration_before", 0), 0))),
                "concentration_after": int(max(0, _as_int(row.get("concentration_after", 0), 0))),
                "injected_mass": int(max(0, _as_int(row.get("injected_mass", 0), 0))),
                "diffusion_term": int(_as_int(row.get("diffusion_term", 0), 0)),
                "decay_mass": int(max(0, _as_int(row.get("decay_mass", 0), 0))),
                "deposition_mass": int(max(0, _as_int(row.get("deposition_mass", 0), 0))),
                "policy_id": str(row.get("policy_id", "")).strip(),
                "decay_model_id": str(row.get("decay_model_id", "")).strip(),
            }
            for row in rows
        ]
    )


def _exposure_hash_chain(payload: Mapping[str, object]) -> str:
    rows = normalize_pollution_exposure_state_rows(payload.get("pollution_exposure_state_rows") or [])
    return canonical_sha256(
        [
            {
                "subject_id": str(row.get("subject_id", "")).strip(),
                "pollutant_id": str(row.get("pollutant_id", "")).strip(),
                "accumulated_exposure": int(max(0, _as_int(row.get("accumulated_exposure", 0), 0))),
                "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
            }
            for row in rows
        ]
    )


def _pollution_hash_chains(payload: Mapping[str, object]) -> Dict[str, str]:
    pollutant_types_by_id = dict((pollutant_id, {"pollutant_id": pollutant_id}) for pollutant_id in _pollutant_ids_from_payload(payload))
    if not pollutant_types_by_id:
        pollutant_types_by_id = {
            "pollutant.smoke_particulate": {"pollutant_id": "pollutant.smoke_particulate"},
            "pollutant.co2_stub": {"pollutant_id": "pollutant.co2_stub"},
            "pollutant.toxic_gas_stub": {"pollutant_id": "pollutant.toxic_gas_stub"},
            "pollutant.oil_spill_stub": {"pollutant_id": "pollutant.oil_spill_stub"},
        }
    deposition_rows = normalize_pollution_deposition_rows(payload.get("pollution_deposition_rows") or [])
    return {
        "pollution_dispersion_hash_chain": _dispersion_hash_chain(payload),
        "pollution_deposition_hash_chain": pollution_deposition_hash_chain(deposition_rows),
        "pollution_field_hash_chain": pollution_field_hash_chain(
            field_cell_rows=payload.get("field_cells"),
            pollutant_types_by_id=pollutant_types_by_id,
        ),
        "pollution_exposure_hash_chain": _exposure_hash_chain(payload),
    }


def verify_dispersion_replay_window(*, state_payload: Mapping[str, object], expected_payload: Mapping[str, object] | None = None) -> dict:
    observed = _pollution_hash_chains(state_payload)
    report = {
        "result": "complete",
        "violations": [],
        "observed": dict(observed),
        "recorded": {
            "pollution_dispersion_hash_chain": str(state_payload.get("pollution_dispersion_hash_chain", "")).strip().lower(),
            "pollution_deposition_hash_chain": str(state_payload.get("pollution_deposition_hash_chain", "")).strip().lower(),
            "pollution_field_hash_chain": str(state_payload.get("pollution_field_hash_chain", "")).strip().lower(),
            "pollution_exposure_hash_chain": str(state_payload.get("pollution_exposure_hash_chain", "")).strip().lower(),
        },
        "proof_surface": {
            "pollution_field_hash_chain": str(observed.get("pollution_field_hash_chain", "")).strip().lower(),
            "deposition_hash_chain": str(observed.get("pollution_deposition_hash_chain", "")).strip().lower(),
        },
        "deterministic_fingerprint": "",
    }

    for key in (
        "pollution_dispersion_hash_chain",
        "pollution_deposition_hash_chain",
        "pollution_field_hash_chain",
        "pollution_exposure_hash_chain",
    ):
        recorded = str(report["recorded"][key]).strip().lower()
        observed_value = str(observed[key]).strip().lower()
        if recorded and recorded != observed_value:
            report["violations"].append("recorded {} does not match replay hash".format(key))

    if expected_payload:
        expected = _pollution_hash_chains(dict(expected_payload))
        report["expected"] = dict(expected)
        for key in (
            "pollution_dispersion_hash_chain",
            "pollution_deposition_hash_chain",
            "pollution_field_hash_chain",
            "pollution_exposure_hash_chain",
        ):
            if str(expected[key]).strip().lower() != str(observed[key]).strip().lower():
                report["violations"].append("{} mismatch against expected replay baseline".format(key))

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify replay-window determinism for POLL dispersion hash chains.")
    parser.add_argument("--state-path", default="", help="JSON payload path containing pollution state/events.")
    parser.add_argument("--expected-state-path", default="", help="Optional second payload for replay equality checks.")
    args = parser.parse_args()

    state_path = str(args.state_path or "").strip()
    if not state_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.pollution.state_path_required",
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
                    "reason_code": "refusal.pollution.state_payload_invalid",
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
                        "reason_code": "refusal.pollution.expected_payload_invalid",
                        "message": expected_error,
                        "expected_state_path": os.path.normpath(os.path.abspath(expected_path)),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2

    report = verify_dispersion_replay_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
