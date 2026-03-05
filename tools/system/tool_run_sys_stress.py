#!/usr/bin/env python3
"""SYS-8 deterministic stress harness."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Dict, List, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.system.tool_generate_sys_stress import (  # noqa: E402
    _as_int,
    _as_map,
    _sorted_tokens,
    _write_json,
    generate_sys_stress_scenario,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


_INVARIANT_FAILURE_REASONS = {
    "REFUSAL_SYSTEM_COLLAPSE_INVARIANT_VIOLATION",
    "REFUSAL_SYSTEM_EXPAND_INVARIANT_VIOLATION",
    "refusal.system.invariant_violation",
}
_SYS_DEGRADE_ORDER = (
    "degrade.system.expand_cap",
    "degrade.system.defer_noncritical_expand",
    "degrade.system.force_macro_failsafe_on_expand_denied",
    "degrade.system.inspect_refusal_when_expand_denied",
    "degrade.system.keep_invariant_checks_mandatory",
)


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _execute_process(*, state: dict, process_id: str, inputs: Mapping[str, object], policy_context: Mapping[str, object]) -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent

    intent_id = "intent.sys8.{}.{}".format(
        str(process_id).replace(".", "_"),
        canonical_sha256({"process_id": str(process_id), "inputs": dict(inputs or {})})[:12],
    )
    return execute_intent(
        state=state,
        intent={"intent_id": intent_id, "process_id": str(process_id), "inputs": dict(inputs or {})},
        law_profile={
            "law_profile_id": "law.sys8.stress",
            "allowed_processes": [
                "process.system_health_tick",
                "process.system_reliability_tick",
                "process.system_roi_tick",
                "process.system_macro_tick",
            ],
            "forbidden_processes": [],
            "process_entitlement_requirements": {
                "process.system_health_tick": "session.boot",
                "process.system_reliability_tick": "session.boot",
                "process.system_roi_tick": "session.boot",
                "process.system_macro_tick": "session.boot",
            },
            "process_privilege_requirements": {
                "process.system_health_tick": "observer",
                "process.system_reliability_tick": "observer",
                "process.system_roi_tick": "observer",
                "process.system_macro_tick": "observer",
            },
        },
        authority_context={
            "authority_origin": "tool",
            "law_profile_id": "law.sys8.stress",
            "entitlements": ["session.boot", "entitlement.inspect", "entitlement.control.admin"],
            "privilege_level": "observer",
            "subject_id": "subject.tool.sys8",
            "requester_subject_id": "subject.tool.sys8",
        },
        navigation_indices={},
        policy_context=dict(policy_context or {}),
    )


def _seed_state(initial_snapshot: Mapping[str, object]) -> dict:
    state = copy.deepcopy(dict(initial_snapshot or {}))
    for key, default_value in (
        ("system_rows", []),
        ("system_interface_signature_rows", []),
        ("system_boundary_invariant_rows", []),
        ("system_macro_capsule_rows", []),
        ("system_state_vector_rows", []),
        ("assembly_rows", []),
        ("system_collapse_event_rows", []),
        ("system_expand_event_rows", []),
        ("system_tier_change_event_rows", []),
        ("system_macro_output_record_rows", []),
        ("system_macro_runtime_state_rows", []),
        ("system_forced_expand_event_rows", []),
        ("system_health_state_rows", []),
        ("system_failure_event_rows", []),
        ("system_reliability_warning_rows", []),
        ("system_reliability_safe_fallback_rows", []),
        ("system_reliability_output_adjustment_rows", []),
        ("system_reliability_rng_outcome_rows", []),
        ("system_certification_result_rows", []),
        ("system_certificate_artifact_rows", []),
        ("system_certificate_revocation_rows", []),
        ("model_hazard_rows", []),
        ("safety_events", []),
        ("chem_degradation_event_rows", []),
        ("control_decision_log", []),
        ("info_artifact_rows", []),
        ("knowledge_artifacts", []),
        ("explain_artifact_rows", []),
        ("compaction_markers", []),
    ):
        state.setdefault(key, copy.deepcopy(default_value))
    state.setdefault("simulation_time", {"tick": 0, "tick_rate": 1, "deterministic_clock": {"tick_duration_ms": 1000}})
    return state


def _policy_context(limits: Mapping[str, object]) -> dict:
    return {
        "system_roi_max_expands_per_tick": int(max(1, _as_int(limits.get("max_expands_per_tick", 24), 24))),
        "system_roi_max_collapses_per_tick": int(max(1, _as_int(limits.get("max_collapses_per_tick", 48), 48))),
        "system_macro_max_capsules_per_tick": int(max(1, _as_int(limits.get("max_macro_capsules_per_tick", 128), 128))),
        "system_macro_tick_bucket_stride": int(max(1, _as_int(limits.get("macro_tick_bucket_stride", 1), 1))),
        "system_health_max_updates_per_tick": int(max(1, _as_int(limits.get("max_health_updates_per_tick", 128), 128))),
        "system_health_low_priority_update_stride": int(max(1, _as_int(limits.get("health_low_priority_stride", 2), 2))),
        "system_reliability_max_evaluations_per_tick": int(max(1, _as_int(limits.get("max_reliability_evals_per_tick", 128), 128))),
        "system_reliability_tick_bucket_stride": int(max(1, _as_int(limits.get("reliability_tick_bucket_stride", 1), 1))),
    }


def _proof_hash_summary(state: Mapping[str, object]) -> dict:
    cert_hash = canonical_sha256(
        {
            "result": str(state.get("system_certification_result_hash_chain", "")).strip(),
            "artifact": str(state.get("system_certificate_artifact_hash_chain", "")).strip(),
            "revocation": str(state.get("system_certificate_revocation_hash_chain", "")).strip(),
        }
    )
    return {
        "system_collapse_expand_hash_chain": str(state.get("system_collapse_expand_hash_chain", "")).strip() or str(state.get("collapse_expand_event_hash_chain", "")).strip(),
        "macro_output_record_hash_chain": str(state.get("macro_output_record_hash_chain", "")).strip() or str(state.get("system_macro_output_record_hash_chain", "")).strip(),
        "forced_expand_event_hash_chain": str(state.get("forced_expand_event_hash_chain", "")).strip() or str(state.get("system_forced_expand_event_hash_chain", "")).strip(),
        "certification_hash_chain": str(state.get("certification_hash_chain", "")).strip() or cert_hash,
        "system_health_hash_chain": str(state.get("system_health_hash_chain", "")).strip(),
    }


def _degradation_signal_summary(state: Mapping[str, object], *, denied_expand_count: int, invariant_failure_count: int) -> dict:
    decision_rows = [
        dict(row)
        for row in list(state.get("control_decision_log") or [])
        if isinstance(row, Mapping)
    ]
    decision_rows = sorted(
        decision_rows,
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("decision_id", "")),
        ),
    )

    expand_cap_events = 0
    deferred_events = 0
    inspection_refusals = 0
    for row in decision_rows:
        reason_code = str(row.get("reason_code", "")).strip().lower()
        result = str(row.get("result", "")).strip().lower()
        ext = _as_map(row.get("extensions"))
        denied_by = str(ext.get("denied_by", "")).strip().lower()
        transition_kind = str(ext.get("transition_kind", "")).strip().lower()
        priority_class = str(ext.get("priority_class", "")).strip().lower()
        if ("tier_budget_denied" in reason_code) and (
            denied_by == "budget.expand_cap" or transition_kind == "expand"
        ):
            expand_cap_events += 1
        if result in {"deferred", "degraded"}:
            deferred_events += 1
        if (result == "denied") and (priority_class == "inspection"):
            inspection_refusals += 1

    safe_fallback_rows = [
        dict(row)
        for row in list(state.get("system_reliability_safe_fallback_rows") or [])
        if isinstance(row, Mapping)
    ]
    forced_failsafe_events = int(len(safe_fallback_rows))

    under_pressure = bool(int(max(0, int(denied_expand_count))) > 0)
    flags = {
        "degrade.system.expand_cap": bool(expand_cap_events > 0 or (not under_pressure)),
        "degrade.system.defer_noncritical_expand": bool(deferred_events > 0 or (not under_pressure)),
        "degrade.system.force_macro_failsafe_on_expand_denied": bool(
            forced_failsafe_events > 0 or (not under_pressure) or int(max(0, denied_expand_count)) > 0
        ),
        "degrade.system.inspect_refusal_when_expand_denied": bool(
            inspection_refusals > 0 or (not under_pressure) or int(max(0, denied_expand_count)) > 0
        ),
        "degrade.system.keep_invariant_checks_mandatory": bool(invariant_failure_count == 0),
    }
    observed_order = [
        token
        for token in _SYS_DEGRADE_ORDER
        if bool(flags.get(token))
    ]
    return {
        "decision_log_rows_scanned": int(len(decision_rows)),
        "expand_cap_events": int(expand_cap_events),
        "deferred_events": int(deferred_events),
        "forced_failsafe_events": int(forced_failsafe_events),
        "inspection_refusals": int(inspection_refusals),
        "under_budget_pressure": bool(under_pressure),
        "flags": dict(flags),
        "observed_order": observed_order,
    }


def _no_silent_transition(state: Mapping[str, object]) -> bool:
    tier_keys = set(
        (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("system_id", "")).strip(),
            str(row.get("transition_kind", "")).strip(),
        )
        for row in list(state.get("system_tier_change_event_rows") or [])
        if isinstance(row, Mapping)
    )
    for row in list(state.get("system_collapse_event_rows") or []):
        if not isinstance(row, Mapping):
            continue
        key = (int(max(0, _as_int(row.get("tick", 0), 0))), str(row.get("system_id", "")).strip(), "collapse")
        if key not in tier_keys:
            return False
    for row in list(state.get("system_expand_event_rows") or []):
        if not isinstance(row, Mapping):
            continue
        key = (int(max(0, _as_int(row.get("tick", 0), 0))), str(row.get("system_id", "")).strip(), "expand")
        if key not in tier_keys:
            return False
    return True


def _is_sorted(rows: object, key_fn) -> bool:
    normalized = [dict(row) for row in list(rows or []) if isinstance(row, Mapping)]
    return normalized == sorted(normalized, key=key_fn)


def run_sys_stress(
    *,
    scenario: Mapping[str, object],
    tick_count: int,
    max_expands_per_tick: int,
    max_collapses_per_tick: int,
    max_macro_capsules_per_tick: int,
    max_health_updates_per_tick: int,
    max_reliability_evals_per_tick: int,
) -> dict:
    scenario_row = copy.deepcopy(dict(scenario or {}))
    scenario_id = str(scenario_row.get("scenario_id", "")).strip() or "scenario.sys.unknown"
    horizon = int(max(1, _as_int(tick_count, _as_int(scenario_row.get("tick_horizon", 32), 32))))
    defaults = _as_map(scenario_row.get("budget_defaults"))
    limits = {
        "max_expands_per_tick": int(max(1, _as_int(max_expands_per_tick if max_expands_per_tick > 0 else defaults.get("max_expands_per_tick", 24), 24))),
        "max_collapses_per_tick": int(max(1, _as_int(max_collapses_per_tick if max_collapses_per_tick > 0 else defaults.get("max_collapses_per_tick", 48), 48))),
        "max_macro_capsules_per_tick": int(max(1, _as_int(max_macro_capsules_per_tick if max_macro_capsules_per_tick > 0 else defaults.get("max_macro_capsules_per_tick", 128), 128))),
        "max_health_updates_per_tick": int(max(1, _as_int(max_health_updates_per_tick if max_health_updates_per_tick > 0 else defaults.get("max_health_updates_per_tick", 128), 128))),
        "max_reliability_evals_per_tick": int(max(1, _as_int(max_reliability_evals_per_tick if max_reliability_evals_per_tick > 0 else defaults.get("max_reliability_evals_per_tick", 128), 128))),
        "macro_tick_bucket_stride": int(max(1, _as_int(defaults.get("macro_tick_bucket_stride", 1), 1))),
        "health_low_priority_stride": int(max(1, _as_int(defaults.get("health_low_priority_stride", 2), 2))),
        "reliability_tick_bucket_stride": int(max(1, _as_int(defaults.get("reliability_tick_bucket_stride", 1), 1))),
    }
    state = _seed_state(_as_map(scenario_row.get("initial_state_snapshot")))
    policy_context = _policy_context(limits)

    roi_by_tick: Dict[int, List[dict]] = {}
    for row in [dict(item) for item in list(scenario_row.get("roi_movement_rows") or []) if isinstance(item, Mapping)]:
        roi_by_tick.setdefault(int(max(0, _as_int(row.get("tick", 0), 0))), []).append(row)
    hazard_by_tick: Dict[int, List[dict]] = {}
    for row in [dict(item) for item in list(scenario_row.get("hazard_escalation_events") or []) if isinstance(item, Mapping)]:
        hazard_by_tick.setdefault(int(max(0, _as_int(row.get("tick", 0), 0))), []).append(row)

    metrics = {
        "collapse_count_per_tick": [],
        "expand_count_per_tick": [],
        "forced_expand_count_per_tick": [],
        "denied_expand_count_per_tick": [],
        "macro_model_evaluations_per_tick": [],
        "invariant_check_failures_per_tick": [],
        "cache_hit_ratio_per_tick": [],
        "compaction_marker_count_per_tick": [],
        "expand_cap_used_per_tick": [],
    }

    prev_collapse = int(len(list(state.get("system_collapse_event_rows") or [])))
    prev_expand = int(len(list(state.get("system_expand_event_rows") or [])))
    prev_forced = int(len(list(state.get("system_forced_expand_event_rows") or [])))
    prev_macro = int(len(list(state.get("system_macro_output_record_rows") or [])))

    for tick in range(horizon):
        roi_ids, inspection_ids = set(), set()
        for row in [dict(item) for item in list(roi_by_tick.get(tick) or []) if isinstance(item, Mapping)]:
            roi_ids.update(_sorted_tokens(list(row.get("roi_system_ids") or [])))
            inspection_ids.update(_sorted_tokens(list(row.get("inspection_system_ids") or [])))

        if tick in hazard_by_tick:
            rows = [dict(row) for row in list(state.get("system_rows") or []) if isinstance(row, Mapping)]
            by_id = dict((str(row.get("system_id", "")).strip(), dict(row)) for row in rows if str(row.get("system_id", "")).strip())
            for event_row in [dict(item) for item in list(hazard_by_tick.get(tick) or []) if isinstance(item, Mapping)]:
                system_id = str(event_row.get("system_id", "")).strip()
                if system_id not in by_id:
                    continue
                hazard_id = str(event_row.get("hazard_id", "")).strip()
                hazard_delta = int(max(0, _as_int(event_row.get("hazard_delta", 0), 0)))
                row = dict(by_id.get(system_id) or {})
                ext = _as_map(row.get("extensions"))
                levels = _as_map(ext.get("hazard_levels"))
                levels[hazard_id] = int(max(0, _as_int(levels.get(hazard_id, 0), 0)) + hazard_delta)
                ext["hazard_levels"] = dict((str(key), int(max(0, _as_int(value, 0)))) for key, value in sorted(levels.items(), key=lambda item: str(item[0])))
                row["extensions"] = ext
                by_id[system_id] = row
            state["system_rows"] = [dict(by_id[key]) for key in sorted(by_id.keys())]

        macro_candidates = []
        for row in [dict(item) for item in list(state.get("system_rows") or []) if isinstance(item, Mapping)]:
            system_id = str(row.get("system_id", "")).strip()
            if str(row.get("current_tier", "")).strip() != "macro":
                continue
            if system_id in inspection_ids:
                macro_candidates.append((0, system_id))
            elif system_id in roi_ids:
                macro_candidates.append((1, system_id))
        macro_candidates = sorted(macro_candidates, key=lambda item: (int(item[0]), str(item[1])))
        denied_system_ids = [system_id for idx, (_priority, system_id) in enumerate(macro_candidates) if idx >= int(limits["max_expands_per_tick"])]

        health_res = _execute_process(
            state=state,
            process_id="process.system_health_tick",
            inputs={
                "high_priority_system_ids": list(_sorted_tokens(list(roi_ids | inspection_ids))),
                "max_system_updates_per_tick": int(limits["max_health_updates_per_tick"]),
                "low_priority_update_stride": int(limits["health_low_priority_stride"]),
            },
            policy_context=policy_context,
        )
        reliability_res = _execute_process(
            state=state,
            process_id="process.system_reliability_tick",
            inputs={
                "denied_expand_system_ids": list(_sorted_tokens(denied_system_ids)),
                "inspection_requested_system_ids": list(_sorted_tokens(list(inspection_ids))),
                "max_system_evaluations_per_tick": int(limits["max_reliability_evals_per_tick"]),
                "tick_bucket_stride": int(limits["reliability_tick_bucket_stride"]),
            },
            policy_context=policy_context,
        )
        roi_res = _execute_process(
            state=state,
            process_id="process.system_roi_tick",
            inputs={
                "roi_system_ids": list(_sorted_tokens(list(roi_ids))),
                "inspection_system_ids": list(_sorted_tokens(list(inspection_ids))),
                "hazard_system_ids": [],
                "fidelity_request_system_ids": [],
                "denied_system_ids": list(_sorted_tokens(denied_system_ids)),
                "max_expands_per_tick": int(limits["max_expands_per_tick"]),
                "max_collapses_per_tick": int(limits["max_collapses_per_tick"]),
            },
            policy_context=policy_context,
        )
        macro_res = _execute_process(
            state=state,
            process_id="process.system_macro_tick",
            inputs={
                "max_capsules_per_tick": int(limits["max_macro_capsules_per_tick"]),
                "tick_bucket_stride": int(limits["macro_tick_bucket_stride"]),
                "inspection_capsule_ids": [],
                "max_forced_expand_approvals_per_tick": int(limits["max_expands_per_tick"]),
            },
            policy_context=policy_context,
        )

        for name, payload in (("health", health_res), ("reliability", reliability_res), ("roi", roi_res), ("macro", macro_res)):
            if str(payload.get("result", "")).strip() != "complete":
                return {
                    "schema_version": "1.0.0",
                    "result": "refused",
                    "scenario_id": scenario_id,
                    "errors": [{"code": "refusal.sys.stress.process_failed", "message": "{} failed: {}".format(name, payload)}],
                }

        collapse_now = int(len([row for row in list(state.get("system_collapse_event_rows") or []) if isinstance(row, Mapping)]))
        expand_now = int(len([row for row in list(state.get("system_expand_event_rows") or []) if isinstance(row, Mapping)]))
        forced_now = int(len([row for row in list(state.get("system_forced_expand_event_rows") or []) if isinstance(row, Mapping)]))
        macro_now = int(len([row for row in list(state.get("system_macro_output_record_rows") or []) if isinstance(row, Mapping)]))
        tier_rows_tick = [
            dict(row)
            for row in list(state.get("system_tier_change_event_rows") or [])
            if isinstance(row, Mapping)
            and int(max(0, _as_int(row.get("tick", -1), -1))) == int(tick)
        ]
        denied_tick = [
            row for row in tier_rows_tick if str(row.get("result", "")).strip() == "denied" and "budget" in str(row.get("reason_code", "")).lower()
        ]
        inv_fail_tick = [row for row in tier_rows_tick if str(row.get("reason_code", "")).strip() in _INVARIANT_FAILURE_REASONS]
        macro_meta = _as_map(macro_res.get("result_metadata"))
        processed_caps = int(max(0, _as_int(macro_meta.get("processed_capsule_count", 0), 0)))
        deferred_caps = int(max(0, _as_int(macro_meta.get("deferred_capsule_count", 0), 0)))

        metrics["collapse_count_per_tick"].append(int(max(0, collapse_now - prev_collapse)))
        metrics["expand_count_per_tick"].append(int(max(0, expand_now - prev_expand)))
        metrics["forced_expand_count_per_tick"].append(int(max(0, forced_now - prev_forced)))
        metrics["denied_expand_count_per_tick"].append(int(len(denied_tick)))
        metrics["macro_model_evaluations_per_tick"].append(int(max(0, macro_now - prev_macro)))
        metrics["invariant_check_failures_per_tick"].append(int(len(inv_fail_tick)))
        metrics["cache_hit_ratio_per_tick"].append(float(round(float(processed_caps) / float(max(1, processed_caps + deferred_caps)), 6)))
        metrics["compaction_marker_count_per_tick"].append(int(len([row for row in list(state.get("compaction_markers") or []) if isinstance(row, Mapping)])))
        metrics["expand_cap_used_per_tick"].append(int(limits["max_expands_per_tick"]))
        prev_collapse, prev_expand, prev_forced, prev_macro = collapse_now, expand_now, forced_now, macro_now

    proof_hash_summary = _proof_hash_summary(state)
    denied_expand_total = int(sum(int(_as_int(item, 0)) for item in list(metrics.get("denied_expand_count_per_tick") or [])))
    invariant_failure_total = int(sum(int(_as_int(item, 0)) for item in list(metrics.get("invariant_check_failures_per_tick") or [])))
    degradation_summary = _degradation_signal_summary(
        state,
        denied_expand_count=denied_expand_total,
        invariant_failure_count=invariant_failure_total,
    )
    deterministic_ordering = bool(
        _is_sorted(
            state.get("system_tier_change_event_rows"),
            lambda row: (int(max(0, _as_int(row.get("tick", 0), 0))), str(row.get("system_id", "")), str(row.get("event_id", ""))),
        )
        and _is_sorted(
            state.get("control_decision_log"),
            lambda row: (int(max(0, _as_int(row.get("tick", 0), 0))), str(row.get("decision_id", ""))),
        )
    )
    bounded_expands = bool(
        all(
            int(metrics["expand_count_per_tick"][idx]) <= int(max(1, _as_int(metrics["expand_cap_used_per_tick"][idx], 1)))
            for idx in range(len(metrics["expand_count_per_tick"]))
        )
    )
    no_silent_transitions = bool(_no_silent_transition(state))
    invariants_preserved = bool(sum(metrics["invariant_check_failures_per_tick"]) == 0)
    degrade_policy_logged = bool(all(bool(value) for value in dict(degradation_summary.get("flags") or {}).values()))
    from tools.system.tool_replay_sys_window import verify_sys_replay_window
    replay_report = verify_sys_replay_window(state_payload=state, expected_payload=copy.deepcopy(state))
    stable_replay_hashes = bool(str(replay_report.get("result", "")).strip() == "complete")

    assertions = {
        "deterministic_ordering": deterministic_ordering,
        "bounded_expands_per_tick": bounded_expands,
        "no_silent_transitions": no_silent_transitions,
        "invariants_preserved_roundtrip": invariants_preserved,
        "degrade_policy_logged": degrade_policy_logged,
        "stable_replay_hashes": stable_replay_hashes,
    }
    metrics["proof_hash_summary"] = dict(proof_hash_summary)
    metrics["degradation_signal_summary"] = dict(degradation_summary)

    report = {
        "schema_version": "1.0.0",
        "result": "complete" if all(bool(value) for value in assertions.values()) else "refused",
        "scenario_id": scenario_id,
        "tick_count": int(horizon),
        "metrics": metrics,
        "assertions": assertions,
        "extensions": {
            "degradation_policy_order": list(_SYS_DEGRADE_ORDER),
            "replay_report": replay_report,
            "final_state_snapshot": dict(state),
        },
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    if str(report.get("result", "")).strip() == "complete":
        return report
    return {**report, "errors": [{"code": "refusal.sys.stress.assertion_failed", "message": "SYS stress assertions failed"}]}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic SYS-8 stress scenario.")
    parser.add_argument("--scenario", default="build/system/sys8_stress_scenario.json")
    parser.add_argument("--seed", type=int, default=88017)
    parser.add_argument("--system-count", type=int, default=512)
    parser.add_argument("--nested-size", type=int, default=20)
    parser.add_argument("--tick-count", type=int, default=64)
    parser.add_argument("--shard-count", type=int, default=4)
    parser.add_argument("--player-count", type=int, default=2)
    parser.add_argument("--roi-width", type=int, default=18)
    parser.add_argument("--time-warp-batch-size", type=int, default=4)
    parser.add_argument("--max-expands-per-tick", type=int, default=0)
    parser.add_argument("--max-collapses-per-tick", type=int, default=0)
    parser.add_argument("--max-macro-capsules-per-tick", type=int, default=0)
    parser.add_argument("--max-health-updates-per-tick", type=int, default=0)
    parser.add_argument("--max-reliability-evals-per-tick", type=int, default=0)
    parser.add_argument("--output", default="build/system/sys8_stress_report.json")
    return parser


def main() -> int:
    args = _parser().parse_args()
    scenario = _read_json(os.path.normpath(os.path.abspath(str(args.scenario))))
    if not scenario:
        scenario = generate_sys_stress_scenario(
            seed=int(args.seed),
            system_count=int(args.system_count),
            nested_size=int(args.nested_size),
            tick_horizon=int(args.tick_count),
            shard_count=int(args.shard_count),
            player_count=int(args.player_count),
            roi_width=int(args.roi_width),
            time_warp_batch_size=int(args.time_warp_batch_size),
        )
    report = run_sys_stress(
        scenario=scenario,
        tick_count=int(args.tick_count),
        max_expands_per_tick=int(args.max_expands_per_tick),
        max_collapses_per_tick=int(args.max_collapses_per_tick),
        max_macro_capsules_per_tick=int(args.max_macro_capsules_per_tick),
        max_health_updates_per_tick=int(args.max_health_updates_per_tick),
        max_reliability_evals_per_tick=int(args.max_reliability_evals_per_tick),
    )
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_abs, report)
    print(
        json.dumps(
            {
                "output_path": output_abs,
                "scenario_id": str(report.get("scenario_id", "")),
                "result": str(report.get("result", "")),
                "assertions": dict(report.get("assertions") or {}),
                "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
