#!/usr/bin/env python3
"""Verify SYS-7 system forensics explain determinism over a state window."""

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

from src.system import (  # noqa: E402
    evaluate_system_explain_request,
    normalize_system_explain_artifact_rows,
    normalize_system_explain_request_rows,
)
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


def _sorted_tokens(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _requester_policy_id(request_row: Mapping[str, object]) -> str:
    ext = _as_map(request_row.get("extensions"))
    explicit = str(ext.get("requester_policy_id", "")).strip()
    if explicit:
        return explicit
    requester = str(request_row.get("requester_subject_id", "")).strip().lower()
    if "admin" in requester:
        return "policy.epistemic.admin"
    if "inspect" in requester:
        return "policy.epistemic.inspector"
    return "policy.epistemic.diegetic"


def _truth_hash_anchor(state: Mapping[str, object], request_row: Mapping[str, object]) -> str:
    ext = _as_map(request_row.get("extensions"))
    explicit = str(ext.get("truth_hash_anchor", "")).strip()
    if explicit:
        return explicit
    return str(
        str(state.get("system_failure_event_hash_chain", "")).strip()
        or str(state.get("system_forced_expand_event_hash_chain", "")).strip()
        or str(state.get("system_certificate_revocation_hash_chain", "")).strip()
        or str(state.get("system_macro_output_record_hash_chain", "")).strip()
        or str(state.get("system_health_hash_chain", "")).strip()
    ).strip()


def _domain_fault_rows(state: Mapping[str, object]) -> list[dict]:
    rows: list[dict] = []
    for key in (
        "fault_states",
        "thermal_fire_events",
        "pollution_health_risk_event_rows",
        "pollution_compliance_report_rows",
    ):
        rows.extend(
            dict(row)
            for row in list(state.get(key) or [])
            if isinstance(row, Mapping)
        )
    return rows


def _normalize_cache_rows(rows: object) -> list[dict]:
    if not isinstance(rows, list):
        rows = []
    normalized = []
    for item in rows:
        if not isinstance(item, Mapping):
            continue
        row = dict(item)
        cache_key = str(row.get("cache_key", "")).strip()
        if not cache_key:
            continue
        artifact = _as_map(row.get("artifact"))
        normalized.append(
            {
                "cache_key": cache_key,
                "system_id": str(row.get("system_id", "")).strip(),
                "event_id": (
                    None
                    if row.get("event_id") is None
                    else str(row.get("event_id", "")).strip() or None
                ),
                "truth_hash_anchor": str(row.get("truth_hash_anchor", "")).strip(),
                "requester_policy_id": str(row.get("requester_policy_id", "")).strip(),
                "artifact": artifact,
            }
        )
    return sorted(
        normalized,
        key=lambda row: (
            str(row.get("cache_key", "")),
            str(row.get("system_id", "")),
            str(row.get("event_id", "")),
        ),
    )


def _system_explain_hash(state: Mapping[str, object]) -> str:
    rows = normalize_system_explain_artifact_rows(state.get("system_explain_artifact_rows") or [])
    return canonical_sha256(
        [
            {
                "explain_id": str(row.get("explain_id", "")).strip(),
                "system_id": str(row.get("system_id", "")).strip(),
                "explain_level": str(row.get("explain_level", "")).strip(),
                "primary_cause": str(row.get("primary_cause", "")).strip(),
                "epistemic_redaction_level": str(row.get("epistemic_redaction_level", "")).strip(),
            }
            for row in sorted(
                (dict(item) for item in rows if isinstance(item, Mapping)),
                key=lambda item: (
                    str(item.get("system_id", "")),
                    str(item.get("explain_level", "")),
                    str(item.get("explain_id", "")),
                ),
            )
        ]
    )


def _system_explain_cache_hash(state: Mapping[str, object]) -> str:
    rows = _normalize_cache_rows(state.get("system_explain_cache_rows") or [])
    return canonical_sha256(
        [
            {
                "cache_key": str(row.get("cache_key", "")).strip(),
                "system_id": str(row.get("system_id", "")).strip(),
                "event_id": str(row.get("event_id", "")).strip(),
                "truth_hash_anchor": str(row.get("truth_hash_anchor", "")).strip(),
                "requester_policy_id": str(row.get("requester_policy_id", "")).strip(),
                "artifact_id": str(_as_map(row.get("artifact")).get("explain_id", "")).strip(),
            }
            for row in rows
        ]
    )


def _observed_hashes(state: Mapping[str, object]) -> dict:
    return {
        "system_explain_hash_chain": _system_explain_hash(state),
        "system_explain_cache_hash_chain": _system_explain_cache_hash(state),
    }


def verify_explain_determinism(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
    request_id: str = "",
) -> dict:
    state = _state_payload(state_payload)
    tick_value = int(max(0, _as_int(state.get("current_tick", 0), 0)))
    request_rows = normalize_system_explain_request_rows(state.get("system_explain_request_rows") or [])
    requested_id = str(request_id or "").strip()
    selected_request = {}
    for row in request_rows:
        request_token = str(dict(row).get("request_id", "")).strip()
        if not request_token:
            continue
        if requested_id and (request_token != requested_id):
            continue
        selected_request = dict(row)
        break

    report = {
        "result": "complete",
        "violations": [],
        "selected_request_id": str(selected_request.get("request_id", "")).strip(),
        "observed": dict(_observed_hashes(state)),
        "recorded": {
            "system_explain_hash_chain": str(state.get("system_explain_hash_chain", "")).strip().lower(),
            "system_explain_cache_hash_chain": str(
                state.get("system_explain_cache_hash_chain", "")
            ).strip().lower(),
        },
        "evaluation": {},
        "deterministic_fingerprint": "",
    }
    for key in ("system_explain_hash_chain", "system_explain_cache_hash_chain"):
        recorded = str(report["recorded"][key]).strip().lower()
        observed = str(report["observed"][key]).strip().lower()
        if recorded and (recorded != observed):
            report["violations"].append("recorded {} does not match replay hash".format(key))

    if not selected_request:
        report["violations"].append("system_explain_request_rows is empty or request_id not found")
    else:
        policy_id = _requester_policy_id(selected_request)
        truth_hash_anchor = _truth_hash_anchor(state, selected_request)
        domain_fault_rows = _domain_fault_rows(state)
        eval_one = evaluate_system_explain_request(
            current_tick=tick_value,
            system_explain_request=selected_request,
            system_rows=state.get("system_rows") or [],
            system_macro_capsule_rows=state.get("system_macro_capsule_rows") or [],
            system_failure_event_rows=state.get("system_failure_event_rows") or [],
            system_forced_expand_event_rows=state.get("system_forced_expand_event_rows") or [],
            system_certificate_revocation_rows=state.get("system_certificate_revocation_rows") or [],
            system_certification_result_rows=state.get("system_certification_result_rows") or [],
            safety_event_rows=state.get("safety_events") or [],
            energy_ledger_entry_rows=state.get("energy_ledger_entries") or [],
            model_hazard_rows=state.get("model_hazard_rows") or [],
            spec_compliance_result_rows=state.get("spec_compliance_results") or [],
            system_macro_output_record_rows=state.get("system_macro_output_record_rows") or [],
            system_macro_runtime_state_rows=state.get("system_macro_runtime_state_rows") or [],
            domain_fault_rows=domain_fault_rows,
            existing_cache_rows=[],
            truth_hash_anchor=truth_hash_anchor,
            requester_policy_id=policy_id,
            max_cause_entries=int(max(1, _as_int(state.get("system_forensics_max_cause_entries", 16), 16))),
        )
        eval_two = evaluate_system_explain_request(
            current_tick=tick_value,
            system_explain_request=selected_request,
            system_rows=state.get("system_rows") or [],
            system_macro_capsule_rows=state.get("system_macro_capsule_rows") or [],
            system_failure_event_rows=state.get("system_failure_event_rows") or [],
            system_forced_expand_event_rows=state.get("system_forced_expand_event_rows") or [],
            system_certificate_revocation_rows=state.get("system_certificate_revocation_rows") or [],
            system_certification_result_rows=state.get("system_certification_result_rows") or [],
            safety_event_rows=state.get("safety_events") or [],
            energy_ledger_entry_rows=state.get("energy_ledger_entries") or [],
            model_hazard_rows=state.get("model_hazard_rows") or [],
            spec_compliance_result_rows=state.get("spec_compliance_results") or [],
            system_macro_output_record_rows=state.get("system_macro_output_record_rows") or [],
            system_macro_runtime_state_rows=state.get("system_macro_runtime_state_rows") or [],
            domain_fault_rows=domain_fault_rows,
            existing_cache_rows=list(eval_one.get("cache_rows") or []),
            truth_hash_anchor=truth_hash_anchor,
            requester_policy_id=policy_id,
            max_cause_entries=int(max(1, _as_int(state.get("system_forensics_max_cause_entries", 16), 16))),
        )
        artifact_one = _as_map(eval_one.get("artifact_row"))
        artifact_two = _as_map(eval_two.get("artifact_row"))
        report["evaluation"] = {
            "first_result": str(eval_one.get("result", "")).strip(),
            "second_result": str(eval_two.get("result", "")).strip(),
            "first_cache_hit": bool(eval_one.get("cache_hit", False)),
            "second_cache_hit": bool(eval_two.get("cache_hit", False)),
            "first_explain_id": str(artifact_one.get("explain_id", "")).strip(),
            "second_explain_id": str(artifact_two.get("explain_id", "")).strip(),
            "first_fingerprint": str(artifact_one.get("deterministic_fingerprint", "")).strip(),
            "second_fingerprint": str(artifact_two.get("deterministic_fingerprint", "")).strip(),
            "selected_policy_id": policy_id,
            "truth_hash_anchor": truth_hash_anchor,
        }
        if str(eval_one.get("result", "")).strip() != "complete":
            report["violations"].append("first explain evaluation did not complete")
        if str(eval_two.get("result", "")).strip() != "complete":
            report["violations"].append("second explain evaluation did not complete")
        if not artifact_one or not artifact_two:
            report["violations"].append("explain artifact row missing from evaluation output")
        else:
            if str(artifact_one.get("explain_id", "")).strip() != str(
                artifact_two.get("explain_id", "")
            ).strip():
                report["violations"].append("explain_id drifted across equivalent evaluations")
            if str(artifact_one.get("deterministic_fingerprint", "")).strip().lower() != str(
                artifact_two.get("deterministic_fingerprint", "")
            ).strip().lower():
                report["violations"].append("artifact deterministic_fingerprint drifted across equivalent evaluations")
        if bool(eval_two.get("cache_hit", False)) is not True:
            report["violations"].append("second explain evaluation must be a cache hit")

        stored_artifacts = normalize_system_explain_artifact_rows(state.get("system_explain_artifact_rows") or [])
        matched = {}
        for row in stored_artifacts:
            if not isinstance(row, Mapping):
                continue
            ext = _as_map(dict(row).get("extensions"))
            if str(ext.get("request_id", "")).strip() != str(selected_request.get("request_id", "")).strip():
                continue
            matched = dict(row)
            break
        report["evaluation"]["stored_artifact_explain_id"] = str(matched.get("explain_id", "")).strip()
        if matched:
            if str(matched.get("explain_id", "")).strip() != str(artifact_two.get("explain_id", "")).strip():
                report["violations"].append("stored explain artifact explain_id mismatch against replay evaluation")

    if expected_payload:
        expected_state = _state_payload(expected_payload)
        expected = _observed_hashes(expected_state)
        report["expected"] = dict(expected)
        for key in ("system_explain_hash_chain", "system_explain_cache_hash_chain"):
            if str(expected[key]).strip().lower() != str(report["observed"][key]).strip().lower():
                report["violations"].append("{} mismatch against expected replay baseline".format(key))

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify deterministic explain outputs for SYS-7 system forensics windows."
    )
    parser.add_argument("--state-path", default="build/system/sys7_forensics_report.json")
    parser.add_argument("--expected-state-path", default="")
    parser.add_argument("--request-id", default="")
    args = parser.parse_args()

    state_path = os.path.normpath(os.path.abspath(str(args.state_path)))
    state_payload, state_err = _read_json(state_path)
    if state_err:
        print(
            json.dumps(
                {
                    "result": "error",
                    "reason": "state_read_failed",
                    "state_path": state_path,
                    "details": state_err,
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
        loaded_expected, expected_err = _read_json(expected_abs)
        if expected_err:
            print(
                json.dumps(
                    {
                        "result": "error",
                        "reason": "expected_state_read_failed",
                        "expected_state_path": expected_abs,
                        "details": expected_err,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2
        expected_payload = loaded_expected

    report = verify_explain_determinism(
        state_payload=state_payload,
        expected_payload=expected_payload,
        request_id=str(args.request_id or "").strip(),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if str(report.get("result", "")).strip() != "complete":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
