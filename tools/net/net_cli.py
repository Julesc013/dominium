#!/usr/bin/env python3
"""CLI: deterministic network handshake command surface for MP-2."""

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

from tools.xstack.compatx.validator import validate_instance  # noqa: E402
from tools.xstack.registry_compile.compiler import compile_bundle  # noqa: E402
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload  # noqa: E402
from tools.xstack.sessionx.common import norm, read_json_object, refusal, write_canonical_json  # noqa: E402
from tools.xstack.sessionx.net_handshake import run_loopback_handshake  # noqa: E402


_REGISTRY_FILENAME_MAP = {
    "net_replication_policy_registry_hash": "net_replication_policy.registry.json",
    "anti_cheat_policy_registry_hash": "anti_cheat_policy.registry.json",
    "net_server_policy_registry_hash": "net_server_policy.registry.json",
}


def _repo_root(value: str) -> str:
    if value:
        return os.path.normpath(os.path.abspath(value))
    return REPO_ROOT_HINT


def _state_path(repo_root: str, save_id: str) -> str:
    return os.path.join(repo_root, "build", "net", "state", "{}.json".format(str(save_id)))


def _read_state(repo_root: str, save_id: str) -> dict:
    path = _state_path(repo_root, save_id)
    payload, err = read_json_object(path)
    if err:
        return {
            "schema_version": "1.0.0",
            "save_id": str(save_id),
            "connected": False,
            "handshake_complete": False,
            "endpoint": "",
            "transport_id": "",
            "last_handshake_id": "",
            "extensions": {},
        }
    return payload


def _write_state(repo_root: str, save_id: str, payload: dict) -> str:
    path = _state_path(repo_root, save_id)
    write_canonical_json(path, payload)
    return norm(os.path.relpath(path, repo_root))


def _load_session_spec(repo_root: str, session_spec_path: str) -> Tuple[dict, dict]:
    abs_path = os.path.normpath(os.path.abspath(session_spec_path))
    payload, err = read_json_object(abs_path)
    if err:
        return {}, refusal(
            "refusal.net.envelope_invalid",
            "session_spec path is missing or invalid JSON",
            "Provide a valid SessionSpec JSON file path.",
            {"session_spec_path": norm(abs_path)},
            "$.session_spec",
        )
    checked = validate_instance(
        repo_root=repo_root,
        schema_name="session_spec",
        payload=payload,
        strict_top_level=True,
    )
    if not bool(checked.get("valid", False)):
        return {}, refusal(
            "refusal.net.envelope_invalid",
            "session_spec failed schema validation",
            "Fix SessionSpec fields before running net commands.",
            {"schema_id": "session_spec"},
            "$.session_spec",
        )
    return payload, {}


def _authority_gate(session_spec: dict) -> dict:
    authority = dict(session_spec.get("authority_context") or {})
    entitlements = sorted(set(str(item).strip() for item in (authority.get("entitlements") or []) if str(item).strip()))
    privilege = str(authority.get("privilege_level", "")).strip()
    if privilege not in ("operator", "system"):
        return refusal(
            "refusal.net.authority_violation",
            "net command requires operator or system privilege",
            "Use a SessionSpec with operator/system privilege level for net tooling.",
            {"privilege_level": privilege or "<empty>"},
            "$.authority_context.privilege_level",
        )
    if "session.boot" not in entitlements:
        return refusal(
            "refusal.net.authority_violation",
            "net command requires 'session.boot' entitlement",
            "Add session.boot entitlement to SessionSpec authority_context.",
            {"entitlement": "session.boot"},
            "$.authority_context.entitlements",
        )
    return {"result": "complete"}


