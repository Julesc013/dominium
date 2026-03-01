#!/usr/bin/env python3
"""CTRL-10 deterministic cross-platform/thread-count comparison tool."""

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
                "description": "determinism compare player profile",
                "allowed_actions": ["action.interaction.execute_process", "action.view.change_policy"],
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
                "description": "determinism compare admin profile",
                "allowed_actions": ["action.admin.meta_override", "action.view.change_policy"],
                "allowed_abstraction_levels": ["AL0", "AL1", "AL2", "AL3", "AL4"],
                "allowed_view_policies": ["view.mode.first_person", "view.mode.third_person", "view.mode.freecam"],
                "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                "downgrade_rules": {},
                "strictness": "C2",
                "extensions": {},
            },
        ]
    }


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.ctrl10.determinism.compare",
        "allowed_processes": [
            "process.inspect_generate_snapshot",
            "process.view_bind",
            "process.meta_pose_override",
        ],
        "forbidden_processes": [],
    }


def _authority_context(subject_id: str, entitlements: Sequence[str], privilege_level: str) -> dict:
    return {
        "authority_origin": "server",
        "peer_id": str(subject_id),
        "subject_id": str(subject_id),
        "law_profile_id": "law.ctrl10.determinism.compare",
        "entitlements": _sorted_unique_strings(list(entitlements or [])),
        "epistemic_scope": {"scope_id": "ep.scope.default", "visibility_level": "diegetic"},
        "privilege_level": str(privilege_level),
    }


def _fidelity_requests_for_tick(subject_ids: Sequence[str], tick: int) -> List[dict]:
    out: List[dict] = []
    for idx, subject_id in enumerate(list(subject_ids or [])):
        requested_level = ("micro", "meso", "macro")[(idx + tick) % 3]
        cost_estimate = 9 if requested_level == "micro" else (5 if requested_level == "meso" else 2)
        out.append(
            build_fidelity_request(
                requester_subject_id=str(subject_id),
                target_kind="region",
                target_id="region.compare.{}".format(str(idx).zfill(4)),
                requested_level=requested_level,
                cost_estimate=cost_estimate,
                priority=3 - (idx % 3),
                created_tick=int(tick),
                extensions={
                    "allowed_levels": ["micro", "meso", "macro"],
                    "fidelity_cost_by_level": {"micro": 9, "meso": 5, "macro": 1},
                },
            )
        )
    return out


def _spec_for_subject(subject_id: str, subject_index: int, tick: int) -> dict:
    abstractions = ("AL0", "AL1", "AL2", "AL3", "AL4")
    fidelities = ("micro", "meso", "macro")
    views = ("view.mode.first_person", "view.mode.third_person", "view.mode.freecam")
    requested_al = abstractions[(subject_index + tick) % len(abstractions)]
    requested_fidelity = fidelities[(subject_index + tick) % len(fidelities)]
    requested_view = views[(subject_index + tick) % len(views)]
    if subject_index % 17 == 0:
        return {
            "subject_id": str(subject_id),
            "action_id": "action.view.change_policy",
            "policy_id": "ctrl.policy.player.diegetic",
            "params": {
                "subject_id": str(subject_id),
                "view_policy_id": requested_view,
                "target_spatial_id": "body.compare.{}".format(subject_index),
            },
            "requested_al": "AL1",
            "requested_fidelity": requested_fidelity,
            "requested_view": requested_view,
            "entitlements": ["entitlement.control.camera"],
            "privilege_level": "operator",
            "target_kind": "none",
            "target_id": None,
        }
    if subject_index % 29 == 0:
        return {
            "subject_id": str(subject_id),
            "action_id": "action.admin.meta_override",
            "policy_id": "ctrl.policy.admin.meta",
            "params": {"action": "override", "target_id": "meta.compare.{}".format(subject_index)},
            "requested_al": "AL4",
            "requested_fidelity": "micro",
            "requested_view": requested_view,
            "entitlements": ["entitlement.control.admin"],
            "privilege_level": "admin",
            "target_kind": "none",
            "target_id": None,
        }
    return {
        "subject_id": str(subject_id),
        "action_id": "action.interaction.execute_process",
        "policy_id": "ctrl.policy.player.diegetic",
        "params": {
            "process_id": "process.inspect_generate_snapshot",
            "target_id": "structure.compare.{}".format(str(subject_index).zfill(4)),
            "desired_fidelity": requested_fidelity,
        },
        "requested_al": requested_al,
        "requested_fidelity": requested_fidelity,
        "requested_view": requested_view,
        "entitlements": [],
        "privilege_level": "operator",
        "target_kind": "structure",
        "target_id": "structure.compare.{}".format(str(subject_index).zfill(4)),
    }


