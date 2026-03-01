#!/usr/bin/env python3
"""CTRL-10 extreme control-plane stress scenario runner."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from typing import Dict, List, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.control import build_control_intent, build_control_resolution  # noqa: E402
from src.control.fidelity import arbitrate_fidelity_requests, build_fidelity_request  # noqa: E402
from src.control.proof import build_control_proof_bundle_from_markers, collect_control_decision_markers  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


NET_MODES = (
    "policy.net.lockstep",
    "policy.net.server_authoritative",
    "policy.net.srz_hybrid",
)
PROFILE_IDS = (
    "private",
    "ranked",
    "replay",
)


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
                "action_id": "action.interaction.execute_process",
                "display_name": "Execute Process",
                "produces": {"process_id": "", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": [],
                "required_capabilities": [],
                "target_kinds": ["none", "structure", "surface", "pose_slot", "mount_point"],
                "extensions": {"adapter": "legacy.process_id"},
            },
            {
                "schema_version": "1.0.0",
                "action_id": "action.surface.execute_task",
                "display_name": "Execute Surface Task",
                "produces": {"process_id": "process.task_create", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": ["entitlement.tool.use"],
                "required_capabilities": [],
                "target_kinds": ["surface"],
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "action_id": "action.view.change_policy",
                "display_name": "Change View Policy",
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
    return {
        "policies": [
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.player.diegetic",
                "description": "global stress player policy",
                "allowed_actions": [
                    "action.interaction.execute_process",
                    "action.surface.execute_task",
                    "action.view.change_policy",
                ],
                "allowed_abstraction_levels": ["AL0", "AL1", "AL2"],
                "allowed_view_policies": ["view.mode.first_person", "view.mode.third_person", "view.mode.freecam"],
                "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                "downgrade_rules": {},
                "strictness": "C1",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.admin.meta",
                "description": "global stress admin policy",
                "allowed_actions": ["action.admin.meta_override", "action.view.change_policy"],
                "allowed_abstraction_levels": ["AL0", "AL1", "AL2", "AL3", "AL4"],
                "allowed_view_policies": ["view.mode.first_person", "view.mode.third_person", "view.mode.freecam"],
                "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                "downgrade_rules": {},
                "strictness": "C2",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.replay",
                "description": "global stress replay policy",
                "allowed_actions": ["action.interaction.*", "action.view.change_policy"],
                "allowed_abstraction_levels": ["AL0", "AL1"],
                "allowed_view_policies": ["view.mode.first_person", "view.mode.replay"],
                "allowed_fidelity_ranges": ["macro", "meso"],
                "downgrade_rules": {},
                "strictness": "C1",
                "extensions": {"replay_only": True},
            },
        ]
    }


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.ctrl10.global.stress",
        "allowed_processes": [
            "process.inspect_generate_snapshot",
            "process.view_bind",
            "process.task_create",
            "process.pose_enter",
            "process.meta_pose_override",
        ],
        "forbidden_processes": [],
    }


def _server_profile_id(profile_id: str) -> str:
    token = str(profile_id).strip().lower()
    if token == "ranked":
        return "server.profile.ranked.strict"
    if token == "replay":
        return "server.profile.replay"
    return "server.profile.private.default"


def _authority_context(subject_id: str, entitlements: Sequence[str], privilege_level: str) -> dict:
    return {
        "authority_origin": "server",
        "peer_id": str(subject_id),
        "subject_id": str(subject_id),
        "law_profile_id": "law.ctrl10.global.stress",
        "entitlements": _sorted_unique_strings(list(entitlements or [])),
        "epistemic_scope": {"scope_id": "ep.scope.default", "visibility_level": "diegetic"},
        "privilege_level": str(privilege_level),
    }


def _fidelity_requests_for_tick(subject_ids: Sequence[str], tick: int) -> List[dict]:
    out: List[dict] = []
    for idx, subject_id in enumerate(list(subject_ids or [])):
        requested_level = ("micro", "meso", "macro")[(idx + tick) % 3]
        cost_estimate = 8 if requested_level == "micro" else (5 if requested_level == "meso" else 2)
        out.append(
            build_fidelity_request(
                requester_subject_id=str(subject_id),
                target_kind="region",
                target_id="region.global.{}".format(str(idx).zfill(5)),
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


def _spec_for_subject(profile_id: str, subject_id: str, subject_index: int, tick: int) -> dict:
    abstractions = ("AL0", "AL1", "AL2", "AL3", "AL4")
    fidelities = ("micro", "meso", "macro")
    views = ("view.mode.first_person", "view.mode.third_person", "view.mode.freecam")
    requested_al = abstractions[(subject_index + tick) % len(abstractions)]
    requested_fidelity = fidelities[(subject_index + tick) % len(fidelities)]
    requested_view = views[(subject_index + tick) % len(views)]
    token = str(profile_id).strip().lower()
    if token == "replay":
        if subject_index % 9 == 0:
            return {
                "subject_id": str(subject_id),
                "action_id": "action.interaction.execute_process",
                "policy_id": "ctrl.policy.replay",
                "params": {"process_id": "process.pose_enter", "pose_slot_id": "pose.slot.{}".format(subject_index)},
                "requested_al": "AL1",
                "requested_fidelity": "meso",
                "requested_view": "view.mode.replay",
                "entitlements": [],
                "privilege_level": "operator",
                "target_kind": "pose_slot",
                "target_id": "pose.slot.{}".format(subject_index),
            }
        return {
            "subject_id": str(subject_id),
            "action_id": "action.view.change_policy",
            "policy_id": "ctrl.policy.replay",
            "params": {"subject_id": str(subject_id), "view_policy_id": "view.mode.first_person"},
            "requested_al": "AL0",
            "requested_fidelity": "meso",
            "requested_view": "view.mode.replay",
            "entitlements": [],
            "privilege_level": "operator",
            "target_kind": "none",
            "target_id": None,
        }
    if subject_index % 97 == 0:
        return {
            "subject_id": str(subject_id),
            "action_id": "action.admin.meta_override",
            "policy_id": "ctrl.policy.admin.meta",
            "params": {"action": "override", "target_id": "meta.global.{}".format(subject_index)},
            "requested_al": "AL4",
            "requested_fidelity": "micro",
            "requested_view": requested_view,
            "entitlements": ["entitlement.control.admin"],
            "privilege_level": "admin",
            "target_kind": "none",
            "target_id": None,
        }
    if subject_index % 13 == 0:
        return {
            "subject_id": str(subject_id),
            "action_id": "action.view.change_policy",
            "policy_id": "ctrl.policy.player.diegetic",
            "params": {"subject_id": str(subject_id), "view_policy_id": requested_view},
            "requested_al": "AL1",
            "requested_fidelity": requested_fidelity,
            "requested_view": requested_view,
            "entitlements": ["entitlement.control.camera"],
            "privilege_level": "operator",
            "target_kind": "none",
            "target_id": None,
        }
    if subject_index % 11 == 0:
        return {
            "subject_id": str(subject_id),
            "action_id": "action.surface.execute_task",
            "policy_id": "ctrl.policy.player.diegetic",
            "params": {
                "surface_id": "surface.global.{}".format(str(subject_index).zfill(5)),
                "task_type_id": "task.inspect",
                "actor_subject_id": str(subject_id),
            },
            "requested_al": requested_al,
            "requested_fidelity": requested_fidelity,
            "requested_view": requested_view,
            "entitlements": ["entitlement.tool.use"],
            "privilege_level": "operator",
            "target_kind": "surface",
            "target_id": "surface.global.{}".format(str(subject_index).zfill(5)),
        }
    return {
        "subject_id": str(subject_id),
        "action_id": "action.interaction.execute_process",
        "policy_id": "ctrl.policy.player.diegetic",
        "params": {
            "process_id": "process.inspect_generate_snapshot",
            "target_id": "structure.global.{}".format(str(subject_index).zfill(5)),
            "desired_fidelity": requested_fidelity,
        },
        "requested_al": requested_al,
        "requested_fidelity": requested_fidelity,
        "requested_view": requested_view,
        "entitlements": [],
        "privilege_level": "operator",
        "target_kind": "structure",
        "target_id": "structure.global.{}".format(str(subject_index).zfill(5)),
    }


def _decision_log_fingerprint(repo_root: str, decision_log_ref: str) -> str:
    rel = str(decision_log_ref or "").strip()
    if not rel:
        return ""
    abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
    payload = _read_json(abs_path)
    return str(payload.get("deterministic_fingerprint", "")).strip()


def _run_mode_profile(
    *,
    repo_root: str,
    mode_id: str,
    profile_id: str,
    subjects: int,
    ticks: int,
    max_cost_units_per_tick: int,
) -> dict:
    action_registry = _control_action_registry()
    policy_registry = _control_policy_registry()
    law_profile = _law_profile()
    subject_ids = ["subject.global.{}".format(str(i).zfill(5)) for i in range(int(subjects))]
    runtime_budget_state: dict = {}
    fairness_state: dict = {}
    subject_budget_allocated = dict((subject_id, 0) for subject_id in subject_ids)
    refusal_counts: Dict[str, int] = {}
    downgrade_counts: Dict[str, int] = {}
    decision_log_hashes: List[str] = []
    proof_bundle_hashes: List[str] = []
    per_tick_cost_usage: List[dict] = []
    downgrade_order_hashes: List[str] = []
    envelope_ids_seen = set()
    envelope_overflow = False

    sequence = 0
    for tick in range(1, int(ticks) + 1):
        fidelity_result = arbitrate_fidelity_requests(
            fidelity_requests=_fidelity_requests_for_tick(subject_ids=subject_ids, tick=tick),
            rs5_budget_state={
                "tick": int(tick),
                "max_cost_units_per_tick": int(max_cost_units_per_tick),
                "runtime_budget_state": dict(runtime_budget_state),
                "fairness_state": dict(fairness_state),
                "connected_subject_ids": list(subject_ids),
                "envelope_id": "budget.ctrl10.global.stress",
            },
            server_profile={"server_profile_id": _server_profile_id(profile_id)},
            fidelity_policy={"policy_id": "fidelity.policy.rank_fair" if str(profile_id) == "ranked" else "fidelity.policy.default"},
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

        tick_envelopes: List[dict] = []
        for subject_index, subject_id in enumerate(subject_ids):
            sequence += 1
            spec = _spec_for_subject(profile_id=profile_id, subject_id=subject_id, subject_index=subject_index, tick=tick)
            intent = build_control_intent(
                requester_subject_id=str(spec.get("subject_id", "")),
                requested_action_id=str(spec.get("action_id", "")),
                target_kind=str(spec.get("target_kind", "none")),
                target_id=spec.get("target_id"),
                parameters=dict(spec.get("params") or {}),
                abstraction_level_requested=str(spec.get("requested_al", "AL0")),
                fidelity_requested=str(spec.get("requested_fidelity", "meso")),
                view_requested=str(spec.get("requested_view", "view.mode.first_person")),
                created_tick=int(tick),
            )
            result = build_control_resolution(
                control_intent=dict(intent),
                law_profile=dict(law_profile),
                authority_context=_authority_context(
                    subject_id=str(subject_id),
                    entitlements=list(spec.get("entitlements") or []),
                    privilege_level=str(spec.get("privilege_level", "operator")),
                ),
                policy_context={
                    "control_policy_id": str(spec.get("policy_id", "ctrl.policy.player.diegetic")),
                    "server_profile_id": _server_profile_id(profile_id),
                    "ranked_server": bool(str(profile_id) == "ranked"),
                    "net_policy_id": str(mode_id),
                    "pack_lock_hash": "c" * 64,
                    "submission_tick": int(tick),
                    "deterministic_sequence_number": int(sequence),
                    "peer_id": str(subject_id),
                },
                control_action_registry=action_registry,
                control_policy_registry=policy_registry,
                repo_root=repo_root,
            )
            resolution = dict(result.get("resolution") or {})
            log_hash = _decision_log_fingerprint(repo_root=repo_root, decision_log_ref=str(resolution.get("decision_log_ref", "")))
            if log_hash:
                decision_log_hashes.append(log_hash)
            if str(result.get("result", "")) != "complete":
                refusal_payload = dict(result.get("refusal") or {})
                reason_code = str(refusal_payload.get("reason_code", "refusal.ctrl.unknown")).strip() or "refusal.ctrl.unknown"
                refusal_counts[reason_code] = int(refusal_counts.get(reason_code, 0) + 1)
            reasons = _sorted_unique_strings(list(resolution.get("downgrade_reasons") or []))
            for reason in reasons:
                downgrade_counts[reason] = int(downgrade_counts.get(reason, 0) + 1)
            downgrade_order_hashes.append(
                canonical_sha256(
                    {
                        "tick": int(tick),
                        "sequence": int(sequence),
                        "downgrade_reasons": list(resolution.get("downgrade_reasons") or []),
                    }
                )
            )
            for envelope in list(resolution.get("emitted_intent_envelopes") or []):
                if not isinstance(envelope, Mapping):
                    continue
                envelope_id = str(envelope.get("envelope_id", "")).strip()
                envelope_seq = int(_to_int(envelope.get("deterministic_sequence_number", 0), 0))
                if envelope_id in envelope_ids_seen:
                    envelope_overflow = True
                if envelope_seq < 0 or envelope_seq > 4294967295:
                    envelope_overflow = True
                if envelope_id:
                    envelope_ids_seen.add(envelope_id)
                tick_envelopes.append(dict(envelope))

        markers = collect_control_decision_markers(tick_envelopes)
        proof_bundle = build_control_proof_bundle_from_markers(
            tick_start=int(tick),
            tick_end=int(tick),
            decision_markers=markers,
            proof_id="control.proof.global_stress.{}.{}.tick.{}".format(
                str(mode_id).replace(".", "_"),
                str(profile_id),
                int(tick),
            ),
            extensions={
                "mode_id": str(mode_id),
                "profile_id": str(profile_id),
                "stress_scale": "extreme",
            },
        )
        proof_bundle_hashes.append(str(proof_bundle.get("deterministic_fingerprint", "")))

    starved_subject_ids = sorted(
        subject_id
        for subject_id in subject_ids
        if int(_to_int(subject_budget_allocated.get(subject_id, 0), 0)) <= 0
    )
    report = {
        "mode_id": str(mode_id),
        "profile_id": str(profile_id),
        "subjects": int(subjects),
        "ticks": int(ticks),
        "per_tick_cost_usage": list(per_tick_cost_usage),
        "downgrade_counts": dict((key, int(downgrade_counts[key])) for key in sorted(downgrade_counts.keys())),
        "refusal_counts": dict((key, int(refusal_counts[key])) for key in sorted(refusal_counts.keys())),
        "decision_log_hashes": list(decision_log_hashes),
        "proof_bundle_hashes": list(proof_bundle_hashes),
        "downgrade_order_fingerprint": canonical_sha256(list(downgrade_order_hashes)),
        "envelope_overflow": bool(envelope_overflow),
        "starved_subject_ids": list(starved_subject_ids),
        "deterministic_fingerprint": "",
    }
    seed = dict(report)
    seed["deterministic_fingerprint"] = ""
    report["deterministic_fingerprint"] = canonical_sha256(seed)
    return report


def run_global_control_stress(
    *,
    subjects: int,
    ticks: int,
    max_cost_units_per_tick: int,
) -> dict:
    first_pass: Dict[str, dict] = {}
    second_pass: Dict[str, dict] = {}
    for mode_id in NET_MODES:
        for profile_id in PROFILE_IDS:
            with tempfile.TemporaryDirectory(prefix="ctrl10_global_stress_a_") as temp_dir:
                first_pass["{}::{}".format(mode_id, profile_id)] = _run_mode_profile(
                    repo_root=temp_dir,
                    mode_id=mode_id,
                    profile_id=profile_id,
                    subjects=int(subjects),
                    ticks=int(ticks),
                    max_cost_units_per_tick=int(max_cost_units_per_tick),
                )
            with tempfile.TemporaryDirectory(prefix="ctrl10_global_stress_b_") as temp_dir:
                second_pass["{}::{}".format(mode_id, profile_id)] = _run_mode_profile(
                    repo_root=temp_dir,
                    mode_id=mode_id,
                    profile_id=profile_id,
                    subjects=int(subjects),
                    ticks=int(ticks),
                    max_cost_units_per_tick=int(max_cost_units_per_tick),
                )

    mode_reports = []
    deterministic_ok = True
    no_envelope_overflow = True
    no_starvation_ranked = True
    proof_hashes_stable = True
    downgrade_order_stable = True
    for key in sorted(first_pass.keys()):
        first = dict(first_pass.get(key) or {})
        second = dict(second_pass.get(key) or {})
        deterministic_ok = deterministic_ok and (
            str(first.get("deterministic_fingerprint", "")) == str(second.get("deterministic_fingerprint", ""))
        )
        no_envelope_overflow = no_envelope_overflow and (not bool(first.get("envelope_overflow", False)))
        if str(first.get("profile_id", "")) == "ranked":
            no_starvation_ranked = no_starvation_ranked and (len(list(first.get("starved_subject_ids") or [])) == 0)
        proof_hashes_stable = proof_hashes_stable and (
            list(first.get("proof_bundle_hashes") or []) == list(second.get("proof_bundle_hashes") or [])
        )
        downgrade_order_stable = downgrade_order_stable and (
            str(first.get("downgrade_order_fingerprint", "")) == str(second.get("downgrade_order_fingerprint", ""))
        )
        mode_reports.append(first)

    report = {
        "schema_version": "1.0.0",
        "subjects": int(subjects),
        "ticks": int(ticks),
        "max_cost_units_per_tick": int(max_cost_units_per_tick),
        "mode_reports": sorted(
            mode_reports,
            key=lambda row: (
                str(row.get("mode_id", "")),
                str(row.get("profile_id", "")),
            ),
        ),
        "assertions": {
            "deterministic_results": bool(deterministic_ok),
            "no_envelope_overflow": bool(no_envelope_overflow),
            "deterministic_downgrade_ordering": bool(downgrade_order_stable),
            "ranked_no_starvation": bool(no_starvation_ranked),
            "stable_proof_bundle_hashes": bool(proof_hashes_stable),
        },
        "extensions": {
            "net_modes": list(NET_MODES),
            "profiles": list(PROFILE_IDS),
            "replay_sessions_active": True,
            "meta_override_path_exercised": True,
        },
        "deterministic_fingerprint": "",
    }
    seed = dict(report)
    seed["deterministic_fingerprint"] = ""
    report["deterministic_fingerprint"] = canonical_sha256(seed)
    if all(bool(value) for value in dict(report.get("assertions") or {}).values()):
        return {"result": "complete", "report": report}
    failed = sorted(
        key
        for key, value in dict(report.get("assertions") or {}).items()
        if not bool(value)
    )
    return {
        "result": "refused",
        "errors": [
            {
                "code": "refusal.ctrl.global_stress_assertions_failed",
                "message": "global control stress assertions failed: {}".format(",".join(failed)),
                "path": "$.assertions",
            }
        ],
        "report": report,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run CTRL-10 global control stress suite.")
    parser.add_argument("--subjects", type=int, default=1200)
    parser.add_argument("--ticks", type=int, default=3)
    parser.add_argument("--max-cost-units-per-tick", type=int, default=2400)
    parser.add_argument("--output", default="build/control/control_global_stress_report.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    result = run_global_control_stress(
        subjects=max(1000, int(args.subjects)),
        ticks=max(1, int(args.ticks)),
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
