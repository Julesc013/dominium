#!/usr/bin/env python3
"""Verify TEMP-2 deterministic synchronization behavior using process.time_adjust."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.sessionx.process_runtime import execute_intent  # noqa: E402

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _fixture_state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0},
        "camera": {
            "frame_id": "frame.test",
            "position_mm": {"x": 0, "y": 0, "z": 0},
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
        },
    }


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.tool.time.sync",
        "allowed_processes": ["process.time_adjust"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {"process.time_adjust": "session.boot"},
        "process_privilege_requirements": {"process.time_adjust": "observer"},
        "allowed_lenses": ["lens.nondiegetic.debug"],
        "epistemic_limits": {"max_view_radius_km": 1_000_000, "allow_hidden_state_access": True},
        "epistemic_policy_id": "ep.policy.lab_broad",
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "peer_id": "peer.tool.time.sync",
        "experience_id": "profile.tool.time.sync",
        "law_profile_id": "law.tool.time.sync",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "scope.tool.time.sync", "visibility_level": "nondiegetic"},
        "privilege_level": "observer",
    }


def _run_once(
    *,
    sync_policy_id: str,
    temporal_domain_id: str,
    target_id: str,
    local_domain_time: int,
    remote_domain_time: int,
    max_adjust_per_tick: int,
    max_skew_allowed: int,
) -> dict:
    state = _fixture_state()
    intent = {
        "intent_id": "intent.tool.time.sync.001",
        "process_id": "process.time_adjust",
        "inputs": {
            "sync_policy_id": str(sync_policy_id),
            "temporal_domain_id": str(temporal_domain_id),
            "target_id": str(target_id),
            "local_domain_time": int(local_domain_time),
            "remote_domain_time": int(remote_domain_time),
            "max_adjust_per_tick": int(max_adjust_per_tick),
            "max_skew_allowed": int(max_skew_allowed),
            "originating_receipt_id": "receipt.sync.tool.001",
        },
    }
    result = execute_intent(
        state=state,
        intent=intent,
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        navigation_indices={},
        policy_context={},
    )
    return {
        "result": dict(result or {}),
        "state": dict(state or {}),
    }


def verify_sync_consistency(
    *,
    sync_policy_id: str,
    temporal_domain_id: str,
    target_id: str,
    local_domain_time: int,
    remote_domain_time: int,
    max_adjust_per_tick: int,
    max_skew_allowed: int,
) -> dict:
    first = _run_once(
        sync_policy_id=sync_policy_id,
        temporal_domain_id=temporal_domain_id,
        target_id=target_id,
        local_domain_time=local_domain_time,
        remote_domain_time=remote_domain_time,
        max_adjust_per_tick=max_adjust_per_tick,
        max_skew_allowed=max_skew_allowed,
    )
    second = _run_once(
        sync_policy_id=sync_policy_id,
        temporal_domain_id=temporal_domain_id,
        target_id=target_id,
        local_domain_time=local_domain_time,
        remote_domain_time=remote_domain_time,
        max_adjust_per_tick=max_adjust_per_tick,
        max_skew_allowed=max_skew_allowed,
    )

    report = {
        "result": "complete",
        "violations": [],
        "sync_policy_id": str(sync_policy_id),
        "temporal_domain_id": str(temporal_domain_id),
        "target_id": str(target_id),
        "deterministic_fingerprint": "",
        "first": {
            "process_result": str((first["result"]).get("result", "")),
            "metadata": dict((first["result"]).get("metadata") or {}),
            "time_adjust_event_hash_chain": str((first["state"]).get("time_adjust_event_hash_chain", "")).strip().lower(),
        },
        "second": {
            "process_result": str((second["result"]).get("result", "")),
            "metadata": dict((second["result"]).get("metadata") or {}),
            "time_adjust_event_hash_chain": str((second["state"]).get("time_adjust_event_hash_chain", "")).strip().lower(),
        },
    }

    if report["first"]["process_result"] != "complete":
        report["violations"].append("first sync execution did not complete")
    if report["second"]["process_result"] != "complete":
        report["violations"].append("second sync execution did not complete")

    hash_a = str(report["first"]["time_adjust_event_hash_chain"]).strip().lower()
    hash_b = str(report["second"]["time_adjust_event_hash_chain"]).strip().lower()
    if (not _HASH64.fullmatch(hash_a)) or (not _HASH64.fullmatch(hash_b)):
        report["violations"].append("time_adjust_event_hash_chain missing or invalid")
    elif hash_a != hash_b:
        report["violations"].append("time_adjust_event_hash_chain drifted across equivalent runs")

    metadata_a = dict(report["first"]["metadata"] or {})
    metadata_b = dict(report["second"]["metadata"] or {})
    if metadata_a != metadata_b:
        report["violations"].append("sync metadata drifted across equivalent runs")

    if report["violations"]:
        report["result"] = "violation"
    report["deterministic_fingerprint"] = json.dumps(
        {
            "result": report["result"],
            "violations": list(report["violations"]),
            "hash_a": hash_a,
            "hash_b": hash_b,
            "metadata_a": metadata_a,
            "metadata_b": metadata_b,
        },
        sort_keys=True,
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify deterministic sync correction behavior for TEMP-2.")
    parser.add_argument("--sync-policy-id", default="sync.adjust_on_receipt")
    parser.add_argument("--temporal-domain-id", default="time.civil")
    parser.add_argument("--target-id", default="session.default")
    parser.add_argument("--local-domain-time", type=int, default=100)
    parser.add_argument("--remote-domain-time", type=int, default=130)
    parser.add_argument("--max-adjust-per-tick", type=int, default=5)
    parser.add_argument("--max-skew-allowed", type=int, default=30)
    args = parser.parse_args()

    report = verify_sync_consistency(
        sync_policy_id=str(args.sync_policy_id),
        temporal_domain_id=str(args.temporal_domain_id),
        target_id=str(args.target_id),
        local_domain_time=int(args.local_domain_time),
        remote_domain_time=int(args.remote_domain_time),
        max_adjust_per_tick=int(args.max_adjust_per_tick),
        max_skew_allowed=int(args.max_skew_allowed),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
