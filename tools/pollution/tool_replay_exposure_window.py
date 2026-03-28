#!/usr/bin/env python3
"""Verify POLL-2 exposure/compliance replay windows reproduce deterministic hash chains."""

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

from pollution.compliance_engine import (  # noqa: E402
    normalize_pollution_compliance_report_rows,
)
from pollution.exposure_engine import normalize_health_risk_event_rows  # noqa: E402
from pollution.measurement_engine import normalize_pollution_measurement_rows  # noqa: E402
from pollution.dispersion_engine import (  # noqa: E402
    normalize_pollution_exposure_state_rows,
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


def _health_risk_hash_chain(payload: Mapping[str, object]) -> str:
    rows = normalize_health_risk_event_rows(payload.get("pollution_health_risk_event_rows") or [])
    return canonical_sha256(
        [
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "subject_id": str(row.get("subject_id", "")).strip(),
                "pollutant_id": str(row.get("pollutant_id", "")).strip(),
                "threshold_crossed": str(row.get("threshold_crossed", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            }
            for row in rows
        ]
    )


def _measurement_hash_chain(payload: Mapping[str, object]) -> str:
    rows = normalize_pollution_measurement_rows(payload.get("pollution_measurement_rows") or [])
    return canonical_sha256(
        [
            {
                "measurement_id": str(row.get("measurement_id", "")).strip(),
                "pollutant_id": str(row.get("pollutant_id", "")).strip(),
                "spatial_scope_id": str(row.get("spatial_scope_id", "")).strip(),
                "measured_concentration": int(max(0, _as_int(row.get("measured_concentration", 0), 0))),
                "instrument_id": None if row.get("instrument_id") is None else str(row.get("instrument_id", "")).strip() or None,
                "calibration_cert_id": None if row.get("calibration_cert_id") is None else str(row.get("calibration_cert_id", "")).strip() or None,
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
            }
            for row in rows
        ]
    )


def _compliance_hash_chain(payload: Mapping[str, object]) -> str:
    rows = normalize_pollution_compliance_report_rows(payload.get("pollution_compliance_report_rows") or [])
    return canonical_sha256(
        [
            {
                "report_id": str(row.get("report_id", "")).strip(),
                "region_id": str(row.get("region_id", "")).strip(),
                "pollutant_id": str(row.get("pollutant_id", "")).strip(),
                "observed_statistic": str(row.get("observed_statistic", "")).strip(),
                "threshold": int(max(0, _as_int(row.get("threshold", 0), 0))),
                "status": str(row.get("status", "")).strip(),
                "start_tick": int(max(0, _as_int(dict(row.get("tick_range") or {}).get("start_tick", 0), 0))),
                "end_tick": int(max(0, _as_int(dict(row.get("tick_range") or {}).get("end_tick", 0), 0))),
            }
            for row in rows
        ]
    )


def _pollution_hash_chains(payload: Mapping[str, object]) -> dict:
    return {
        "pollution_exposure_hash_chain": _exposure_hash_chain(payload),
        "pollution_health_risk_hash_chain": _health_risk_hash_chain(payload),
        "pollution_measurement_hash_chain": _measurement_hash_chain(payload),
        "pollution_compliance_report_hash_chain": _compliance_hash_chain(payload),
    }


def verify_exposure_replay_window(*, state_payload: Mapping[str, object], expected_payload: Mapping[str, object] | None = None) -> dict:
    observed = _pollution_hash_chains(state_payload)
    report = {
        "result": "complete",
        "violations": [],
        "observed": dict(observed),
        "recorded": {
            "pollution_exposure_hash_chain": str(state_payload.get("pollution_exposure_hash_chain", "")).strip().lower(),
            "pollution_health_risk_hash_chain": str(state_payload.get("pollution_health_risk_hash_chain", "")).strip().lower(),
            "pollution_measurement_hash_chain": str(state_payload.get("pollution_measurement_hash_chain", "")).strip().lower(),
            "pollution_compliance_report_hash_chain": str(state_payload.get("pollution_compliance_report_hash_chain", "")).strip().lower(),
        },
        "proof_surface": {
            "exposure_hash_chain": str(observed.get("pollution_exposure_hash_chain", "")).strip().lower(),
            "measurement_hash_chain": str(observed.get("pollution_measurement_hash_chain", "")).strip().lower(),
            "compliance_report_hash_chain": str(observed.get("pollution_compliance_report_hash_chain", "")).strip().lower(),
        },
        "deterministic_fingerprint": "",
    }

    for key in (
        "pollution_exposure_hash_chain",
        "pollution_health_risk_hash_chain",
        "pollution_measurement_hash_chain",
        "pollution_compliance_report_hash_chain",
    ):
        recorded = str(report["recorded"][key]).strip().lower()
        observed_value = str(observed[key]).strip().lower()
        if recorded and recorded != observed_value:
            report["violations"].append("recorded {} does not match replay hash".format(key))

    if expected_payload:
        expected = _pollution_hash_chains(dict(expected_payload))
        report["expected"] = dict(expected)
        for key in (
            "pollution_exposure_hash_chain",
            "pollution_health_risk_hash_chain",
            "pollution_measurement_hash_chain",
            "pollution_compliance_report_hash_chain",
        ):
            if str(expected[key]).strip().lower() != str(observed[key]).strip().lower():
                report["violations"].append("{} mismatch against expected replay baseline".format(key))

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify replay-window determinism for POLL-2 exposure hash chains.")
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

    report = verify_exposure_replay_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