def _load_lock_and_registries(repo_root: str, bundle_id: str) -> Tuple[dict, dict, dict, dict, dict]:
    compiled = compile_bundle(
        repo_root=repo_root,
        bundle_id=str(bundle_id),
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=False,
    )
    if str(compiled.get("result", "")) != "complete":
        return {}, {}, {}, {}, refusal(
            "refusal.net.handshake_registry_hash_mismatch",
            "failed to compile lockfile/registries for net handshake",
            "Resolve compile_bundle refusal details and retry.",
            {"bundle_id": str(bundle_id)},
            "$.bundle_id",
        )
    lock_payload, err = read_json_object(os.path.join(repo_root, "build", "lockfile.json"))
    if err:
        return {}, {}, {}, {}, refusal(
            "refusal.net.handshake_pack_lock_mismatch",
            "build/lockfile.json is missing or invalid for net handshake",
            "Rebuild lockfile and retry handshake.",
            {"bundle_id": str(bundle_id)},
            "$.lockfile",
        )
    semantic = validate_lockfile_payload(lock_payload)
    if str(semantic.get("result", "")) != "complete":
        return {}, {}, {}, {}, refusal(
            "refusal.net.handshake_pack_lock_mismatch",
            "lockfile semantic validation failed for net handshake",
            "Rebuild lockfile from deterministic bundle inputs.",
            {"bundle_id": str(bundle_id)},
            "$.lockfile",
        )
    registries = dict(lock_payload.get("registries") or {})
    payloads: Dict[str, dict] = {}
    for key, file_name in sorted(_REGISTRY_FILENAME_MAP.items(), key=lambda item: item[0]):
        payload, payload_err = read_json_object(os.path.join(repo_root, "build", "registries", file_name))
        if payload_err:
            return {}, {}, {}, {}, refusal(
                "refusal.net.handshake_registry_hash_mismatch",
                "required registry '{}' is missing or invalid".format(file_name),
                "Rebuild registries and retry handshake.",
                {"registry_file": file_name},
                "$.registries",
            )
        if str(payload.get("registry_hash", "")).strip() != str(registries.get(key, "")).strip():
            return {}, {}, {}, {}, refusal(
                "refusal.net.handshake_registry_hash_mismatch",
                "registry hash mismatch for '{}'".format(file_name),
                "Rebuild client and server registries from the same lockfile inputs.",
                {"registry_file": file_name},
                "$.registries.{}".format(key),
            )
        payloads[key] = payload
    return lock_payload, payloads.get("net_replication_policy_registry_hash", {}), payloads.get(
        "anti_cheat_policy_registry_hash", {}
    ), payloads.get("net_server_policy_registry_hash", {}), {}


def _command_connect(repo_root: str, session_spec: dict, endpoint_override: str) -> dict:
    network = dict(session_spec.get("network") or {})
    endpoint = str(endpoint_override or network.get("endpoint", "")).strip()
    if not endpoint:
        return refusal(
            "refusal.net.envelope_invalid",
            "net.connect requires endpoint from argument or SessionSpec.network.endpoint",
            "Set --endpoint or populate SessionSpec.network.endpoint.",
            {"command_id": "net.connect"},
            "$.network.endpoint",
        )
    save_id = str(session_spec.get("save_id", "")).strip()
    state = _read_state(repo_root=repo_root, save_id=save_id)
    state.update(
        {
            "schema_version": "1.0.0",
            "save_id": save_id,
            "connected": True,
            "handshake_complete": False,
            "endpoint": endpoint,
            "transport_id": str(network.get("transport_id", "")),
            "last_handshake_id": "",
            "extensions": {},
        }
    )
    return {
        "result": "complete",
        "command_id": "net.connect",
        "save_id": save_id,
        "state_path": _write_state(repo_root=repo_root, save_id=save_id, payload=state),
        "state": state,
    }


