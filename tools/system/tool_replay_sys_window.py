#!/usr/bin/env python3
"""Verify SYS-8 replay windows reproduce deterministic SYS proof hash chains."""

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

from tools.system.tool_replay_capsule_window import verify_capsule_replay_window  # noqa: E402
from tools.system.tool_replay_certification_window import verify_certification_replay_window  # noqa: E402
from tools.system.tool_replay_system_failure_window import verify_system_failure_replay_window  # noqa: E402
from tools.system.tool_replay_tier_transitions import verify_tier_transition_replay_window  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


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


def _certification_hash_from_report(report: Mapping[str, object]) -> str:
    observed = _as_map(report.get("observed"))
    return canonical_sha256(
        {
            "system_certification_result_hash_chain": str(observed.get("system_certification_result_hash_chain", "")).strip(),
            "system_certificate_artifact_hash_chain": str(observed.get("system_certificate_artifact_hash_chain", "")).strip(),
            "system_certificate_revocation_hash_chain": str(observed.get("system_certificate_revocation_hash_chain", "")).strip(),
        }
    )


def _observed_hashes(state_payload: Mapping[str, object]) -> dict:
    tier_report = verify_tier_transition_replay_window(state_payload=state_payload, expected_payload=None)
    capsule_report = verify_capsule_replay_window(state_payload=state_payload, expected_payload=None)
    reliability_report = verify_system_failure_replay_window(state_payload=state_payload, expected_payload=None)
    certification_report = verify_certification_replay_window(state_payload=state_payload, expected_payload=None)

    tier_observed = _as_map(tier_report.get("observed"))
    capsule_observed = _as_map(capsule_report.get("observed"))
    reliability_observed = _as_map(reliability_report.get("observed"))
    certification_observed = _as_map(certification_report.get("observed"))

    return {
        "system_collapse_expand_hash_chain": str(tier_observed.get("collapse_expand_event_hash_chain", "")).strip(),
        "macro_output_record_hash_chain": str(capsule_observed.get("system_macro_output_record_hash_chain", "")).strip(),
        "forced_expand_event_hash_chain": str(capsule_observed.get("system_forced_expand_event_hash_chain", "")).strip()
        or str(reliability_observed.get("system_forced_expand_event_hash_chain", "")).strip(),
        "certification_hash_chain": _certification_hash_from_report(certification_report),
        "system_health_hash_chain": str(reliability_observed.get("system_health_hash_chain", "")).strip(),
        "subreports": {
            "tier": dict(tier_report),
            "capsule": dict(capsule_report),
            "reliability": dict(reliability_report),
            "certification": dict(certification_report),
        },
        "certification_observed": dict(certification_observed),
    }


def verify_sys_replay_window(
    *,
    state_payload: Mapping[str, object],
    expected_payload: Mapping[str, object] | None = None,
) -> dict:
    state = _state_payload(state_payload)
    observed = _observed_hashes(state)
    recorded = {
        "system_collapse_expand_hash_chain": str(
            state.get("system_collapse_expand_hash_chain", state.get("collapse_expand_event_hash_chain", ""))
        )
        .strip()
        .lower(),
        "macro_output_record_hash_chain": str(
            state.get("macro_output_record_hash_chain", state.get("system_macro_output_record_hash_chain", ""))
        )
        .strip()
        .lower(),
        "forced_expand_event_hash_chain": str(
            state.get("forced_expand_event_hash_chain", state.get("system_forced_expand_event_hash_chain", ""))
        )
        .strip()
        .lower(),
        "certification_hash_chain": str(
            state.get(
                "certification_hash_chain",
                canonical_sha256(
                    {
                        "system_certification_result_hash_chain": str(state.get("system_certification_result_hash_chain", "")).strip(),
                        "system_certificate_artifact_hash_chain": str(state.get("system_certificate_artifact_hash_chain", "")).strip(),
                        "system_certificate_revocation_hash_chain": str(state.get("system_certificate_revocation_hash_chain", "")).strip(),
                    }
                ),
            )
        )
        .strip()
        .lower(),
        "system_health_hash_chain": str(state.get("system_health_hash_chain", "")).strip().lower(),
    }

    report = {
        "result": "complete",
        "violations": [],
        "observed": {
            "system_collapse_expand_hash_chain": str(observed.get("system_collapse_expand_hash_chain", "")).strip(),
            "macro_output_record_hash_chain": str(observed.get("macro_output_record_hash_chain", "")).strip(),
            "forced_expand_event_hash_chain": str(observed.get("forced_expand_event_hash_chain", "")).strip(),
            "certification_hash_chain": str(observed.get("certification_hash_chain", "")).strip(),
            "system_health_hash_chain": str(observed.get("system_health_hash_chain", "")).strip(),
        },
        "recorded": dict(recorded),
        "subreports": dict(_as_map(observed.get("subreports"))),
        "deterministic_fingerprint": "",
    }

    for key in (
        "system_collapse_expand_hash_chain",
        "macro_output_record_hash_chain",
        "forced_expand_event_hash_chain",
        "certification_hash_chain",
        "system_health_hash_chain",
    ):
        observed_value = str(_as_map(report.get("observed")).get(key, "")).strip().lower()
        recorded_value = str(recorded.get(key, "")).strip().lower()
        if recorded_value and (recorded_value != observed_value):
            report["violations"].append("recorded {} does not match replay hash".format(key))

    if expected_payload:
        expected_state = _state_payload(expected_payload)
        expected = _observed_hashes(expected_state)
        report["expected"] = {
            "system_collapse_expand_hash_chain": str(expected.get("system_collapse_expand_hash_chain", "")).strip(),
            "macro_output_record_hash_chain": str(expected.get("macro_output_record_hash_chain", "")).strip(),
            "forced_expand_event_hash_chain": str(expected.get("forced_expand_event_hash_chain", "")).strip(),
            "certification_hash_chain": str(expected.get("certification_hash_chain", "")).strip(),
            "system_health_hash_chain": str(expected.get("system_health_hash_chain", "")).strip(),
        }
        for key in (
            "system_collapse_expand_hash_chain",
            "macro_output_record_hash_chain",
            "forced_expand_event_hash_chain",
            "certification_hash_chain",
            "system_health_hash_chain",
        ):
            expected_value = str(_as_map(report.get("expected")).get(key, "")).strip().lower()
            observed_value = str(_as_map(report.get("observed")).get(key, "")).strip().lower()
            if expected_value != observed_value:
                report["violations"].append("{} mismatch against expected replay baseline".format(key))

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify deterministic replay hashes for SYS-8 stress windows.")
    parser.add_argument("--state-path", default="build/system/sys8_stress_report.json")
    parser.add_argument("--expected-state-path", default="")
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

    report = verify_sys_replay_window(state_payload=state_payload, expected_payload=expected_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())

