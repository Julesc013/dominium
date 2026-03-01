"""STRICT test: control artifact compat stubs + legacy save replay determinism."""

from __future__ import annotations

import json
import os
import sys
import tempfile


TEST_ID = "test_control_save_compat_replay"
TEST_TAGS = ["strict", "control", "compatx", "replay"]


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


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
                "description": "Compat replay deterministic policy",
                "allowed_actions": ["action.interaction.*"],
                "allowed_abstraction_levels": ["AL0", "AL1", "AL2"],
                "allowed_view_policies": ["view.mode.first_person"],
                "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                "downgrade_rules": {},
                "strictness": "C1",
                "extensions": {},
            }
        ]
    }


def _legacy_saved_intents() -> list[dict]:
    return [
        {
            "requester_subject_id": "subject.legacy.001",
            "requested_action_id": "action.interaction.execute_process",
            "target_kind": "structure",
            "target_id": "structure.legacy.alpha",
            "parameters": {"process_id": "process.inspect_generate_snapshot", "target_id": "structure.legacy.alpha"},
            "abstraction_level_requested": "AL1",
            "fidelity_requested": "meso",
            "view_requested": "view.mode.first_person",
            "created_tick": 300,
        },
        {
            "requester_subject_id": "subject.legacy.002",
            "requested_action_id": "action.interaction.execute_process",
            "target_kind": "structure",
            "target_id": "structure.legacy.beta",
            "parameters": {"process_id": "process.inspect_generate_snapshot", "target_id": "structure.legacy.beta"},
            "abstraction_level_requested": "AL2",
            "fidelity_requested": "micro",
            "view_requested": "view.mode.first_person",
            "created_tick": 301,
        },
        {
            "requester_subject_id": "subject.legacy.003",
            "requested_action_id": "action.interaction.execute_process",
            "target_kind": "none",
            "target_id": None,
            "parameters": {"process_id": "process.inspect_generate_snapshot", "target_id": "structure.legacy.gamma"},
            "abstraction_level_requested": "AL0",
            "fidelity_requested": "macro",
            "view_requested": "view.mode.first_person",
            "created_tick": 302,
        },
    ]