def _command_handshake(repo_root: str, session_spec: dict, policy_id: str, anti_cheat_policy_id: str) -> dict:
    network = dict(session_spec.get("network") or {})
    if not network:
        return refusal(
            "refusal.net.envelope_invalid",
            "net.handshake requires SessionSpec network payload",
            "Populate SessionSpec.network fields and retry.",
            {"command_id": "net.handshake"},
            "$.network",
        )
    if str(policy_id).strip():
        network["requested_replication_policy_id"] = str(policy_id).strip()
    if str(anti_cheat_policy_id).strip():
        network["anti_cheat_policy_id"] = str(anti_cheat_policy_id).strip()

    spec_copy = dict(session_spec)
    spec_copy["network"] = network
    lock_payload, replication_registry, anti_cheat_registry, server_policy_registry, lock_error = _load_lock_and_registries(
        repo_root=repo_root,
        bundle_id=str(session_spec.get("bundle_id", "bundle.base.lab")),
    )
    if lock_error:
        return lock_error

    handshake = run_loopback_handshake(
        repo_root=repo_root,
        session_spec=spec_copy,
        lock_payload=lock_payload,
        replication_registry=replication_registry,
        anti_cheat_registry=anti_cheat_registry,
        server_policy_registry=server_policy_registry,
        authority_context=dict(session_spec.get("authority_context") or {}),
    )
    save_id = str(session_spec.get("save_id", "")).strip()
    state = _read_state(repo_root=repo_root, save_id=save_id)
    if str(handshake.get("result", "")) == "complete":
        state.update(
            {
                "connected": True,
                "handshake_complete": True,
                "endpoint": str(network.get("endpoint", "")),
                "transport_id": str(network.get("transport_id", "")),
                "last_handshake_id": str(handshake.get("handshake_id", "")),
            }
        )
        state_path = _write_state(repo_root=repo_root, save_id=save_id, payload=state)
        handshake_rel = ""
        handshake_payload = dict(handshake.get("handshake") or {})
        if handshake_payload:
            handshake_id = str(handshake_payload.get("handshake_id", "")).strip() or "unknown"
            handshake_abs = os.path.join(repo_root, "build", "net", "handshakes", "{}.json".format(handshake_id))
            write_canonical_json(handshake_abs, handshake_payload)
            handshake_rel = norm(os.path.relpath(handshake_abs, repo_root))
        return {
            "result": "complete",
            "command_id": "net.handshake",
            "save_id": save_id,
            "state_path": state_path,
            "handshake_path": handshake_rel,
            "handshake": handshake_payload,
            "handshake_artifact_hash": str(handshake.get("handshake_artifact_hash", "")),
        }
    state.update({"handshake_complete": False})
    state_path = _write_state(repo_root=repo_root, save_id=save_id, payload=state)
    out = dict(handshake)
    out["state_path"] = state_path
    out["command_id"] = "net.handshake"
    return out


def _command_status(repo_root: str, session_spec: dict) -> dict:
    save_id = str(session_spec.get("save_id", "")).strip()
    state = _read_state(repo_root=repo_root, save_id=save_id)
    return {
        "result": "complete",
        "command_id": "net.status",
        "save_id": save_id,
        "state": state,
    }


def _command_disconnect(repo_root: str, session_spec: dict) -> dict:
    save_id = str(session_spec.get("save_id", "")).strip()
    state = _read_state(repo_root=repo_root, save_id=save_id)
    state.update(
        {
            "connected": False,
            "handshake_complete": False,
            "last_handshake_id": "",
        }
    )
    return {
        "result": "complete",
        "command_id": "net.disconnect",
        "save_id": save_id,
        "state_path": _write_state(repo_root=repo_root, save_id=save_id, payload=state),
        "state": state,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic net command surface (MP-2).")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--session-spec", required=True)
    sub = parser.add_subparsers(dest="command")

    connect_cmd = sub.add_parser("net.connect")
    connect_cmd.add_argument("--endpoint", default="")

    handshake_cmd = sub.add_parser("net.handshake")
    handshake_cmd.add_argument("--policy", default="")
    handshake_cmd.add_argument("--anti-cheat", default="")

    sub.add_parser("net.status")
    sub.add_parser("net.disconnect")

    args = parser.parse_args()
    repo_root = _repo_root(str(args.repo_root))
    session_spec, spec_error = _load_session_spec(repo_root=repo_root, session_spec_path=str(args.session_spec))
    if spec_error:
        print(json.dumps(spec_error, indent=2, sort_keys=True))
        return 2
    gate = _authority_gate(session_spec=session_spec)
    if str(gate.get("result", "")) != "complete":
        print(json.dumps(gate, indent=2, sort_keys=True))
        return 2

    command = str(args.command or "").strip()
    if command == "net.connect":
        result = _command_connect(repo_root=repo_root, session_spec=session_spec, endpoint_override=str(args.endpoint))
    elif command == "net.handshake":
        result = _command_handshake(
            repo_root=repo_root,
            session_spec=session_spec,
            policy_id=str(args.policy),
            anti_cheat_policy_id=str(args.anti_cheat),
        )
    elif command == "net.status":
        result = _command_status(repo_root=repo_root, session_spec=session_spec)
    elif command == "net.disconnect":
        result = _command_disconnect(repo_root=repo_root, session_spec=session_spec)
    else:
        parser.print_help()
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
