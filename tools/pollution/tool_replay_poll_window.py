#!/usr/bin/env python3
"""Verify POLL-3 replay windows reproduce deterministic pollution proof hash chains."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Mapping, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.pollution.dispersion_engine import pollution_field_hash_chain  # noqa: E402
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


def _state_payload(payload: Mapping[str, object]) -> dict:
    ext = _as_map(payload.get("extensions"))
    final_state = _as_map(ext.get("final_state_snapshot"))
    if final_state:
        return final_state
    return dict(payload)


def _emission_hash_chain(state: Mapping[str, object]) -> str:
    rows = [dict(row) for row in list(state.get("pollution_source_event_rows") or []) if isinstance(row, Mapping)]
    rows = sorted(
        rows,
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("source_event_id", row.get("event_id", ""))),
            str(row.get("origin_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "source_event_id": str(row.get("source_event_id", row.get("event_id", ""))).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "origin_kind": str(row.get("origin_kind", "")).strip(),
                "origin_id": str(row.get("origin_id", "")).strip(),
                "pollutant_id": str(row.get("pollutant_id", "")).strip(),
                "emitted_mass": int(max(0, _as_int(row.get("emitted_mass", 0), 0))),
                "spatial_scope_id": str(row.get("spatial_scope_id", "")).strip(),
            }
            for row in rows
        ]
    )


def _exposure_hash_chain(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in list(state.get("pollution_exposure_state_rows") or [])
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            str(item.get("subject_id", "")),
            str(item.get("pollutant_id", "")),
        ),
    )
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


def _compliance_hash_chain(state: Mapping[str, object]) -> str:
    rows = sorted(
        (
            dict(item)
            for item in list(state.get("pollution_compliance_report_rows") or [])
            if isinstance(item, Mapping)
        ),
        key=lambda item: (
            str(item.get("region_id", "")),
            str(item.get("pollutant_id", "")),
            str(item.get("report_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "report_id": str(row.get("report_id", "")).strip(),
                "region_id": str(row.get("region_id", "")).strip(),
                "pollutant_id": str(row.get("pollutant_id", "")).strip(),
                "observed_statistic": str(row.get("observed_statistic", "")).strip(),
                "threshold": int(max(0, _as_int(row.get("threshold", 0), 0))),
                "status": str(row.get("status", "")).strip(),
                "start_tick": int(max(0, _as_int(_as_map(row.get("tick_range")).get("start_tick", 0), 0))),
                "end_tick": int(max(0, _as_int(_as_map(row.get("tick_range")).get("end_tick", 0), 0))),
            }
            for row in rows
        ]
    )


def _degradation_hash_chain(state: Mapping[str, object]) -> str:
    rows = [dict(row) for row in list(state.get("pollution_dispersion_degrade_rows") or []) if isinstance(row, Mapping)]
    rows = sorted(
        rows,
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("event_id", "")),
        ),
    )
    return canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "degrade_reason": str(row.get("degrade_reason", "")).strip(),
                "deferred_cell_ids": sorted(set(str(item).strip() for item in list(row.get("deferred_cell_ids") or []) if str(item).strip())),
            }
            for row in rows
        ]
    )


def _pollutant_ids(state: Mapping[str, object]) -> list[str]:
    out = set()
    for row in list(state.get("pollution_source_event_rows") or []):
        if not isinstance(row, Mapping):
            continue
        token = str(row.get("pollutant_id", "")).strip()
        if token:
            out.add(token)
    for row in list(state.get("pollution_dispersion_step_rows") or []):
        if not isinstance(row, Mapping):
            continue
        token = str(row.get("pollutant_id", "")).strip()
        if token:
            out.add(token)
    for row in list(state.get("field_cells") or []):
        if not isinstance(row, Mapping):
            continue
        field_id = str(row.get("field_id", "")).strip()
        if not (field_id.startswith("field.pollution.") and field_id.endswith("_concentration")):
            continue
        suffix = field_id[len("field.pollution.") : -len("_concentration")]
        if suffix:
            out.add("pollutant.{}".format(suffix))
    return sorted(out)


def _pollution_hashes(state: Mapping[str, object]) -> dict:
    pollutant_ids = _pollutant_ids(state)
    pollutant_types_by_id = dict((token, {"pollutant_id": token}) for token in pollutant_ids)
    if not pollutant_types_by_id:
        pollutant_types_by_id = {
            "pollutant.smoke_particulate": {"pollutant_id": "pollutant.smoke_particulate"},
            "pollutant.co2_stub": {"pollutant_id": "pollutant.co2_stub"},
            "pollutant.toxic_gas_stub": {"pollutant_id": "pollutant.toxic_gas_stub"},
            "pollutant.oil_spill_stub": {"pollutant_id": "pollutant.oil_spill_stub"},
        }
    return {
        "pollution_emission_hash_chain": _emission_hash_chain(state),
        "pollution_field_hash_chain": pollution_field_hash_chain(
            field_cell_rows=state.get("field_cells"),
            pollutant_types_by_id=pollutant_types_by_id,
        ),
        "pollution_exposure_hash_chain": _exposure_hash_chain(state),
        "pollution_compliance_hash_chain": _compliance_hash_chain(state),
        "pollution_degradation_event_hash_chain": _degradation_hash_chain(state),
    }


def verify_poll_replay_window(*, state_payload: Mapping[str, object], expected_payload: Mapping[str, object] | None = None) -> dict:
    state = _state_payload(state_payload)
    observed = _pollution_hashes(state)
    report = {
        "result": "complete",
        "violations": [],
        "observed": dict(observed),
        "recorded": {
            "pollution_emission_hash_chain": str(state.get("pollution_emission_hash_chain", state.get("pollution_source_hash_chain", ""))).strip().lower(),
            "pollution_field_hash_chain": str(state.get("pollution_field_hash_chain", "")).strip().lower(),
            "pollution_exposure_hash_chain": str(state.get("pollution_exposure_hash_chain", "")).strip().lower(),
            "pollution_compliance_hash_chain": str(state.get("pollution_compliance_hash_chain", state.get("pollution_compliance_report_hash_chain", ""))).strip().lower(),
            "pollution_degradation_event_hash_chain": str(state.get("pollution_degradation_event_hash_chain", state.get("pollution_dispersion_degrade_hash_chain", ""))).strip().lower(),
        },
        "deterministic_fingerprint": "",
    }

    for key in (
        "pollution_emission_hash_chain",
        "pollution_field_hash_chain",
        "pollution_exposure_hash_chain",
        "pollution_compliance_hash_chain",
        "pollution_degradation_event_hash_chain",
    ):
        recorded = str(report["recorded"][key]).strip().lower()
        observed_value = str(observed[key]).strip().lower()
        if recorded and (recorded != observed_value):
            report["violations"].append("recorded {} does not match replay hash".format(key))

    if expected_payload:
        expected_state = _state_payload(expected_payload)
        expected = _pollution_hashes(expected_state)
        report["expected"] = dict(expected)
        for key in (
            "pollution_emission_hash_chain",
            "pollution_field_hash_chain",
            "pollution_exposure_hash_chain",
            "pollution_compliance_hash_chain",
            "pollution_degradation_event_hash_chain",
        ):
            if str(expected[key]).strip().lower() != str(observed[key]).strip().lower():
                report["violations"].append("{} mismatch against expected replay baseline".format(key))

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify deterministic replay hashes for POLL-3 stress windows.")
    parser.add_argument("--state-path", default="build/pollution/poll3_stress_report.json")
    parser.add_argument("--expected-state-path", default="")
    args = parser.parse_args()

    state_path = os.path.normpath(os.path.abspath(str(args.state_path)))
    state_payload, state_err = _read_json(state_path)
    if state_err:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.pollution.replay.state_payload_invalid",
                    "message": state_err,
                    "state_path": state_path,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    expected_payload = None
    expected_path = str(args.expected_state_path or "").strip()
    if expected_path:
        expected_abs = os.path.normpath(os.path.abspath(expected_path))
        expected_payload, expected_err = _read_json(expected_abs)
        if expected_err:
            print(
                json.dumps(
                    {
                        "result": "refusal",
                        "reason_code": "refusal.pollution.replay.expected_payload_invalid",
                        "message": expected_err,
                        "expected_state_path": expected_abs,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2

    report = verify_poll_replay_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