def _decision_log_fingerprint(repo_root: str, decision_log_ref: str) -> str:
    rel = str(decision_log_ref or "").strip()
    if not rel:
        return ""
    abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
    payload = _read_json(abs_path)
    return str(payload.get("deterministic_fingerprint", "")).strip()


def _run_variant(
    *,
    repo_root: str,
    thread_count: int,
    platform_tag: str,
    subjects: int,
    ticks: int,
    max_cost_units_per_tick: int,
) -> dict:
    action_registry = _control_action_registry()
    policy_registry = _control_policy_registry()
    law_profile = _law_profile()
    subject_ids = ["subject.compare.{}".format(str(i).zfill(4)) for i in range(int(subjects))]
    runtime_budget_state: dict = {}
    fairness_state: dict = {}
    decision_hashes: List[str] = []
    resolution_hashes: List[str] = []
    fidelity_hashes: List[str] = []

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
                "envelope_id": "budget.ctrl10.determinism.compare",
            },
            server_profile={"server_profile_id": "server.profile.private.default"},
            fidelity_policy={"policy_id": "fidelity.policy.rank_fair"},
        )
        runtime_budget_state = dict(fidelity_result.get("runtime_budget_state") or {})
        fairness_state = dict(fidelity_result.get("fairness_state") or {})
        allocation_surface = []
        for row in list(fidelity_result.get("budget_allocation_records") or []):
            if not isinstance(row, Mapping):
                continue
            allocation_surface.append(
                {
                    "subject_id": str(row.get("subject_id", "")),
                    "requested_level": str(row.get("requested_level", "")),
                    "resolved_level": str(row.get("resolved_level", "")),
                    "total_cost_allocated": int(_to_int(row.get("total_cost_allocated", 0), 0)),
                }
            )
        fidelity_hashes.append(
            canonical_sha256(
                sorted(
                    allocation_surface,
                    key=lambda item: (
                        str(item.get("subject_id", "")),
                        str(item.get("requested_level", "")),
                        str(item.get("resolved_level", "")),
                    ),
                )
            )
        )

        for subject_index, subject_id in enumerate(subject_ids):
            sequence += 1
            spec = _spec_for_subject(subject_id=subject_id, subject_index=subject_index, tick=tick)
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
                    "server_profile_id": "server.profile.private.default",
                    "net_policy_id": "policy.net.lockstep",
                    "pack_lock_hash": "a" * 64,
                    "submission_tick": int(tick),
                    "deterministic_sequence_number": int(sequence),
                    "peer_id": str(subject_id),
                    "runtime_thread_count": int(thread_count),
                    "runtime_platform_tag": str(platform_tag),
                },
                control_action_registry=action_registry,
                control_policy_registry=policy_registry,
                repo_root=repo_root,
            )
            resolution = dict(result.get("resolution") or {})
            resolution_hashes.append(
                canonical_sha256(
                    {
                        "result": str(result.get("result", "")),
                        "allowed": bool(resolution.get("allowed", False)),
                        "resolved_vector": dict(resolution.get("resolved_vector") or {}),
                        "downgrade_reasons": list(resolution.get("downgrade_reasons") or []),
                        "refusal_reason_code": str((dict(result.get("refusal") or {})).get("reason_code", "")),
                    }
                )
            )
            decision_hash = _decision_log_fingerprint(
                repo_root=repo_root,
                decision_log_ref=str(resolution.get("decision_log_ref", "")),
            )
            if decision_hash:
                decision_hashes.append(decision_hash)

    report = {
        "thread_count": int(thread_count),
        "platform_tag": str(platform_tag),
        "subjects": int(subjects),
        "ticks": int(ticks),
        "control_resolution_fingerprint": canonical_sha256(list(resolution_hashes)),
        "decision_log_fingerprint": canonical_sha256(list(decision_hashes)),
        "fidelity_allocations_fingerprint": canonical_sha256(list(fidelity_hashes)),
        "deterministic_fingerprint": "",
    }
    seed = dict(report)
    seed["deterministic_fingerprint"] = ""
    report["deterministic_fingerprint"] = canonical_sha256(seed)
    return report


def _parse_csv(raw: str, default_values: Sequence[str]) -> List[str]:
    rows = [str(item).strip() for item in str(raw or "").split(",")]
    out = [token for token in rows if token]
    if out:
        return sorted(set(out))
    return sorted(set(str(item).strip() for item in default_values if str(item).strip()))


