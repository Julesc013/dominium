#!/usr/bin/env python3
"""Verify TEMP-1 replay windows reproduce deterministic time-mapping/schedule hashes."""

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

from engine.time import (  # noqa: E402
    normalize_proper_time_state_rows,
    normalize_time_adjust_event_rows,
    normalize_time_mapping_cache_rows,
    normalize_time_stamp_artifact_rows,
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


def _normalize_schedule_domain_evaluations(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("temporal_domain_id", "")),
            str(item.get("schedule_id", "")),
        ),
    ):
        schedule_id = str(row.get("schedule_id", "")).strip()
        if not schedule_id:
            continue
        tick = int(max(0, _as_int(row.get("tick", 0), 0)))
        temporal_domain_id = str(row.get("temporal_domain_id", "")).strip() or "time.canonical_tick"
        payload = {
            "schema_version": "1.0.0",
            "schedule_id": schedule_id,
            "target_id": str(row.get("target_id", "")).strip(),
            "temporal_domain_id": temporal_domain_id,
            "tick": int(tick),
            "domain_time_value": int(_as_int(row.get("domain_time_value", -1), -1)),
            "target_time_value": int(max(0, _as_int(row.get("target_time_value", 0), 0))),
            "due": bool(row.get("due", False)),
            "evaluation_policy_id": str(row.get("evaluation_policy_id", "")).strip() or "schedule.eval.gte_target",
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), Mapping) else {},
        }
        if not payload["deterministic_fingerprint"]:
            payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        key = "{}::{}::{}".format(int(tick), temporal_domain_id, schedule_id)
        out[key] = payload
    return [
        dict(out[key])
        for key in sorted(
            out.keys(),
            key=lambda token: (
                int(_as_int((token.split("::", 2) + ["0", "0", "0"])[0], 0)),
                str((token.split("::", 2) + ["", "", ""])[1]),
                str((token.split("::", 2) + ["", "", ""])[2]),
            ),
        )
    ]


def _hash_chains(payload: Mapping[str, object]) -> dict:
    mapping_rows = normalize_time_mapping_cache_rows(payload.get("time_mapping_cache_rows") or [])
    stamp_rows = normalize_time_stamp_artifact_rows(
        payload.get("time_stamp_artifacts") or payload.get("time_stamp_rows") or []
    )
    proper_rows = normalize_proper_time_state_rows(payload.get("proper_time_states") or [])
    schedule_domain_rows = _normalize_schedule_domain_evaluations(payload.get("schedule_domain_evaluations") or [])
    adjust_rows = normalize_time_adjust_event_rows(payload.get("time_adjust_events") or [])
    return {
        "time_mapping_hash_chain": canonical_sha256(
            [
                {
                    "mapping_id": str(row.get("mapping_id", "")).strip(),
                    "temporal_domain_id": str(row.get("temporal_domain_id", "")).strip(),
                    "scope_id": str(row.get("scope_id", "")).strip(),
                    "canonical_tick": int(max(0, _as_int(row.get("canonical_tick", 0), 0))),
                    "domain_time_value": int(_as_int(row.get("domain_time_value", 0), 0)),
                    "delta_domain_time": int(_as_int(row.get("delta_domain_time", 0), 0)),
                    "model_id": str(row.get("model_id", "")).strip(),
                    "drift_policy_id": str(row.get("drift_policy_id", "")).strip(),
                    "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
                }
                for row in mapping_rows
            ]
        ),
        "schedule_domain_evaluation_hash": canonical_sha256(
            [
                {
                    "schedule_id": str(row.get("schedule_id", "")).strip(),
                    "target_id": str(row.get("target_id", "")).strip(),
                    "temporal_domain_id": str(row.get("temporal_domain_id", "")).strip(),
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "domain_time_value": int(_as_int(row.get("domain_time_value", 0), 0)),
                    "target_time_value": int(max(0, _as_int(row.get("target_time_value", 0), 0))),
                    "due": bool(row.get("due", False)),
                    "evaluation_policy_id": str(row.get("evaluation_policy_id", "")).strip(),
                    "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
                }
                for row in schedule_domain_rows
            ]
        ),
        "time_stamp_hash_chain": canonical_sha256(
            [
                {
                    "stamp_id": str(row.get("stamp_id", "")).strip(),
                    "temporal_domain_id": str(row.get("temporal_domain_id", "")).strip(),
                    "canonical_tick": int(max(0, _as_int(row.get("canonical_tick", 0), 0))),
                    "domain_time_value": int(_as_int(row.get("domain_time_value", 0), 0)),
                    "issuer_subject_id": str(row.get("issuer_subject_id", "")).strip(),
                    "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
                }
                for row in stamp_rows
            ]
        ),
        "proper_time_hash_chain": canonical_sha256(
            [
                {
                    "target_id": str(row.get("target_id", "")).strip(),
                    "accumulated_proper_time": int(max(0, _as_int(row.get("accumulated_proper_time", 0), 0))),
                    "last_update_tick": int(max(0, _as_int(row.get("last_update_tick", 0), 0))),
                    "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
                }
                for row in proper_rows
            ]
        ),
        "time_adjust_event_hash_chain": canonical_sha256(
            [
                {
                    "adjust_id": str(row.get("adjust_id", "")).strip(),
                    "target_id": str(row.get("target_id", "")).strip(),
                    "temporal_domain_id": str(row.get("temporal_domain_id", "")).strip(),
                    "canonical_tick": int(max(0, _as_int(row.get("canonical_tick", 0), 0))),
                    "previous_domain_time": int(_as_int(row.get("previous_domain_time", 0), 0)),
                    "new_domain_time": int(_as_int(row.get("new_domain_time", 0), 0)),
                    "adjustment_delta": int(_as_int(row.get("adjustment_delta", 0), 0)),
                    "originating_receipt_id": str(row.get("originating_receipt_id", "")).strip(),
                    "sync_policy_id": str(row.get("sync_policy_id", "")).strip(),
                    "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
                }
                for row in adjust_rows
            ]
        ),
        "drift_policy_id": str(payload.get("drift_policy_id", "")).strip() or "drift.none",
    }


