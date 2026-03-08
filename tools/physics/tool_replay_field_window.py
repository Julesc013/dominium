#!/usr/bin/env python3
"""Verify PHYS-2 field replay windows reproduce deterministic field hash chains."""

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

from src.fields import normalize_field_sample_rows  # noqa: E402
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


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _field_update_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("field_update_events")
    if not isinstance(rows, list):
        rows = []
    normalized: List[dict] = []
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("source_process_id", "")),
            str(item.get("event_id", "")),
        ),
    ):
        normalized.append(
            {
                "event_id": str(row.get("event_id", "")).strip(),
                "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                "source_process_id": str(row.get("source_process_id", "")).strip() or "process.unknown",
                "update_kind": str(row.get("update_kind", "")).strip() or "field_update",
                "updated_field_ids": _sorted_tokens(list(row.get("updated_field_ids") or [])),
                "applied_update_count": int(max(0, _as_int(row.get("applied_update_count", 0), 0))),
                "skipped_update_count": int(max(0, _as_int(row.get("skipped_update_count", 0), 0))),
                "field_sample_count": int(max(0, _as_int(row.get("field_sample_count", 0), 0))),
                "boundary_field_exchange_count": int(max(0, _as_int(row.get("boundary_field_exchange_count", 0), 0))),
                "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            }
        )
    return normalized


def _boundary_rows(payload: Mapping[str, object]) -> List[dict]:
    rows = payload.get("portal_flow_params")
    if not isinstance(rows, list):
        rows = []
    out: List[dict] = []
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("portal_id", "")),
    ):
        portal_id = str(row.get("portal_id", "")).strip()
        if not portal_id:
            continue
        ext = dict(row.get("extensions") or {})
        boundary = dict(ext.get("field_boundary") or {})
        if not boundary:
            continue
        wind = dict(boundary.get("wind_vector") or {})
        sampled_geo_cell_keys = dict(boundary.get("field_sampled_geo_cell_keys") or {})
        out.append(
            {
                "portal_id": portal_id,
                "temperature": int(_as_int(boundary.get("temperature", 0), 0)),
                "moisture": int(max(0, _as_int(boundary.get("moisture", 0), 0))),
                "visibility": int(max(0, _as_int(boundary.get("visibility", 0), 0))),
                "wind_vector": {
                    "x": int(_as_int(wind.get("x", 0), 0)),
                    "y": int(_as_int(wind.get("y", 0), 0)),
                    "z": int(_as_int(wind.get("z", 0), 0)),
                },
                "wind_magnitude": int(max(0, _as_int(boundary.get("wind_magnitude", 0), 0))),
                "wind_boost_air_conductance": int(max(0, _as_int(boundary.get("wind_boost_air_conductance", 0), 0))),
                "ram_air_boost_air_conductance": int(
                    max(0, _as_int(boundary.get("ram_air_boost_air_conductance", 0), 0))
                ),
                "field_sampled_cell_ids": dict(boundary.get("field_sampled_cell_ids") or {}),
                "field_sampled_geo_cell_key_hashes": dict(
                    (
                        str(field_id).strip(),
                        canonical_sha256(dict(sampled_geo_cell_keys.get(field_id) or {})),
                    )
                    for field_id in sorted(sampled_geo_cell_keys.keys())
                    if str(field_id).strip()
                ),
                "source_tick": int(max(0, _as_int(boundary.get("source_tick", 0), 0))),
                "source_process_id": str(boundary.get("source_process_id", "")).strip() or None,
                "deterministic_fingerprint": canonical_sha256(
                    {
                        "portal_id": portal_id,
                        "boundary": dict(boundary),
                    }
                ),
            }
        )
    return out


def _field_hash_chains(payload: Mapping[str, object]) -> Dict[str, str]:
    update_rows = _field_update_rows(payload)
    sample_rows = normalize_field_sample_rows(payload.get("field_sample_rows") or [])
    boundary_rows = _boundary_rows(payload)
    return {
        "field_update_hash_chain": canonical_sha256(list(update_rows)),
        "field_sample_hash_chain": canonical_sha256(
            [
                {
                    "field_id": str(row.get("field_id", "")).strip(),
                    "spatial_node_id": str(row.get("spatial_node_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "sampled_value": row.get("sampled_value"),
                    "has_cell": bool(row.get("has_cell", False)),
                    "sampled_cell_id": str(row.get("sampled_cell_id", "")).strip(),
                    "sampled_geo_cell_key_hash": canonical_sha256(
                        dict((dict(row.get("extensions") or {})).get("geo_cell_key") or {})
                    ),
                    "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
                }
                for row in sample_rows
            ]
        ),
        "boundary_field_exchange_hash_chain": canonical_sha256(list(boundary_rows)),
    }


def verify_field_replay_window(*, state_payload: Mapping[str, object], expected_payload: Mapping[str, object] | None = None) -> dict:
    observed = _field_hash_chains(state_payload)
    report = {
        "result": "complete",
        "violations": [],
        "observed": dict(observed),
        "recorded": {
            "field_update_hash_chain": str(state_payload.get("field_update_hash_chain", "")).strip().lower(),
            "field_sample_hash_chain": str(state_payload.get("field_sample_hash_chain", "")).strip().lower(),
            "boundary_field_exchange_hash_chain": str(
                state_payload.get("boundary_field_exchange_hash_chain", "")
            ).strip().lower(),
        },
        "deterministic_fingerprint": "",
    }

    for key in ("field_update_hash_chain", "field_sample_hash_chain", "boundary_field_exchange_hash_chain"):
        recorded = str(report["recorded"][key]).strip().lower()
        observed_value = str(observed[key]).strip().lower()
        if recorded and recorded != observed_value:
            report["violations"].append("recorded {} does not match replay hash".format(key))

    if expected_payload:
        expected = _field_hash_chains(dict(expected_payload))
        report["expected"] = dict(expected)
        for key in ("field_update_hash_chain", "field_sample_hash_chain", "boundary_field_exchange_hash_chain"):
            if str(expected[key]).strip().lower() != str(observed[key]).strip().lower():
                report["violations"].append("{} mismatch against expected replay baseline".format(key))

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify replay-window determinism for PHYS field hash chains.")
    parser.add_argument("--state-path", default="", help="JSON payload path containing field state/events.")
    parser.add_argument("--expected-state-path", default="", help="Optional second payload for replay equality checks.")
    args = parser.parse_args()

    state_path = str(args.state_path or "").strip()
    if not state_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.field.state_path_required",
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
                    "reason_code": "refusal.field.state_payload_invalid",
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
                        "reason_code": "refusal.field.expected_payload_invalid",
                        "message": expected_error,
                        "expected_state_path": os.path.normpath(os.path.abspath(expected_path)),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2

    report = verify_field_replay_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
