#!/usr/bin/env python3
"""Run deterministic CTRL-9 control-plane stress scenario."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from control import build_control_intent, build_control_resolution  # noqa: E402
from control.fidelity import arbitrate_fidelity_requests, build_fidelity_request  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _to_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _control_action_registry() -> dict:
    return {
        "actions": [
            {
                "schema_version": "1.0.0",
                "action_id": "action.surface.execute_task",
                "display_name": "Surface Execute",
                "produces": {"process_id": "process.task_create", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": [],
                "required_capabilities": [],
                "target_kinds": ["surface"],
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "action_id": "action.plan.blueprint",
                "display_name": "Plan Blueprint",
                "produces": {"process_id": "", "task_type_id": "", "plan_intent_type": "plan.blueprint"},
                "required_entitlements": ["entitlement.inspect"],
                "required_capabilities": [],
                "target_kinds": ["structure"],
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "action_id": "action.interaction.execute_process",
                "display_name": "Execute Process",
                "produces": {"process_id": "", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": [],
                "required_capabilities": [],
                "target_kinds": ["none", "surface", "structure"],
                "extensions": {"adapter": "legacy.process_id"},
            },
            {
                "schema_version": "1.0.0",
                "action_id": "action.view.change_policy",
                "display_name": "View Policy Change",
                "produces": {"process_id": "process.view_bind", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": ["entitlement.control.camera"],
                "required_capabilities": [],
                "target_kinds": ["none"],
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "action_id": "action.admin.meta_override",
                "display_name": "Meta Override",
                "produces": {"process_id": "process.meta_pose_override", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": ["entitlement.control.admin"],
                "required_capabilities": [],
                "target_kinds": ["none"],
                "extensions": {},
            },
        ]
    }


def _control_policy_registry() -> dict:
    view_rows = ["view.mode.first_person", "view.mode.third_person", "view.mode.freecam"]
    fidelity_rows = ["macro", "meso", "micro"]
    return {
        "policies": [
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.player.diegetic",
                "description": "stress diegetic policy",
                "allowed_actions": [
                    "action.surface.execute_task",
                    "action.interaction.execute_process",
                    "action.view.change_policy",
                ],
                "allowed_abstraction_levels": ["AL0", "AL1", "AL2"],
                "allowed_view_policies": list(view_rows),
                "allowed_fidelity_ranges": list(fidelity_rows),
                "downgrade_rules": {},
                "strictness": "C0",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.planner",
                "description": "stress planner policy",
                "allowed_actions": [
                    "action.plan.blueprint",
                    "action.interaction.execute_process",
                    "action.view.change_policy",
                ],
                "allowed_abstraction_levels": ["AL2", "AL3"],
                "allowed_view_policies": list(view_rows),
                "allowed_fidelity_ranges": list(fidelity_rows),
                "downgrade_rules": {},
                "strictness": "C1",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.admin.meta",
                "description": "stress admin meta policy",
                "allowed_actions": [
                    "action.admin.meta_override",
                    "action.interaction.execute_process",
                    "action.view.change_policy",
                ],
                "allowed_abstraction_levels": ["AL0", "AL1", "AL2", "AL3", "AL4"],
                "allowed_view_policies": list(view_rows),
                "allowed_fidelity_ranges": list(fidelity_rows),
                "downgrade_rules": {},
                "strictness": "C2",
                "extensions": {},
            },
        ]
    }


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.ctrl9.stress.private",
        "allowed_processes": [
            "process.task_create",
            "process.plan_execute",
            "process.inspect_generate_snapshot",
            "process.view_bind",
            "process.meta_pose_override",
        ],
        "forbidden_processes": [],
    }


def _authority_context(subject_id: str, entitlements: Sequence[str], privilege_level: str) -> dict:
    return {
        "authority_origin": "client",
        "peer_id": str(subject_id),
        "subject_id": str(subject_id),
        "law_profile_id": "law.ctrl9.stress.private",
        "entitlements": _sorted_unique_strings(list(entitlements or [])),
        "epistemic_scope": {"scope_id": "ep.scope.default", "visibility_level": "diegetic"},
        "privilege_level": str(privilege_level),
    }


def _request_spec(*, subject_id: str, subject_index: int, tick: int) -> dict:
    abstractions = ("AL0", "AL1", "AL2", "AL3", "AL4")
    fidelities = ("micro", "meso", "macro")
    views = ("view.mode.first_person", "view.mode.third_person", "view.mode.freecam")

    requested_al = abstractions[(subject_index + tick) % len(abstractions)]
    requested_fidelity = fidelities[(subject_index + tick) % len(fidelities)]
    requested_view = views[(subject_index + tick) % len(views)]

    action_id = "action.interaction.execute_process"
    policy_id = "ctrl.policy.player.diegetic"
    entitlements: List[str] = []
    privilege = "operator"
    params: Dict[str, object] = {}
    target_kind = "none"
    target_id = None

    if subject_index % 29 == 0:
        action_id = "action.admin.meta_override"
        policy_id = "ctrl.policy.admin.meta"
        entitlements = ["entitlement.control.admin"]
        privilege = "admin"
        requested_al = "AL4"
        params = {"action": "override", "target_id": "target.meta.{}".format(subject_index)}
    elif subject_index % 17 == 0:
        action_id = "action.view.change_policy"
        entitlements = ["entitlement.control.camera"]
        params = {
            "subject_id": str(subject_id),
            "view_policy_id": requested_view,
            "target_spatial_id": "body.{}".format(subject_index),
        }
    elif subject_index % 13 == 0:
        action_id = "action.plan.blueprint"
        policy_id = "ctrl.policy.planner"
        entitlements = ["entitlement.inspect"]
        params = {"blueprint_id": "bp.{}".format(str(subject_index).zfill(4))}
        target_kind = "structure"
        target_id = "assembly.structure.{}".format(str(subject_index).zfill(4))
    elif subject_index % 11 == 0:
        action_id = "action.interaction.execute_process"
        policy_id = "ctrl.policy.planner"
        entitlements = ["entitlement.inspect"]
        params = {
            "process_id": "process.plan_execute",
            "plan_id": "plan.{}".format(str(subject_index).zfill(4)),
        }
    elif subject_index % 7 == 0:
        action_id = "action.surface.execute_task"
        params = {
            "surface_id": "surface.{}".format(str(subject_index).zfill(4)),
            "task_type_id": "task.inspect",
            "actor_subject_id": str(subject_id),
        }
        target_kind = "surface"
        target_id = "surface.{}".format(str(subject_index).zfill(4))
    else:
        params = {
            "process_id": "process.inspect_generate_snapshot",
            "target_id": "structure.{}".format(str(subject_index).zfill(4)),
            "desired_fidelity": requested_fidelity,
        }

    if action_id == "action.interaction.execute_process" and "process_id" not in params:
        params["process_id"] = "process.inspect_generate_snapshot"

    return {
        "subject_id": str(subject_id),
        "action_id": str(action_id),
        "policy_id": str(policy_id),
        "requested_al": str(requested_al),
        "requested_fidelity": str(requested_fidelity),
        "requested_view": str(requested_view),
        "params": dict(params),
        "entitlements": list(entitlements),
        "privilege_level": str(privilege),
        "target_kind": str(target_kind),
        "target_id": target_id,
    }


def _decision_log_fingerprint(repo_root: str, decision_log_ref: str) -> str:
    rel = str(decision_log_ref or "").strip()
    if not rel:
        return ""
    abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
    payload = _read_json(abs_path)
    return str(payload.get("deterministic_fingerprint", "")).strip()


def _fidelity_requests_for_tick(subject_ids: Sequence[str], tick: int) -> List[dict]:
    out: List[dict] = []
    for idx, subject_id in enumerate(list(subject_ids or [])):
        requested_level = ("micro", "meso", "macro")[(idx + tick) % 3]
        cost_estimate = 8 if requested_level == "micro" else (5 if requested_level == "meso" else 2)
        out.append(
            build_fidelity_request(
                requester_subject_id=str(subject_id),
                target_kind="region",
                target_id="region.{}".format(str(idx).zfill(4)),
                requested_level=requested_level,
                cost_estimate=cost_estimate,
                priority=3 - (idx % 3),
                created_tick=int(tick),
                extensions={
                    "allowed_levels": ["micro", "meso", "macro"],
                    "fidelity_cost_by_level": {"micro": 8, "meso": 5, "macro": 1},
                },
            )
        )
    return out


def _run_profile(
    *,
    repo_root: str,
    profile_id: str,
    subject_count: int,
    tick_count: int,
    max_cost_units_per_tick: int,
) -> dict:
    subject_ids = ["subject.stress.{}".format(str(idx).zfill(3)) for idx in range(int(subject_count))]
    control_action_registry = _control_action_registry()
    control_policy_registry = _control_policy_registry()
    law_profile = _law_profile()

    refusal_counts: Dict[str, int] = {}
    downgrade_counts: Dict[str, int] = {}
    decision_log_hashes: List[str] = []
    envelope_ids_seen = set()
    envelope_overflow = False
    max_sequence = 0

    runtime_budget_state: dict = {}
    fairness_state: dict = {}
    per_tick_cost_usage: List[dict] = []
    subject_budget_allocated = dict((subject_id, 0) for subject_id in subject_ids)

    global_sequence = 0
    for tick in range(1, int(tick_count) + 1):
        fidelity_result = arbitrate_fidelity_requests(
            fidelity_requests=_fidelity_requests_for_tick(subject_ids=subject_ids, tick=tick),
            rs5_budget_state={
                "tick": int(tick),
                "max_cost_units_per_tick": int(max_cost_units_per_tick),
                "runtime_budget_state": dict(runtime_budget_state),
                "fairness_state": dict(fairness_state),
                "connected_subject_ids": list(subject_ids),
                "envelope_id": "budget.ctrl9.stress",
            },
            server_profile={"server_profile_id": str(profile_id)},
            fidelity_policy={"policy_id": "fidelity.policy.rank_fair" if "rank" in str(profile_id).lower() else "fidelity.policy.default"},
        )
        runtime_budget_state = dict(fidelity_result.get("runtime_budget_state") or {})
        fairness_state = dict(fidelity_result.get("fairness_state") or {})
        per_tick_cost_usage.append(
            {
                "tick": int(tick),
                "total_cost_allocated": int(_to_int(fidelity_result.get("total_cost_allocated", 0), 0)),
            }
        )
        for row in list(fidelity_result.get("budget_allocation_records") or []):
            if not isinstance(row, Mapping):
                continue
            subject_id = str(row.get("subject_id", "")).strip()
            if not subject_id:
                continue
            subject_budget_allocated[subject_id] = int(
                _to_int(subject_budget_allocated.get(subject_id, 0), 0)
                + _to_int(row.get("total_cost_allocated", 0), 0)
            )

        for subject_index, subject_id in enumerate(subject_ids):
            spec = _request_spec(subject_id=subject_id, subject_index=subject_index, tick=tick)
            global_sequence += 1
            max_sequence = max(max_sequence, int(global_sequence))
            control_intent = build_control_intent(
                requester_subject_id=str(subject_id),
                requested_action_id=str(spec.get("action_id", "")),
                target_kind=str(spec.get("target_kind", "none")),
                target_id=spec.get("target_id"),
                parameters=dict(spec.get("params") or {}),
                abstraction_level_requested=str(spec.get("requested_al", "AL0")),
                fidelity_requested=str(spec.get("requested_fidelity", "meso")),
                view_requested=str(spec.get("requested_view", "view.mode.first_person")),
                created_tick=int(tick),
            )
            max_control_fidelity = ""
            if str(spec.get("requested_fidelity", "")) == "micro" and ((subject_index + tick) % 5 == 0):
                max_control_fidelity = "meso"
            policy_context = {
                "control_policy_id": str(spec.get("policy_id", "ctrl.policy.player.diegetic")),
                "source_shard_id": "shard.0",
                "target_shard_id": "shard.0",
                "submission_tick": int(tick),
                "deterministic_sequence_number": int(global_sequence),
                "peer_id": str(subject_id),
                "pack_lock_hash": "c" * 64,
                "server_profile_id": str(profile_id),
                "max_control_fidelity": max_control_fidelity,
            }
            result = build_control_resolution(
                control_intent=dict(control_intent),
                law_profile=dict(law_profile),
                authority_context=_authority_context(
                    subject_id=str(subject_id),
                    entitlements=list(spec.get("entitlements") or []),
                    privilege_level=str(spec.get("privilege_level", "operator")),
                ),
                policy_context=policy_context,
                control_action_registry=control_action_registry,
                control_policy_registry=control_policy_registry,
                repo_root=repo_root,
            )
            resolution = dict(result.get("resolution") or {})
            decision_log_fp = _decision_log_fingerprint(repo_root=repo_root, decision_log_ref=str(resolution.get("decision_log_ref", "")))
            if decision_log_fp:
                decision_log_hashes.append(decision_log_fp)

            if str(result.get("result", "")) != "complete":
                refusal = dict(result.get("refusal") or {})
                reason_code = str(refusal.get("reason_code", "refusal.ctrl.unknown")).strip() or "refusal.ctrl.unknown"
                refusal_counts[reason_code] = int(refusal_counts.get(reason_code, 0) + 1)
            for reason in _sorted_unique_strings(list(resolution.get("downgrade_reasons") or [])):
                downgrade_counts[str(reason)] = int(downgrade_counts.get(str(reason), 0) + 1)

            for envelope in list(resolution.get("emitted_intent_envelopes") or []):
                if not isinstance(envelope, Mapping):
                    continue
                envelope_id = str(envelope.get("envelope_id", "")).strip()
                envelope_seq = int(_to_int(envelope.get("deterministic_sequence_number", 0), 0))
                max_sequence = max(max_sequence, envelope_seq)
                if envelope_id in envelope_ids_seen:
                    envelope_overflow = True
                if envelope_seq < 0 or envelope_seq > 4294967295:
                    envelope_overflow = True
                if envelope_id:
                    envelope_ids_seen.add(envelope_id)

    starved_subject_ids = sorted(
        subject_id
        for subject_id in subject_ids
        if int(_to_int(subject_budget_allocated.get(subject_id, 0), 0)) <= 0
    )
    profile_payload = {
        "profile_id": str(profile_id),
        "subject_count": int(subject_count),
        "tick_count": int(tick_count),
        "per_tick_cost_usage": list(per_tick_cost_usage),
        "downgrade_counts": dict((key, int(downgrade_counts[key])) for key in sorted(downgrade_counts.keys())),
        "refusal_counts": dict((key, int(refusal_counts[key])) for key in sorted(refusal_counts.keys())),
        "decision_log_hashes": list(decision_log_hashes),
        "envelope_overflow": bool(envelope_overflow),
        "max_sequence_observed": int(max_sequence),
        "starved_subject_ids": list(starved_subject_ids),
        "subject_budget_allocated": dict(
            (subject_id, int(subject_budget_allocated[subject_id]))
            for subject_id in sorted(subject_budget_allocated.keys())
        ),
        "deterministic_fingerprint": "",
    }
    fingerprint_seed = dict(profile_payload)
    fingerprint_seed["deterministic_fingerprint"] = ""
    profile_payload["deterministic_fingerprint"] = canonical_sha256(fingerprint_seed)
    return profile_payload


def run_control_stress(
    *,
    repo_root: str,
    subject_count: int,
    tick_count: int,
    max_cost_units_per_tick: int,
) -> dict:
    private_profile_id = "server.profile.private.default"
    ranked_profile_id = "server.profile.ranked.strict"

    first_private = _run_profile(
        repo_root=repo_root,
        profile_id=private_profile_id,
        subject_count=subject_count,
        tick_count=tick_count,
        max_cost_units_per_tick=max_cost_units_per_tick,
    )
    first_ranked = _run_profile(
        repo_root=repo_root,
        profile_id=ranked_profile_id,
        subject_count=subject_count,
        tick_count=tick_count,
        max_cost_units_per_tick=max_cost_units_per_tick,
    )
    second_private = _run_profile(
        repo_root=repo_root,
        profile_id=private_profile_id,
        subject_count=subject_count,
        tick_count=tick_count,
        max_cost_units_per_tick=max_cost_units_per_tick,
    )
    second_ranked = _run_profile(
        repo_root=repo_root,
        profile_id=ranked_profile_id,
        subject_count=subject_count,
        tick_count=tick_count,
        max_cost_units_per_tick=max_cost_units_per_tick,
    )

    deterministic_ok = (
        str(first_private.get("deterministic_fingerprint", "")) == str(second_private.get("deterministic_fingerprint", ""))
        and str(first_ranked.get("deterministic_fingerprint", "")) == str(second_ranked.get("deterministic_fingerprint", ""))
    )
    no_envelope_overflow = (not bool(first_private.get("envelope_overflow", False))) and (
        not bool(first_ranked.get("envelope_overflow", False))
    )
    ranked_no_starvation = len(list(first_ranked.get("starved_subject_ids") or [])) == 0
    ranked_meta_refusal_count = int(
        _to_int((dict(first_ranked.get("refusal_counts") or {})).get("refusal.ctrl.meta_forbidden", 0), 0)
    )
    ranked_meta_forbidden_active = ranked_meta_refusal_count > 0

    assertions = {
        "deterministic_results": bool(deterministic_ok),
        "no_envelope_overflow": bool(no_envelope_overflow),
        "ranked_no_starvation": bool(ranked_no_starvation),
        "ranked_forbids_al4_meta": bool(ranked_meta_forbidden_active),
    }

    report = {
        "schema_version": "1.0.0",
        "subject_count": int(subject_count),
        "tick_count": int(tick_count),
        "profiles": {
            "private": dict(first_private),
            "ranked": dict(first_ranked),
        },
        "assertions": assertions,
        "deterministic_fingerprint": "",
    }
    report_seed = dict(report)
    report_seed["deterministic_fingerprint"] = ""
    report["deterministic_fingerprint"] = canonical_sha256(report_seed)

    if all(bool(value) for value in assertions.values()):
        return {
            "result": "complete",
            "stress_report": report,
            "summary": {
                "subject_count": int(subject_count),
                "tick_count": int(tick_count),
                "private_decision_hash_count": len(list(first_private.get("decision_log_hashes") or [])),
                "ranked_decision_hash_count": len(list(first_ranked.get("decision_log_hashes") or [])),
                "ranked_meta_refusal_count": int(ranked_meta_refusal_count),
                "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")),
            },
        }

    failed = sorted(key for key, value in assertions.items() if not bool(value))
    return {
        "result": "refused",
        "errors": [
            {
                "code": "refusal.ctrl.stress_assertion_failed",
                "message": "control stress assertions failed: {}".format(",".join(failed)),
                "path": "$.assertions",
            }
        ],
        "stress_report": report,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic control-plane stress suite.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--subjects", type=int, default=128)
    parser.add_argument("--ticks", type=int, default=8)
    parser.add_argument("--max-cost-units-per-tick", type=int, default=256)
    parser.add_argument("--output", default="build/control/control_stress_report.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root))) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = run_control_stress(
        repo_root=repo_root,
        subject_count=max(100, int(args.subjects)),
        tick_count=max(1, int(args.ticks)),
        max_cost_units_per_tick=max(1, int(args.max_cost_units_per_tick)),
    )
    output = str(args.output).strip()
    if output:
        out_abs = os.path.normpath(os.path.abspath(output))
        _write_json(out_abs, result)
        result["output_path"] = out_abs
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