def _run_legacy_replay(temp_root: str, *, build_control_intent, build_control_resolution, canonical_sha256) -> dict:
    decision_hashes: list[str] = []
    resolution_hashes: list[str] = []
    law_profile = {
        "law_profile_id": "law.ctrl10.compat.replay",
        "allowed_processes": ["process.inspect_generate_snapshot"],
        "forbidden_processes": [],
    }
    for seq, saved in enumerate(_legacy_saved_intents(), start=1):
        intent = build_control_intent(**dict(saved))
        result = build_control_resolution(
            control_intent=intent,
            law_profile=law_profile,
            authority_context={
                "authority_origin": "replay",
                "peer_id": str(saved.get("requester_subject_id", "")),
                "subject_id": str(saved.get("requester_subject_id", "")),
                "law_profile_id": "law.ctrl10.compat.replay",
                "entitlements": [],
                "epistemic_scope": {"scope_id": "ep.scope.default", "visibility_level": "diegetic"},
                "privilege_level": "operator",
            },
            policy_context={
                "control_policy_id": "ctrl.policy.player.diegetic",
                "server_profile_id": "server.profile.replay",
                "net_policy_id": "policy.net.lockstep",
                "pack_lock_hash": "a" * 64,
                "submission_tick": int(saved.get("created_tick", 0) or 0),
                "deterministic_sequence_number": int(seq),
                "peer_id": str(saved.get("requester_subject_id", "")),
            },
            control_action_registry=_action_registry(),
            control_policy_registry=_policy_registry(),
            repo_root=temp_root,
        )
        if str(result.get("result", "")) != "complete":
            return {"ok": False, "message": "legacy replay resolution unexpectedly refused"}
        resolution = dict(result.get("resolution") or {})
        resolution_hashes.append(
            canonical_sha256(
                {
                    "allowed": bool(resolution.get("allowed", False)),
                    "resolved_vector": dict(resolution.get("resolved_vector") or {}),
                    "downgrade_reasons": list(resolution.get("downgrade_reasons") or []),
                }
            )
        )
        log_ref = str(resolution.get("decision_log_ref", "")).strip()
        if not log_ref:
            return {"ok": False, "message": "legacy replay decision_log_ref missing"}
        payload = _read_json(os.path.join(temp_root, log_ref.replace("/", os.sep)))
        fingerprint = str(payload.get("deterministic_fingerprint", "")).strip()
        if not fingerprint:
            return {"ok": False, "message": "legacy replay decision log fingerprint missing"}
        decision_hashes.append(fingerprint)
    return {
        "ok": True,
        "resolution_fingerprint": canonical_sha256(list(resolution_hashes)),
        "decision_fingerprint": canonical_sha256(list(decision_hashes)),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control import build_control_intent, build_control_resolution
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.compatx.schema_registry import load_version_registry
    from tools.xstack.compatx.versioning import resolve_payload_version

    version_registry, version_err = load_version_registry(repo_root)
    if version_err:
        return {"status": "fail", "message": "version registry load failed: {}".format(version_err)}
    schemas = dict(version_registry.get("schemas") or {})
    for schema_name in (
        "control_intent",
        "control_ir",
        "control_decision_log",
        "fidelity_allocation",
        "control_proof_bundle",
    ):
        if schema_name in schemas:
            continue
        return {"status": "fail", "message": "missing compatx schema registration for '{}'".format(schema_name)}

    control_ir_entry = dict(schemas.get("control_ir") or {})
    ir_migration = resolve_payload_version(
        schema_name="control_ir",
        payload_version="0.9.0",
        current_version=str(control_ir_entry.get("current_version", "")),
        supported_versions=list(control_ir_entry.get("supported_versions") or []),
    )
    if str(ir_migration.get("action", "")) != "migrate_stub":
        return {"status": "fail", "message": "control_ir legacy version should route to migration stub"}

    control_log_entry = dict(schemas.get("control_decision_log") or {})
    log_migration = resolve_payload_version(
        schema_name="control_decision_log",
        payload_version="0.1.0",
        current_version=str(control_log_entry.get("current_version", "")),
        supported_versions=list(control_log_entry.get("supported_versions") or []),
    )
    if str(log_migration.get("action", "")) != "migrate_stub":
        return {"status": "fail", "message": "control_decision_log legacy version should route to migration stub"}

    with tempfile.TemporaryDirectory(prefix="ctrl10_compat_replay_a_") as pass_a_dir:
        first = _run_legacy_replay(
            pass_a_dir,
            build_control_intent=build_control_intent,
            build_control_resolution=build_control_resolution,
            canonical_sha256=canonical_sha256,
        )
    with tempfile.TemporaryDirectory(prefix="ctrl10_compat_replay_b_") as pass_b_dir:
        second = _run_legacy_replay(
            pass_b_dir,
            build_control_intent=build_control_intent,
            build_control_resolution=build_control_resolution,
            canonical_sha256=canonical_sha256,
        )
    if not bool(first.get("ok", False)):
        return {"status": "fail", "message": str(first.get("message", "legacy replay pass A failed"))}
    if not bool(second.get("ok", False)):
        return {"status": "fail", "message": str(second.get("message", "legacy replay pass B failed"))}
    if str(first.get("resolution_fingerprint", "")) != str(second.get("resolution_fingerprint", "")):
        return {"status": "fail", "message": "legacy replay control resolution fingerprint drifted"}
    if str(first.get("decision_fingerprint", "")) != str(second.get("decision_fingerprint", "")):
        return {"status": "fail", "message": "legacy replay decision-log fingerprint drifted"}
    return {"status": "pass", "message": "control save compat + legacy replay determinism passed"}
