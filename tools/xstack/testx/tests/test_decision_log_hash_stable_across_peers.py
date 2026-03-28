"""STRICT test: decision-log fingerprints remain stable across peer replicas."""

from __future__ import annotations

import json
import os
import sys
import tempfile


TEST_ID = "test_decision_log_hash_stable_across_peers"
TEST_TAGS = ["strict", "control", "audit", "multiplayer", "determinism"]


def _action_registry() -> dict:
    return {
        "actions": [
            {
                "schema_version": "1.0.0",
                "action_id": "action.interaction.execute_process",
                "display_name": "Execute Process",
                "produces": {"process_id": "", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": [],
                "required_capabilities": [],
                "target_kinds": ["none", "structure"],
                "extensions": {"adapter": "legacy.process_id"},
            }
        ]
    }


def _policy_registry() -> dict:
    return {
        "policies": [
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.player.diegetic",
                "description": "Deterministic decision-log baseline.",
                "allowed_actions": ["action.interaction.*"],
                "allowed_abstraction_levels": ["AL0", "AL1"],
                "allowed_view_policies": ["view.mode.first_person"],
                "allowed_fidelity_ranges": ["macro", "meso"],
                "downgrade_rules": {},
                "strictness": "C1",
                "extensions": {},
            }
        ]
    }


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _run_peer(repo_root: str, *, build_control_intent, build_control_resolution) -> list[str]:
    law_profile = {
        "law_profile_id": "law.ctrl9.decision_hash",
        "allowed_processes": ["process.inspect_generate_snapshot"],
        "forbidden_processes": [],
    }
    authority_context = {
        "authority_origin": "server",
        "peer_id": "peer.authority",
        "subject_id": "subject.replica",
        "law_profile_id": "law.ctrl9.decision_hash",
        "entitlements": [],
        "epistemic_scope": {"scope_id": "ep.scope.default", "visibility_level": "diegetic"},
        "privilege_level": "operator",
    }
    fingerprints: list[str] = []
    for tick in (91, 92, 93):
        intent = build_control_intent(
            requester_subject_id="subject.replica",
            requested_action_id="action.interaction.execute_process",
            target_kind="structure",
            target_id="structure.hash.{}".format(tick),
            parameters={"process_id": "process.inspect_generate_snapshot", "target_id": "structure.hash.{}".format(tick)},
            abstraction_level_requested="AL1",
            fidelity_requested="meso",
            view_requested="view.mode.first_person",
            created_tick=tick,
        )
        result = build_control_resolution(
            control_intent=intent,
            law_profile=law_profile,
            authority_context=authority_context,
            policy_context={
                "control_policy_id": "ctrl.policy.player.diegetic",
                "server_profile_id": "server.profile.lockstep.strict",
                "net_policy_id": "policy.net.lockstep",
                "pack_lock_hash": "e" * 64,
                "peer_id": "peer.authority",
                "submission_tick": tick,
                "deterministic_sequence_number": tick - 90,
            },
            control_action_registry=_action_registry(),
            control_policy_registry=_policy_registry(),
            repo_root=repo_root,
        )
        if str(result.get("result", "")) != "complete":
            return []
        resolution = dict(result.get("resolution") or {})
        log_ref = str(resolution.get("decision_log_ref", "")).strip()
        if not log_ref:
            return []
        log_path = os.path.join(repo_root, log_ref.replace("/", os.sep))
        payload = _read_json(log_path)
        fingerprint = str(payload.get("deterministic_fingerprint", "")).strip()
        if not fingerprint:
            return []
        fingerprints.append(fingerprint)
    return fingerprints


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control import build_control_intent, build_control_resolution

    with tempfile.TemporaryDirectory(prefix="ctrl9_peer_a_") as peer_a_dir:
        peer_a_hashes = _run_peer(
            peer_a_dir,
            build_control_intent=build_control_intent,
            build_control_resolution=build_control_resolution,
        )
    with tempfile.TemporaryDirectory(prefix="ctrl9_peer_b_") as peer_b_dir:
        peer_b_hashes = _run_peer(
            peer_b_dir,
            build_control_intent=build_control_intent,
            build_control_resolution=build_control_resolution,
        )

    if not peer_a_hashes or not peer_b_hashes:
        return {"status": "fail", "message": "unable to collect decision-log fingerprints for one or more peers"}
    if peer_a_hashes != peer_b_hashes:
        return {"status": "fail", "message": "decision-log fingerprint sequence diverged across peer replicas"}
    return {"status": "pass", "message": "decision-log fingerprint stability across peers passed"}