def _proper_time_monotonic_violations(payload: Mapping[str, object]) -> List[str]:
    mapping_rows = normalize_time_mapping_cache_rows(payload.get("time_mapping_cache_rows") or [])
    relevant_rows = [
        dict(row)
        for row in mapping_rows
        if str(row.get("temporal_domain_id", "")).strip() == "time.proper"
    ]
    violations: List[str] = []
    rows_by_scope: Dict[str, List[dict]] = {}
    for row in relevant_rows:
        scope_id = str(row.get("scope_id", "")).strip() or "global"
        rows_by_scope.setdefault(scope_id, []).append(dict(row))
    for scope_id in sorted(rows_by_scope.keys()):
        previous = None
        for row in sorted(
            rows_by_scope[scope_id],
            key=lambda item: int(max(0, _as_int(item.get("canonical_tick", 0), 0))),
        ):
            value = int(_as_int(row.get("domain_time_value", 0), 0))
            if (previous is not None) and (value < previous):
                violations.append("proper-time decreased for scope_id='{}'".format(scope_id))
                break
            previous = int(value)
    return violations


def _schedule_consistency_violations(payload: Mapping[str, object]) -> List[str]:
    rows = _normalize_schedule_domain_evaluations(payload.get("schedule_domain_evaluations") or [])
    violations: List[str] = []
    for row in rows:
        if not bool(row.get("due", False)):
            continue
        domain_value = int(_as_int(row.get("domain_time_value", -1), -1))
        target_value = int(max(0, _as_int(row.get("target_time_value", 0), 0)))
        if domain_value < target_value:
            violations.append(
                "due schedule has domain_time_value < target_time_value for schedule_id='{}'".format(
                    str(row.get("schedule_id", "")).strip()
                )
            )
    return violations


def verify_time_replay_window(*, state_payload: Mapping[str, object], expected_payload: Mapping[str, object] | None = None) -> dict:
    observed = _hash_chains(state_payload)
    report = {
        "result": "complete",
        "violations": [],
        "observed": dict(observed),
        "recorded": {
            "time_mapping_hash_chain": str(state_payload.get("time_mapping_hash_chain", "")).strip().lower(),
            "schedule_domain_evaluation_hash": str(state_payload.get("schedule_domain_evaluation_hash", "")).strip().lower(),
            "time_stamp_hash_chain": str(state_payload.get("time_stamp_hash_chain", "")).strip().lower(),
            "proper_time_hash_chain": str(state_payload.get("proper_time_hash_chain", "")).strip().lower(),
            "time_adjust_event_hash_chain": str(state_payload.get("time_adjust_event_hash_chain", "")).strip().lower(),
            "drift_policy_id": str(state_payload.get("drift_policy_id", "")).strip() or "drift.none",
        },
        "deterministic_fingerprint": "",
    }

    for key in (
        "time_mapping_hash_chain",
        "schedule_domain_evaluation_hash",
        "time_stamp_hash_chain",
        "proper_time_hash_chain",
        "time_adjust_event_hash_chain",
    ):
        recorded = str(report["recorded"][key]).strip().lower()
        observed_value = str(observed[key]).strip().lower()
        if recorded and recorded != observed_value:
            report["violations"].append("recorded {} does not match replay hash".format(key))
    if str(report["recorded"]["drift_policy_id"]).strip() != str(observed.get("drift_policy_id", "")).strip():
        report["violations"].append("recorded drift_policy_id does not match replay value")

    report["violations"].extend(_proper_time_monotonic_violations(state_payload))
    report["violations"].extend(_schedule_consistency_violations(state_payload))

    if expected_payload:
        expected = _hash_chains(dict(expected_payload))
        report["expected"] = dict(expected)
        for key in (
            "time_mapping_hash_chain",
            "schedule_domain_evaluation_hash",
            "time_stamp_hash_chain",
            "proper_time_hash_chain",
            "time_adjust_event_hash_chain",
        ):
            if str(expected[key]).strip().lower() != str(observed[key]).strip().lower():
                report["violations"].append("{} mismatch against expected replay baseline".format(key))
        if str(expected.get("drift_policy_id", "")).strip() != str(observed.get("drift_policy_id", "")).strip():
            report["violations"].append("drift_policy_id mismatch against expected replay baseline")

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify replay-window determinism for TEMP-1 time hash chains.")
    parser.add_argument("--state-path", default="", help="JSON payload path containing time mapping/schedule state.")
    parser.add_argument("--expected-state-path", default="", help="Optional second payload for replay equality checks.")
    args = parser.parse_args()

    state_path = str(args.state_path or "").strip()
    if not state_path:
        print(
            json.dumps(
                {
                    "result": "refusal",
                    "reason_code": "refusal.time.state_path_required",
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
                    "reason_code": "refusal.time.state_payload_invalid",
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
                        "reason_code": "refusal.time.expected_payload_invalid",
                        "message": expected_error,
                        "expected_state_path": os.path.normpath(os.path.abspath(expected_path)),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2

    report = verify_time_replay_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