def _parse_threads(raw: str) -> List[int]:
    out: List[int] = []
    for token in _parse_csv(raw, ["1", "2", "4"]):
        value = _to_int(token, 0)
        if value > 0:
            out.append(int(value))
    if out:
        return sorted(set(out))
    return [1, 2, 4]


def run_determinism_compare(
    *,
    subjects: int,
    ticks: int,
    max_cost_units_per_tick: int,
    thread_counts: Sequence[int],
    platform_tags: Sequence[str],
) -> dict:
    variants: List[dict] = []
    mismatches: List[dict] = []
    baseline = {}
    for thread_count in sorted(set(int(max(1, _to_int(item, 1))) for item in list(thread_counts or []))):
        for platform_tag in sorted(set(str(item).strip() for item in list(platform_tags or []) if str(item).strip())):
            with tempfile.TemporaryDirectory(prefix="ctrl10_det_compare_") as temp_dir:
                variant = _run_variant(
                    repo_root=temp_dir,
                    thread_count=int(thread_count),
                    platform_tag=str(platform_tag),
                    subjects=int(subjects),
                    ticks=int(ticks),
                    max_cost_units_per_tick=int(max_cost_units_per_tick),
                )
            variants.append(dict(variant))
            if not baseline:
                baseline = dict(variant)
                continue
            for key in (
                "control_resolution_fingerprint",
                "decision_log_fingerprint",
                "fidelity_allocations_fingerprint",
            ):
                if str(variant.get(key, "")) == str(baseline.get(key, "")):
                    continue
                mismatches.append(
                    {
                        "thread_count": int(thread_count),
                        "platform_tag": str(platform_tag),
                        "field": str(key),
                        "baseline": str(baseline.get(key, "")),
                        "actual": str(variant.get(key, "")),
                    }
                )
    report = {
        "schema_version": "1.0.0",
        "subjects": int(subjects),
        "ticks": int(ticks),
        "max_cost_units_per_tick": int(max_cost_units_per_tick),
        "thread_counts": [int(item) for item in sorted(set(int(item) for item in list(thread_counts or [])))],
        "platform_tags": sorted(set(str(item).strip() for item in list(platform_tags or []) if str(item).strip())),
        "variants": sorted(
            variants,
            key=lambda row: (
                int(row.get("thread_count", 0) or 0),
                str(row.get("platform_tag", "")),
            ),
        ),
        "baseline_variant": dict(baseline),
        "mismatches": sorted(
            mismatches,
            key=lambda row: (
                str(row.get("field", "")),
                int(row.get("thread_count", 0) or 0),
                str(row.get("platform_tag", "")),
            ),
        ),
        "assertions": {
            "control_resolution_fingerprints_identical": not any(
                str(row.get("field", "")) == "control_resolution_fingerprint" for row in mismatches
            ),
            "decision_log_fingerprints_identical": not any(
                str(row.get("field", "")) == "decision_log_fingerprint" for row in mismatches
            ),
            "fidelity_allocations_identical": not any(
                str(row.get("field", "")) == "fidelity_allocations_fingerprint" for row in mismatches
            ),
        },
        "extensions": {
            "platform_validation_mode": "simulated_platform_tags",
        },
        "deterministic_fingerprint": "",
    }
    seed = dict(report)
    seed["deterministic_fingerprint"] = ""
    report["deterministic_fingerprint"] = canonical_sha256(seed)
    if mismatches:
        return {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.ctrl.determinism_compare_mismatch",
                    "message": "control determinism comparison detected mismatched fingerprints across variants",
                    "path": "$.mismatches",
                }
            ],
            "report": report,
        }
    return {"result": "complete", "report": report}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run CTRL-10 deterministic cross-platform comparison suite.")
    parser.add_argument("--subjects", type=int, default=96)
    parser.add_argument("--ticks", type=int, default=4)
    parser.add_argument("--max-cost-units-per-tick", type=int, default=256)
    parser.add_argument("--threads", default="1,2,4")
    parser.add_argument("--platforms", default="windows,linux,macos")
    parser.add_argument("--output", default="build/control/control_determinism_compare.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    thread_counts = _parse_threads(str(args.threads))
    platform_tags = _parse_csv(str(args.platforms), ["windows", "linux", "macos"])
    result = run_determinism_compare(
        subjects=max(8, int(args.subjects)),
        ticks=max(1, int(args.ticks)),
        max_cost_units_per_tick=max(1, int(args.max_cost_units_per_tick)),
        thread_counts=thread_counts,
        platform_tags=platform_tags,
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
