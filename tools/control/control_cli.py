#!/usr/bin/env python3
"""CLI: deterministic control substrate command surface for controller/camera/possession bindings."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from compat.data_format_loader import stamp_artifact_metadata  # noqa: E402
from tools.xstack.registry_compile.constants import DEFAULT_BUNDLE_ID  # noqa: E402
from tools.xstack.sessionx.common import norm, read_json_object, refusal, write_canonical_json  # noqa: E402
from tools.xstack.sessionx.runner import (  # noqa: E402
    REGISTRY_FILE_MAP,
    _load_lockfile,
    _load_registry_payload,
    _load_schema_validated,
    _select_law_profile,
)
from tools.xstack.sessionx.scheduler import execute_single_intent_srz  # noqa: E402


def _repo_root(value: str) -> str:
    token = str(value).strip()
    if token:
        return os.path.normpath(os.path.abspath(token))
    return REPO_ROOT_HINT


def _authority_from_session_spec(session_spec: dict) -> Tuple[dict, dict]:
    payload = session_spec.get("authority_context")
    if not isinstance(payload, dict):
        return {}, refusal(
            "REFUSE_AUTHORITY_CONTEXT_INVALID",
            "SessionSpec authority_context is missing",
            "Populate authority_context in session_spec.json before running control commands.",
            {"schema_id": "session_spec"},
            "$.authority_context",
        )
    entitlements = sorted(set(str(item).strip() for item in (payload.get("entitlements") or []) if str(item).strip()))
    authority = {
        "authority_origin": str(payload.get("authority_origin", "")).strip() or "client",
        "experience_id": str(session_spec.get("experience_id", "")).strip(),
        "law_profile_id": str(payload.get("law_profile_id", "")).strip(),
        "entitlements": entitlements,
        "epistemic_scope": dict(payload.get("epistemic_scope") or {}),
        "privilege_level": str(payload.get("privilege_level", "")).strip() or "observer",
    }
    return authority, {}


def _save_paths(repo_root: str, save_id: str) -> Dict[str, str]:
    save_dir = os.path.join(repo_root, "saves", str(save_id))
    return {
        "save_dir": save_dir,
        "state_path": os.path.join(save_dir, "universe_state.json"),
        "identity_path": os.path.join(save_dir, "universe_identity.json"),
    }


def _load_runtime_context(repo_root: str, session_spec_path: str, bundle_id: str) -> Tuple[dict, dict, dict, dict, str, dict]:
    session_spec, spec_error = _load_schema_validated(
        repo_root=repo_root,
        schema_name="session_spec",
        path=os.path.normpath(os.path.abspath(session_spec_path)),
    )
    if spec_error:
        return {}, {}, {}, {}, "", spec_error

    save_id = str(session_spec.get("save_id", "")).strip()
    if not save_id:
        return {}, {}, {}, {}, "", refusal(
            "REFUSE_SAVE_ID_MISSING",
            "SessionSpec save_id is missing",
            "Fix session_spec.json save_id before running control commands.",
            {"schema_id": "session_spec"},
            "$.save_id",
        )
    authority_context, authority_error = _authority_from_session_spec(session_spec)
    if authority_error:
        return {}, {}, {}, {}, "", authority_error

    lock_payload, lock_error = _load_lockfile(
        repo_root=repo_root,
        compile_if_missing=False,
        bundle_id=str(bundle_id).strip() or str(session_spec.get("bundle_id", "")).strip() or DEFAULT_BUNDLE_ID,
        lockfile_path="",
    )
    if lock_error:
        return {}, {}, {}, {}, "", lock_error
    registries = dict(lock_payload.get("registries") or {})
    law_registry, law_registry_error = _load_registry_payload(
        repo_root=repo_root,
        file_name=REGISTRY_FILE_MAP["law_registry_hash"],
        expected_hash=str(registries.get("law_registry_hash", "")),
        registries_dir="",
    )
    if law_registry_error:
        return {}, {}, {}, {}, "", law_registry_error
    law_profile, law_error = _select_law_profile(
        law_registry=law_registry,
        law_profile_id=str(authority_context.get("law_profile_id", "")),
    )
    if law_error:
        return {}, {}, {}, {}, "", law_error

    paths = _save_paths(repo_root=repo_root, save_id=save_id)
    universe_state, state_error = _load_schema_validated(
        repo_root=repo_root,
        schema_name="universe_state",
        path=paths["state_path"],
    )
    if state_error:
        return {}, {}, {}, {}, "", state_error
    return session_spec, authority_context, law_profile, universe_state, paths["state_path"], {}


def _control_status_block(universe_state: dict) -> dict:
    controllers = sorted(
        (dict(item) for item in (universe_state.get("controller_assemblies") or []) if isinstance(item, dict)),
        key=lambda item: str(item.get("assembly_id", "")),
    )
    bindings = sorted(
        (dict(item) for item in (universe_state.get("control_bindings") or []) if isinstance(item, dict)),
        key=lambda item: str(item.get("binding_id", "")),
    )
    active_possessions = sorted(
        (
            {
                "controller_id": str(item.get("controller_id", "")),
                "agent_id": str(item.get("target_id", "")),
                "binding_id": str(item.get("binding_id", "")),
            }
            for item in bindings
            if str(item.get("binding_type", "")) == "possess" and bool(item.get("active", True))
        ),
        key=lambda item: (str(item.get("agent_id", "")), str(item.get("controller_id", ""))),
    )
    return {
        "controller_count": len(controllers),
        "binding_count": len(bindings),
        "active_possession_count": len(active_possessions),
        "controllers": controllers,
        "bindings": bindings,
        "active_possessions": active_possessions,
    }


def _intent_for_command(command_id: str, process_id: str, inputs: dict) -> dict:
    digest = canonical_sha256(
        {
            "command_id": str(command_id),
            "process_id": str(process_id),
            "inputs": dict(inputs or {}),
        }
    )
    return {
        "intent_id": "intent.control.{}.{}".format(str(command_id).replace(".", "_"), digest[:16]),
        "process_id": str(process_id),
        "inputs": dict(inputs or {}),
    }


def _execute_command(
    *,
    repo_root: str,
    session_spec: dict,
    authority_context: dict,
    law_profile: dict,
    universe_state: dict,
    state_path: str,
    command_id: str,
    process_id: str,
    inputs: dict,
) -> dict:
    intent = _intent_for_command(command_id=command_id, process_id=process_id, inputs=inputs)
    executed = execute_single_intent_srz(
        repo_root=repo_root,
        universe_state=dict(universe_state),
        law_profile=dict(law_profile),
        authority_context=dict(authority_context),
        intent=intent,
        navigation_indices={},
        worker_count=1,
    )
    if str(executed.get("result", "")) != "complete":
        out = dict(executed)
        out["command_id"] = str(command_id)
        out["process_id"] = str(process_id)
        out["intent"] = intent
        return out
    updated_state = stamp_artifact_metadata(
        repo_root=repo_root,
        artifact_kind="save_file",
        payload=dict(executed.get("universe_state") or {}),
        semantic_contract_bundle_hash=str(session_spec.get("contract_bundle_hash", "")).strip(),
    )
    write_canonical_json(state_path, updated_state)
    return {
        "result": "complete",
        "command_id": str(command_id),
        "process_id": str(process_id),
        "intent": intent,
        "tick": int(executed.get("tick", 0) or 0),
        "state_hash_anchor": str(executed.get("state_hash_anchor", "")),
        "tick_hash_anchor": str(executed.get("tick_hash_anchor", "")),
        "composite_hash": str(executed.get("composite_hash", "")),
        "universe_state_path": norm(os.path.relpath(state_path, repo_root)),
        "status": _control_status_block(updated_state),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Control substrate command surface (EB-1).")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--session-spec", required=True)
    parser.add_argument("--bundle", default="")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("control.controller.list")
    create_cmd = sub.add_parser("control.controller.create")
    create_cmd.add_argument("--controller-id", required=True)
    create_cmd.add_argument("--controller-type", default="script")
    create_cmd.add_argument("--camera-id", default="camera.main")
    create_cmd.add_argument("--owner-peer-id", default="")

    bind_camera_cmd = sub.add_parser("control.bind.camera")
    bind_camera_cmd.add_argument("--controller-id", required=True)
    bind_camera_cmd.add_argument("--camera-id", required=True)

    unbind_camera_cmd = sub.add_parser("control.unbind.camera")
    unbind_camera_cmd.add_argument("--controller-id", required=True)
    unbind_camera_cmd.add_argument("--camera-id", required=True)

    possess_cmd = sub.add_parser("control.possess")
    possess_cmd.add_argument("--controller-id", required=True)
    possess_cmd.add_argument("--agent-id", required=True)

    release_cmd = sub.add_parser("control.release")
    release_cmd.add_argument("--controller-id", required=True)
    release_cmd.add_argument("--agent-id", required=True)

    sub.add_parser("control.status")
    args = parser.parse_args()

    repo_root = _repo_root(str(args.repo_root))
    session_spec, authority_context, law_profile, universe_state, state_path, context_error = _load_runtime_context(
        repo_root=repo_root,
        session_spec_path=str(args.session_spec),
        bundle_id=str(args.bundle),
    )
    if context_error:
        print(json.dumps(context_error, indent=2, sort_keys=True))
        return 2

    command = str(args.command or "").strip()
    if command == "control.controller.list":
        result = {
            "result": "complete",
            "command_id": command,
            "status": _control_status_block(universe_state),
        }
    elif command == "control.status":
        result = {
            "result": "complete",
            "command_id": command,
            "status": _control_status_block(universe_state),
        }
    elif command == "control.controller.create":
        inputs = {
            "controller_id": str(args.controller_id),
            "controller_type": str(args.controller_type),
            "camera_id": str(args.camera_id),
            "owner_peer_id": str(args.owner_peer_id).strip() or authority_context.get("authority_origin"),
        }
        result = _execute_command(
            repo_root=repo_root,
            session_spec=session_spec,
            authority_context=authority_context,
            law_profile=law_profile,
            universe_state=universe_state,
            state_path=state_path,
            command_id=command,
            process_id="process.control_bind_camera",
            inputs=inputs,
        )
    elif command == "control.bind.camera":
        result = _execute_command(
            repo_root=repo_root,
            session_spec=session_spec,
            authority_context=authority_context,
            law_profile=law_profile,
            universe_state=universe_state,
            state_path=state_path,
            command_id=command,
            process_id="process.control_bind_camera",
            inputs={"controller_id": str(args.controller_id), "camera_id": str(args.camera_id)},
        )
    elif command == "control.unbind.camera":
        result = _execute_command(
            repo_root=repo_root,
            session_spec=session_spec,
            authority_context=authority_context,
            law_profile=law_profile,
            universe_state=universe_state,
            state_path=state_path,
            command_id=command,
            process_id="process.control_unbind_camera",
            inputs={"controller_id": str(args.controller_id), "camera_id": str(args.camera_id)},
        )
    elif command == "control.possess":
        result = _execute_command(
            repo_root=repo_root,
            session_spec=session_spec,
            authority_context=authority_context,
            law_profile=law_profile,
            universe_state=universe_state,
            state_path=state_path,
            command_id=command,
            process_id="process.control_possess_agent",
            inputs={"controller_id": str(args.controller_id), "agent_id": str(args.agent_id)},
        )
    elif command == "control.release":
        result = _execute_command(
            repo_root=repo_root,
            session_spec=session_spec,
            authority_context=authority_context,
            law_profile=law_profile,
            universe_state=universe_state,
            state_path=state_path,
            command_id=command,
            process_id="process.control_release_agent",
            inputs={"controller_id": str(args.controller_id), "agent_id": str(args.agent_id)},
        )
    else:
        parser.print_help()
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
