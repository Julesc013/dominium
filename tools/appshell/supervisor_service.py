#!/usr/bin/env python3
"""Persistent APPSHELL-6 launcher supervisor service."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.appshell.compat_adapter import build_version_payload  # noqa: E402
from src.appshell.ipc import AppShellIPCEndpointServer  # noqa: E402
from src.appshell.logging import (  # noqa: E402
    build_default_log_file_path,
    clear_current_log_engine,
    create_log_engine,
    log_emit,
    set_current_log_engine,
)
from src.appshell.paths import clear_current_virtual_paths, set_current_virtual_paths, vpath_init  # noqa: E402
from src.appshell.supervisor import (  # noqa: E402
    DEFAULT_SUPERVISOR_POLICY_ID,
    SupervisorEngine,
    build_supervisor_run_spec,
    clear_current_supervisor_engine,
    set_current_supervisor_engine,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _ready_payload(engine: SupervisorEngine, endpoint_server: AppShellIPCEndpointServer, run_spec: dict) -> dict:
    payload = {
        "result": "complete",
        "endpoint_id": str(endpoint_server.endpoint_id).strip(),
        "address": str(endpoint_server.address_payload.get("address", "")).strip(),
        "run_manifest_path": str(engine.runtime_paths.get("manifest_path", "")).replace("\\", "/"),
        "state_path": str(engine.runtime_paths.get("state_path", "")).replace("\\", "/"),
        "aggregated_log_path": str(engine.runtime_paths.get("aggregated_log_path", "")).replace("\\", "/"),
        "session_id": str(run_spec.get("session_id", "")).strip(),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Persistent APPSHELL-6 launcher supervisor service.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--seed", default="0")
    parser.add_argument("--session-template-id", default="session.mvp_default")
    parser.add_argument("--session-template-path", default="")
    parser.add_argument("--profile-bundle-path", default="")
    parser.add_argument("--pack-lock-path", default="")
    parser.add_argument("--mod-policy-id", default="")
    parser.add_argument("--overlay-conflict-policy-id", default="")
    parser.add_argument("--contract-bundle-hash", default="")
    parser.add_argument("--supervisor-policy-id", default=DEFAULT_SUPERVISOR_POLICY_ID)
    parser.add_argument("--topology", default="singleplayer")
    parser.add_argument("--install-root", default="")
    parser.add_argument("--store-root", default="")
    parser.add_argument("--install-id", default="")
    parser.add_argument("--install-registry-path", default="")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    vpath_args: list[str] = []
    if str(args.install_root or "").strip():
        vpath_args.extend(["--install-root", str(args.install_root).strip()])
    if str(args.store_root or "").strip():
        vpath_args.extend(["--store-root", str(args.store_root).strip()])
    if str(args.install_id or "").strip():
        vpath_args.extend(["--install-id", str(args.install_id).strip()])
    if str(args.install_registry_path or "").strip():
        vpath_args.extend(["--install-registry-path", str(args.install_registry_path).strip()])
    set_current_virtual_paths(
        vpath_init(
            {
                "repo_root": repo_root,
                "product_id": "launcher",
                "raw_args": vpath_args,
                "executable_path": os.path.join(repo_root, "bin", "launcher"),
            }
        )
    )
    run_spec = build_supervisor_run_spec(
        repo_root=repo_root,
        seed=str(args.seed or "0").strip() or "0",
        session_template_id=str(args.session_template_id or "session.mvp_default").strip(),
        session_template_path=str(args.session_template_path or "").strip(),
        profile_bundle_path=str(args.profile_bundle_path or "").strip(),
        pack_lock_path=str(args.pack_lock_path or "").strip(),
        mod_policy_id=str(args.mod_policy_id or "").strip(),
        overlay_conflict_policy_id=str(args.overlay_conflict_policy_id or "").strip(),
        contract_bundle_hash=str(args.contract_bundle_hash or "").strip(),
        supervisor_policy_id=str(args.supervisor_policy_id or DEFAULT_SUPERVISOR_POLICY_ID).strip(),
        topology=str(args.topology or "singleplayer").strip(),
    )
    if str(run_spec.get("result", "")).strip() != "complete":
        print(json.dumps(run_spec, sort_keys=True), flush=True)
        return 1

    version_payload = build_version_payload(repo_root, product_id="launcher")
    logger = create_log_engine(
        product_id="launcher",
        build_id=str(version_payload.get("build_id", "")).strip(),
        session_id=str(run_spec.get("session_id", "")).strip(),
        console_enabled=False,
        file_path=build_default_log_file_path(repo_root, product_id="launcher", session_id=str(run_spec.get("session_id", "")).strip()),
    )
    set_current_log_engine(logger)

    engine = SupervisorEngine(repo_root=repo_root, run_spec=run_spec)
    set_current_supervisor_engine(engine)
    endpoint_server = AppShellIPCEndpointServer(
        repo_root=repo_root,
        product_id="launcher",
        session_id=str(run_spec.get("session_id", "")).strip(),
        mode_id="headless",
        manifest_path=str(run_spec.get("ipc_manifest_path", "")).strip(),
        session_metadata={
            "contract_bundle_hash": str(run_spec.get("contract_bundle_hash", "")).strip(),
            "pack_lock_hash": str(run_spec.get("pack_lock_hash", "")).strip(),
            "mod_policy_id": str(run_spec.get("mod_policy_id", "")).strip(),
            "overlay_conflict_policy_id": str(run_spec.get("overlay_conflict_policy_id", "")).strip(),
            "session_template_id": str(run_spec.get("session_template_id", "")).strip(),
        },
    )
    try:
        endpoint_server.start()
        engine.attach_endpoint_server(endpoint_server)
        started = engine.start()
        if str(started.get("result", "")).strip() != "complete":
            print(json.dumps(started, sort_keys=True), flush=True)
            return 1
        log_emit(
            category="supervisor",
            severity="info",
            message_key="supervisor.service.ready",
            params={
                "session_id": str(run_spec.get("session_id", "")).strip(),
                "endpoint_id": str(endpoint_server.endpoint_id).strip(),
            },
        )
        print(json.dumps(_ready_payload(engine, endpoint_server, run_spec), sort_keys=True), flush=True)
        engine.wait_for_shutdown()
        return 0
    finally:
        try:
            engine.stop()
        except Exception:
            pass
        endpoint_server.stop()
        clear_current_supervisor_engine()
        clear_current_log_engine()
        clear_current_virtual_paths()


if __name__ == "__main__":
    raise SystemExit(main())
