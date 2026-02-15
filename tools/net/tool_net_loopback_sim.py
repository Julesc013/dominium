#!/usr/bin/env python3
"""Deterministic N-client loopback handshake harness."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Dict, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.compatx.validator import validate_instance
from tools.xstack.registry_compile.compiler import compile_bundle
from tools.xstack.registry_compile.lockfile import validate_lockfile_payload
from tools.xstack.sessionx.common import norm, read_json_object, refusal, write_canonical_json
from tools.xstack.sessionx.net_handshake import run_loopback_handshake


REGISTRY_FILE_MAP = {
    "net_replication_policy_registry_hash": "net_replication_policy.registry.json",
    "anti_cheat_policy_registry_hash": "anti_cheat_policy.registry.json",
    "net_server_policy_registry_hash": "net_server_policy.registry.json",
    "securex_policy_registry_hash": "securex_policy.registry.json",
    "server_profile_registry_hash": "server_profile.registry.json",
}


def _repo_root(raw: str) -> str:
    token = str(raw).strip()
    if token:
        return os.path.normpath(os.path.abspath(token))
    return REPO_ROOT_HINT


def _load_session_spec(repo_root: str, session_spec_path: str) -> Tuple[dict, dict]:
    abs_path = os.path.normpath(os.path.abspath(session_spec_path))
    payload, err = read_json_object(abs_path)
    if err:
        return {}, refusal(
            "refusal.net.envelope_invalid",
            "session_spec path is missing or invalid JSON",
            "Provide a valid SessionSpec JSON path.",
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
            "Fix SessionSpec fields before running loopback simulation.",
            {"schema_id": "session_spec"},
            "$.session_spec",
        )
    return payload, {}


def _load_lock_and_registries(repo_root: str, bundle_id: str) -> Tuple[dict, dict, dict, dict, dict, dict, dict]:
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
        return {}, {}, {}, {}, {}, {}, refusal(
            "refusal.net.handshake_registry_hash_mismatch",
            "failed to compile lockfile/registries for loopback simulation",
            "Resolve compile_bundle refusal details and retry.",
            {"bundle_id": str(bundle_id)},
            "$.bundle_id",
        )
    lock_payload, err = read_json_object(os.path.join(repo_root, "build", "lockfile.json"))
    if err:
        return {}, {}, {}, {}, {}, {}, refusal(
            "refusal.net.handshake_pack_lock_mismatch",
            "build/lockfile.json is missing or invalid",
            "Rebuild lockfile and retry loopback simulation.",
            {"bundle_id": str(bundle_id)},
            "$.lockfile",
        )
    semantic = validate_lockfile_payload(lock_payload)
    if str(semantic.get("result", "")) != "complete":
        return {}, {}, {}, {}, {}, {}, refusal(
            "refusal.net.handshake_pack_lock_mismatch",
            "lockfile semantic validation failed",
            "Rebuild lockfile from deterministic bundle inputs.",
            {"bundle_id": str(bundle_id)},
            "$.lockfile",
        )
    registries = dict(lock_payload.get("registries") or {})
    payloads: Dict[str, dict] = {}
    for key, filename in sorted(REGISTRY_FILE_MAP.items(), key=lambda item: item[0]):
        payload, payload_err = read_json_object(os.path.join(repo_root, "build", "registries", filename))
        if payload_err:
            return {}, {}, {}, {}, {}, {}, refusal(
                "refusal.net.handshake_registry_hash_mismatch",
                "required registry '{}' is missing or invalid".format(filename),
                "Rebuild registries and retry loopback simulation.",
                {"registry_file": filename},
                "$.registries",
            )
        expected = str(registries.get(key, "")).strip()
        actual = str(payload.get("registry_hash", "")).strip()
        if expected != actual:
            return {}, {}, {}, {}, {}, {}, refusal(
                "refusal.net.handshake_registry_hash_mismatch",
                "registry hash mismatch for '{}'".format(filename),
                "Rebuild lockfile and registries from identical bundle inputs.",
                {"registry_file": filename},
                "$.registries.{}".format(key),
            )
        payloads[key] = payload
    return (
        lock_payload,
        payloads.get("net_replication_policy_registry_hash", {}),
        payloads.get("anti_cheat_policy_registry_hash", {}),
        payloads.get("net_server_policy_registry_hash", {}),
        payloads.get("securex_policy_registry_hash", {}),
        payloads.get("server_profile_registry_hash", {}),
        {},
    )


def _client_peer_id(base: str, index: int) -> str:
    token = str(base).strip() or "peer.client"
    return "{}.{}".format(token, int(index))


def _simulate_handshakes(
    repo_root: str,
    session_spec: dict,
    lock_payload: dict,
    replication_registry: dict,
    anti_cheat_registry: dict,
    server_policy_registry: dict,
    securex_policy_registry: dict,
    server_profile_registry: dict,
    clients: int,
) -> Tuple[List[dict], dict]:
    base_network = dict(session_spec.get("network") or {})
    if not base_network:
        return [], refusal(
            "refusal.net.envelope_invalid",
            "loopback simulation requires SessionSpec.network payload",
            "Create SessionSpec with --net-endpoint and related network fields.",
            {"schema_id": "session_spec"},
            "$.network",
        )
    rows: List[dict] = []
    for index in range(int(clients)):
        client_session = copy.deepcopy(session_spec)
        network = dict(client_session.get("network") or {})
        network["client_peer_id"] = _client_peer_id(str(base_network.get("client_peer_id", "")), index)
        client_session["network"] = network
        handshake = run_loopback_handshake(
            repo_root=repo_root,
            session_spec=client_session,
            lock_payload=lock_payload,
            replication_registry=replication_registry,
            anti_cheat_registry=anti_cheat_registry,
            server_policy_registry=server_policy_registry,
            securex_policy_registry=securex_policy_registry,
            server_profile_registry=server_profile_registry,
            authority_context=dict(session_spec.get("authority_context") or {}),
        )
        row = {
            "client_peer_id": str(network.get("client_peer_id", "")),
            "result": str(handshake.get("result", "")),
            "handshake_id": str(handshake.get("handshake_id", "")),
            "handshake_artifact_hash": str(handshake.get("handshake_artifact_hash", "")),
            "reason_code": str(((handshake.get("refusal") or {}).get("reason_code", "")) if isinstance(handshake, dict) else ""),
        }
        rows.append(row)
        if str(handshake.get("result", "")) != "complete":
            return sorted(rows, key=lambda item: str(item.get("client_peer_id", ""))), handshake
    return sorted(rows, key=lambda item: str(item.get("client_peer_id", ""))), {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic loopback handshake simulator.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--session-spec", required=True)
    parser.add_argument("--clients", type=int, default=2)
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    if int(args.clients) < 1:
        print(
            json.dumps(
                refusal(
                    "refusal.net.envelope_invalid",
                    "--clients must be >= 1",
                    "Provide a positive --clients value.",
                    {"clients": str(args.clients)},
                    "$.clients",
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    repo_root = _repo_root(str(args.repo_root))
    session_spec, session_spec_error = _load_session_spec(repo_root=repo_root, session_spec_path=str(args.session_spec))
    if session_spec_error:
        print(json.dumps(session_spec_error, indent=2, sort_keys=True))
        return 2

    (
        lock_payload,
        replication_registry,
        anti_cheat_registry,
        server_policy_registry,
        securex_policy_registry,
        server_profile_registry,
        load_error,
    ) = _load_lock_and_registries(
        repo_root=repo_root,
        bundle_id=str(session_spec.get("bundle_id", "bundle.base.lab")),
    )
    if load_error:
        print(json.dumps(load_error, indent=2, sort_keys=True))
        return 2

    rows, sim_error = _simulate_handshakes(
        repo_root=repo_root,
        session_spec=session_spec,
        lock_payload=lock_payload,
        replication_registry=replication_registry,
        anti_cheat_registry=anti_cheat_registry,
        server_policy_registry=server_policy_registry,
        securex_policy_registry=securex_policy_registry,
        server_profile_registry=server_profile_registry,
        clients=int(args.clients),
    )
    if sim_error:
        out = dict(sim_error)
        out["results"] = rows
        out["result_hash"] = canonical_sha256(rows)
        print(json.dumps(out, indent=2, sort_keys=True))
        return 2

    summary = {
        "schema_version": "1.0.0",
        "result": "complete",
        "clients": int(args.clients),
        "save_id": str(session_spec.get("save_id", "")),
        "endpoint": str(((session_spec.get("network") or {}).get("endpoint", "")) if isinstance(session_spec, dict) else ""),
        "results": rows,
        "result_hash": canonical_sha256(rows),
        "extensions": {},
    }
    out_path_arg = str(args.out).strip()
    out_rel = ""
    if out_path_arg:
        out_abs = os.path.normpath(os.path.abspath(out_path_arg))
    else:
        out_abs = os.path.join(
            repo_root,
            "build",
            "net",
            "loopback",
            "{}.report.json".format(str(session_spec.get("save_id", "save.unknown"))),
        )
    write_canonical_json(out_abs, summary)
    if out_abs.startswith(repo_root):
        out_rel = norm(os.path.relpath(out_abs, repo_root))
    out = dict(summary)
    out["report_path"] = out_rel or norm(out_abs)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
