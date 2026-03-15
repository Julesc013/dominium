#!/usr/bin/env python3
"""Persistent supervised product host for APPSHELL-6."""

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
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _build_ready_payload(
    *,
    endpoint_id: str,
    address: str,
    product_id: str,
    session_id: str,
    pid_stub: str,
    log_file_path: str,
) -> dict:
    payload = {
        "result": "complete",
        "endpoint_id": str(endpoint_id).strip(),
        "address": str(address).strip(),
        "product_id": str(product_id).strip(),
        "session_id": str(session_id).strip(),
        "pid_stub": str(pid_stub).strip(),
        "log_file_path": str(log_file_path).replace("\\", "/"),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Persistent supervised product host for APPSHELL-6.")
    parser.add_argument("--repo-root", default=REPO_ROOT_HINT)
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--seed", default="0")
    parser.add_argument("--session-template-id", default="session.mvp_default")
    parser.add_argument("--profile-bundle-path", default="")
    parser.add_argument("--pack-lock-path", default="")
    parser.add_argument("--pack-lock-hash", default="")
    parser.add_argument("--contract-bundle-hash", default="")
    parser.add_argument("--mod-policy-id", default="")
    parser.add_argument("--overlay-conflict-policy-id", default="")
    parser.add_argument("--ipc-manifest-path", default="")
    parser.add_argument("--run-manifest-path", default="")
    parser.add_argument("--pid-stub", default="")
    parser.add_argument("--install-root", default="")
    parser.add_argument("--store-root", default="")
    parser.add_argument("--install-id", default="")
    parser.add_argument("--install-registry-path", default="")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    product_id = str(args.product_id or "").strip()
    session_id = str(args.session_id or "").strip()
    pid_stub = str(args.pid_stub or "").strip() or "proc.{}.0001".format(product_id)
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
                "product_id": product_id,
                "raw_args": vpath_args,
                "executable_path": os.path.join(repo_root, "bin", product_id),
            }
        )
    )

    version_payload = build_version_payload(repo_root, product_id=product_id)
    log_file_path = build_default_log_file_path(repo_root, product_id=product_id, session_id=session_id)
    logger = create_log_engine(
        product_id=product_id,
        build_id=str(version_payload.get("build_id", "")).strip(),
        session_id=session_id,
        console_enabled=False,
        file_path=log_file_path,
    )
    set_current_log_engine(logger)

    endpoint_server = AppShellIPCEndpointServer(
        repo_root=repo_root,
        product_id=product_id,
        session_id=session_id,
        mode_id="headless" if product_id == "server" else "cli",
        manifest_path=str(args.ipc_manifest_path or "").strip(),
        session_metadata={
            "contract_bundle_hash": str(args.contract_bundle_hash or "").strip(),
            "contract_bundle_path": "",
            "pack_lock_path": str(args.pack_lock_path or "").strip(),
            "pack_lock_hash": str(args.pack_lock_hash or "").strip(),
            "mod_policy_id": str(args.mod_policy_id or "").strip(),
            "overlay_conflict_policy_id": str(args.overlay_conflict_policy_id or "").strip(),
            "profile_bundle_path": str(args.profile_bundle_path or "").strip(),
            "run_manifest_path": str(args.run_manifest_path or "").strip(),
            "seed": str(args.seed or "0").strip() or "0",
            "session_id": session_id,
            "session_template_id": str(args.session_template_id or "").strip(),
            "pid_stub": pid_stub,
        },
    )
    ready_payload = {}
    try:
        started = endpoint_server.start()
        log_emit(
            category="supervisor",
            severity="info",
            message_key="supervisor.child.ready",
            params={
                "product_id": product_id,
                "session_id": session_id,
                "pid_stub": pid_stub,
            },
        )
        ready_payload = _build_ready_payload(
            endpoint_id=str(started.get("endpoint_id", "")).strip(),
            address=str(started.get("address", "")).strip(),
            product_id=product_id,
            session_id=session_id,
            pid_stub=pid_stub,
            log_file_path=log_file_path,
        )
        print(json.dumps(ready_payload, sort_keys=True), flush=True)

        for raw_line in sys.stdin:
            command = str(raw_line or "").strip().lower()
            if not command:
                continue
            if command == "stop":
                log_emit(
                    category="supervisor",
                    severity="info",
                    message_key="supervisor.child.stop_requested",
                    params={"product_id": product_id, "pid_stub": pid_stub},
                )
                break
            if command == "crash":
                log_emit(
                    category="supervisor",
                    severity="error",
                    message_key="supervisor.child.crash_requested",
                    params={"product_id": product_id, "pid_stub": pid_stub},
                )
                return 3
            log_emit(
                category="supervisor",
                severity="info",
                message_key="supervisor.child.stdin_ignored",
                params={"product_id": product_id, "pid_stub": pid_stub, "command": command},
            )
        return 0
    finally:
        endpoint_server.stop()
        clear_current_log_engine()
        clear_current_virtual_paths()


if __name__ == "__main__":
    raise SystemExit(main())
