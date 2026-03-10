"""SERVER-MVP-1 local singleplayer orchestration controller."""

from __future__ import annotations

import os
import subprocess
from typing import Mapping

from src.client.net import read_loopback_handshake_response, send_loopback_client_ack
from src.runtime.process_spawn import build_server_process_spec, collect_process_output, poll_process, spawn_process
from src.server import boot_server_runtime, load_server_config, materialize_server_session
from src.server.net.loopback_transport import (
    accept_loopback_connection,
    create_loopback_listener,
    send_client_control_request,
    send_client_hello,
    service_loopback_control_channel,
)
from src.server.runtime.tick_loop import advance_server_tick
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.common import norm, read_json_object, refusal, write_canonical_json
from tools.xstack.sessionx.net_protocol import decode_proto_message


REFUSAL_LOCAL_AUTHORITY_FORBIDDEN = "refusal.client.local_authority_forbidden"
REFUSAL_LOCAL_SERVER_CRASHED = "refusal.local_server.crashed"
REFUSAL_LOCAL_SERVER_READY_UNREACHED = "refusal.local_server.ready_unreached"
LOCAL_READY_POLL_ITERATIONS = 4
LOCAL_DIAG_LOG_LIMIT = 24
LOCAL_SERVER_PROFILE_ALLOWLIST = ("server.profile.private_relaxed",)


def _refuse(reason_code: str, message: str, remediation: str, *, details: Mapping[str, object] | None = None, path: str = "$") -> dict:
    relevant_ids = {
        str(key): str(value).strip()
        for key, value in sorted((dict(details or {})).items(), key=lambda item: str(item[0]))
        if str(value).strip()
    }
    return refusal(reason_code, message, remediation, relevant_ids, path)


def _repo_root_abs(repo_root: str) -> str:
    return os.path.normpath(os.path.abspath(str(repo_root or ".")))


def _decode_message(repo_root: str, recv_result: Mapping[str, object]) -> dict:
    if str((dict(recv_result or {})).get("result", "")).strip() != "complete":
        return {}
    decoded = decode_proto_message(
        repo_root=repo_root,
        message_bytes=bytes((dict(recv_result or {})).get("message_bytes") or b""),
    )
    if str(decoded.get("result", "")) != "complete":
        return {}
    return dict(decoded.get("proto_message") or {})


def _diag_stub_path(repo_root: str, save_id: str) -> str:
    return os.path.join(
        repo_root,
        "build",
        "client",
        "local_singleplayer",
        str(save_id or "save.local.singleplayer"),
        "diag",
        "local_server.diag.stub.json",
    )


def _load_json(path: str) -> dict:
    payload, err = read_json_object(path)
    if err:
        return {}
    return dict(payload)


def _write_diag_stub(
    *,
    repo_root: str,
    save_id: str,
    session_spec: Mapping[str, object] | None,
    launch_spec: Mapping[str, object] | None,
    reason_code: str,
    failure_phase: str,
    exit_code: int | None,
    last_logs: object,
) -> str:
    session = dict(session_spec or {})
    launch = dict(launch_spec or {})
    payload = {
        "schema_version": "1.0.0",
        "save_id": str(save_id or session.get("save_id", "")).strip(),
        "universe_id": str(session.get("universe_id", "")).strip(),
        "seed": str(session.get("selected_seed", launch.get("seed", ""))).strip(),
        "pack_lock_hash": str(session.get("pack_lock_hash", launch.get("pack_lock_hash", ""))).strip(),
        "contract_bundle_hash": str(session.get("contract_bundle_hash", launch.get("contract_bundle_hash", ""))).strip(),
        "semantic_contract_registry_hash": str(
            session.get("semantic_contract_registry_hash", launch.get("semantic_contract_registry_hash", ""))
        ).strip(),
        "reason_code": str(reason_code).strip(),
        "failure_phase": str(failure_phase).strip(),
        "exit_code": None if exit_code is None else int(exit_code),
        "last_logs": [str(item) for item in list(last_logs or [])[:LOCAL_DIAG_LOG_LIMIT]],
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    out_abs = _diag_stub_path(repo_root, str(payload.get("save_id", "")).strip())
    write_canonical_json(out_abs, payload)
    return norm(os.path.relpath(out_abs, repo_root))


def _server_profile_id(server_config: Mapping[str, object] | None) -> str:
    ext = dict((dict(server_config or {})).get("extensions") or {})
    return str(ext.get("official.server_profile_id", "")).strip()


def _local_authority_gate(server_config: Mapping[str, object] | None) -> dict:
    server_profile_id = _server_profile_id(server_config)
    if server_profile_id in LOCAL_SERVER_PROFILE_ALLOWLIST:
        return {"result": "complete", "server_profile_id": server_profile_id}
    return _refuse(
        REFUSAL_LOCAL_AUTHORITY_FORBIDDEN,
        "local singleplayer authority spawn is forbidden for the selected server profile",
        "Use a local-authority profile such as `server.profile.private_relaxed`, or connect to an existing remote authority instead.",
        details={"server_profile_id": server_profile_id or "<empty>"},
        path="$.server_profile_id",
    )


def build_local_server_launch_spec(
    *,
    repo_root: str,
    seed: str,
    profile_bundle_path: str,
    pack_lock_path: str,
    server_config_id: str = "server.mvp_default",
    authority_mode: str = "dev",
    save_id: str = "",
    session_spec_path: str = "",
) -> dict:
    repo_root_abs = _repo_root_abs(repo_root)
    server_config, config_error = load_server_config(repo_root_abs, server_config_id=server_config_id)
    if config_error:
        return dict(config_error)
    gate = _local_authority_gate(server_config)
    if str(gate.get("result", "")) != "complete":
        return dict(gate)

    session_spec_abs = os.path.normpath(os.path.abspath(str(session_spec_path))) if str(session_spec_path or "").strip() else ""
    materialized = {}
    pack_lock_abs = (
        os.path.normpath(str(pack_lock_path))
        if os.path.isabs(str(pack_lock_path or ""))
        else os.path.normpath(os.path.join(repo_root_abs, str(pack_lock_path).replace("/", os.sep)))
    )
    if not session_spec_abs:
        materialized = materialize_server_session(
            repo_root=repo_root_abs,
            seed=str(seed or "0").strip() or "0",
            profile_bundle_path=str(profile_bundle_path or "").strip(),
            pack_lock_path=pack_lock_abs,
            server_config_id=str(server_config_id or "server.mvp_default").strip() or "server.mvp_default",
            authority_mode=str(authority_mode or "dev").strip() or "dev",
            save_id=str(save_id or "").strip(),
        )
        if str(materialized.get("result", "")) != "complete":
            return dict(materialized)
        session_spec_abs = os.path.join(repo_root_abs, str(materialized.get("session_spec_path", "")).replace("/", os.sep))

    session_spec = _load_json(session_spec_abs)
    if not session_spec:
        return _refuse(
            REFUSAL_LOCAL_SERVER_CRASHED,
            "local singleplayer launch could not read SessionSpec",
            "Recreate the local singleplayer session and retry.",
            details={"session_spec_path": norm(os.path.relpath(session_spec_abs, repo_root_abs))},
            path="$.session_spec_path",
        )
    process_spec = build_server_process_spec(
        repo_root=repo_root_abs,
        session_spec_path=session_spec_abs,
        seed=str(seed or session_spec.get("selected_seed", "0")).strip() or "0",
        profile_bundle_path=str(profile_bundle_path or "").strip(),
        pack_lock_path=pack_lock_abs,
        contract_bundle_hash=str(session_spec.get("contract_bundle_hash", "")).strip(),
        server_config_id=str(server_config_id or "server.mvp_default").strip() or "server.mvp_default",
        authority_mode=str(authority_mode or "dev").strip() or "dev",
    )
    payload = {
        "result": "complete",
        "repo_root": repo_root_abs,
        "server_config_id": str(server_config_id or "server.mvp_default").strip() or "server.mvp_default",
        "server_profile_id": _server_profile_id(server_config),
        "authority_mode": str(authority_mode or "dev").strip() or "dev",
        "seed": str(seed or session_spec.get("selected_seed", "0")).strip() or "0",
        "profile_bundle_path": norm(str(profile_bundle_path or "").strip()),
        "pack_lock_path": norm(os.path.relpath(pack_lock_abs, repo_root_abs)),
        "session_spec_path": norm(os.path.relpath(session_spec_abs, repo_root_abs)),
        "session_spec": session_spec,
        "save_id": str(session_spec.get("save_id", "")).strip(),
        "pack_lock_hash": str(session_spec.get("pack_lock_hash", "")).strip(),
        "contract_bundle_hash": str(session_spec.get("contract_bundle_hash", "")).strip(),
        "semantic_contract_registry_hash": str(session_spec.get("semantic_contract_registry_hash", "")).strip(),
        "launch_mode": "inproc_loopback_stub",
        "process_spec": process_spec,
        "materialized": bool(materialized),
        "materialized_paths": dict(materialized),
        "ready_poll_iterations": LOCAL_READY_POLL_ITERATIONS,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(
        dict(payload, session_spec={}, process_spec=dict(process_spec), deterministic_fingerprint="")
    )
    return payload


def start_local_singleplayer(
    *,
    repo_root: str,
    seed: str,
    profile_bundle_path: str,
    pack_lock_path: str,
    server_config_id: str = "server.mvp_default",
    authority_mode: str = "dev",
    save_id: str = "",
    session_spec_path: str = "",
    client_peer_id: str = "peer.client.local_singleplayer",
    account_id: str = "account.local.singleplayer",
) -> dict:
    launch_spec = build_local_server_launch_spec(
        repo_root=repo_root,
        seed=seed,
        profile_bundle_path=profile_bundle_path,
        pack_lock_path=pack_lock_path,
        server_config_id=server_config_id,
        authority_mode=authority_mode,
        save_id=save_id,
        session_spec_path=session_spec_path,
    )
    if str(launch_spec.get("result", "")) != "complete":
        return dict(launch_spec)

    repo_root_abs = str(launch_spec.get("repo_root", ""))
    boot = boot_server_runtime(
        repo_root=repo_root_abs,
        session_spec_path=os.path.join(repo_root_abs, str(launch_spec.get("session_spec_path", "")).replace("/", os.sep)),
        pack_lock_path=os.path.join(repo_root_abs, str(launch_spec.get("pack_lock_path", "")).replace("/", os.sep)),
        server_config_id=str(launch_spec.get("server_config_id", "")).strip(),
        expected_contract_bundle_hash=str(launch_spec.get("contract_bundle_hash", "")).strip(),
    )
    if str(boot.get("result", "")) != "complete":
        diag_path = _write_diag_stub(
            repo_root=repo_root_abs,
            save_id=str(launch_spec.get("save_id", "")).strip(),
            session_spec=dict(launch_spec.get("session_spec") or {}),
            launch_spec=launch_spec,
            reason_code=str((dict(boot.get("refusal") or {})).get("reason_code", REFUSAL_LOCAL_SERVER_CRASHED)).strip()
            or REFUSAL_LOCAL_SERVER_CRASHED,
            failure_phase="boot",
            exit_code=1,
            last_logs=[],
        )
        return dict(boot, diag_stub_path=diag_path, launch_spec=dict(launch_spec))
    boot["repo_root"] = repo_root_abs

    listener = create_loopback_listener(boot)
    if str(listener.get("result", "")) != "complete":
        return dict(listener, launch_spec=dict(launch_spec))
    hello = send_client_hello(
        endpoint=str(listener.get("endpoint", "")).strip(),
        client_peer_id=str(client_peer_id).strip() or "peer.client.local_singleplayer",
        account_id=str(account_id).strip() or "account.local.singleplayer",
        repo_root=repo_root_abs,
    )
    if str(hello.get("result", "")) != "complete":
        return dict(hello, launch_spec=dict(launch_spec))

    accepted = {}
    iterations_used = 0
    for attempt in range(1, LOCAL_READY_POLL_ITERATIONS + 1):
        iterations_used = int(attempt)
        accepted = accept_loopback_connection(boot)
        result_token = str(accepted.get("result", "")).strip()
        if result_token == "complete":
            break
        if result_token != "empty":
            return dict(accepted, launch_spec=dict(launch_spec))
    if str(accepted.get("result", "")).strip() != "complete":
        diag_path = _write_diag_stub(
            repo_root=repo_root_abs,
            save_id=str(launch_spec.get("save_id", "")).strip(),
            session_spec=dict(launch_spec.get("session_spec") or {}),
            launch_spec=launch_spec,
            reason_code=REFUSAL_LOCAL_SERVER_READY_UNREACHED,
            failure_phase="ready_handshake",
            exit_code=None,
            last_logs=[],
        )
        return _refuse(
            REFUSAL_LOCAL_SERVER_READY_UNREACHED,
            "local singleplayer server did not become ready within the bounded handshake poll window",
            "Restart the local server or inspect the generated diag stub for the last deterministic boot events.",
            details={"diag_stub_path": diag_path, "ready_poll_iterations": str(LOCAL_READY_POLL_ITERATIONS)},
            path="$.ready_handshake",
        )

    client_transport = hello.get("client_transport")
    handshake_response = {}
    ack_result = {}
    if client_transport is not None:
        handshake_response = read_loopback_handshake_response(repo_root_abs, client_transport)
        ack_payload = dict(handshake_response.get("payload") or {})
        if str(handshake_response.get("result", "")).strip() == "complete":
            ack_result = send_loopback_client_ack(
                client_transport=client_transport,
                connection_id=str(ack_payload.get("connection_id", "")).strip(),
                negotiation_record_hash=str((dict(ack_payload.get("extensions") or {})).get("official.negotiation_record_hash", "")).strip(),
                accepted=True,
                compatibility_mode_id=str((dict(ack_payload.get("extensions") or {})).get("official.compatibility_mode_id", "")).strip(),
            )
            service_loopback_control_channel(boot)
    controller = {
        "repo_root": repo_root_abs,
        "launch_spec": dict(launch_spec),
        "server_boot_payload": boot,
        "client_transport": client_transport,
        "control_request_counter": 0,
        "ready_iterations_used": int(iterations_used),
        "last_client_messages": [],
        "diag_stub_path": "",
    }
    return {
        "result": "complete",
        "launch_spec": dict(launch_spec),
        "listener": dict(listener),
        "hello": {
            "connection_id": str(hello.get("connection_id", "")).strip(),
            "client_peer_id": str(hello.get("client_peer_id", "")).strip(),
            "hello_payload": dict(hello.get("hello_payload") or {}),
        },
        "accepted": dict(accepted),
        "ack_proto": dict(handshake_response.get("proto_message") or {}),
        "handshake_response": dict(handshake_response),
        "client_ack": dict(ack_result),
        "controller": controller,
        "readiness": {
            "result": "complete",
            "strategy": "bounded_poll_iterations",
            "max_iterations": LOCAL_READY_POLL_ITERATIONS,
            "iterations_used": int(iterations_used),
        },
    }


def collect_local_client_messages(controller: Mapping[str, object]) -> dict:
    repo_root = str((dict(controller or {})).get("repo_root", "")).strip()
    client_transport = (dict(controller or {})).get("client_transport")
    rows = []
    if client_transport is None:
        return {"result": "complete", "messages": rows, "log_events": [], "control_responses": [], "tick_stream": []}
    while True:
        recv_result = client_transport.recv()
        if str((dict(recv_result or {})).get("result", "")).strip() != "complete":
            break
        proto_message = _decode_message(repo_root, recv_result)
        if not proto_message:
            break
        rows.append(proto_message)
    logs = [
        dict((dict(row.get("payload_ref") or {})).get("inline_json") or {})
        for row in rows
        if str(row.get("payload_schema_id", "")).strip() == "server.console.log.stub.v1"
    ]
    responses = [
        dict((dict(row.get("payload_ref") or {})).get("inline_json") or {})
        for row in rows
        if str(row.get("payload_schema_id", "")).strip() == "server.control.response.stub.v1"
    ]
    tick_stream = [
        dict((dict(row.get("payload_ref") or {})).get("inline_json") or {})
        for row in rows
        if str(row.get("payload_schema_id", "")).strip() == "server.tick_stream.stub.v1"
    ]
    if isinstance(controller, dict):
        controller["last_client_messages"] = [dict(row) for row in rows[-64:]]
    return {
        "result": "complete",
        "messages": rows,
        "log_events": logs,
        "control_responses": responses,
        "tick_stream": tick_stream,
    }


def request_local_server_control(
    controller: Mapping[str, object],
    *,
    request_kind: str,
    payload: Mapping[str, object] | None = None,
) -> dict:
    state = controller if isinstance(controller, dict) else {}
    client_transport = state.get("client_transport")
    if client_transport is None:
        return _refuse(
            REFUSAL_LOCAL_SERVER_CRASHED,
            "local singleplayer controller is not attached to a client transport",
            "Start the local singleplayer server before issuing control requests.",
            path="$.client_transport",
        )
    counter = int(state.get("control_request_counter", 0) or 0) + 1
    state["control_request_counter"] = int(counter)
    return send_client_control_request(
        client_transport=client_transport,
        request_id="ctrl.local.{}".format(int(counter)),
        request_kind=str(request_kind or "").strip(),
        payload=dict(payload or {}),
        sequence=1000 + int(counter),
    )


def run_local_server_ticks(controller: Mapping[str, object], *, ticks: int) -> dict:
    state = controller if isinstance(controller, dict) else {}
    boot = dict(state.get("server_boot_payload") or {})
    rows = []
    log_rows = []
    response_rows = []
    tick_stream_rows = []
    for _idx in range(max(0, int(ticks or 0))):
        step = advance_server_tick(boot)
        if str(step.get("result", "")) != "complete":
            return dict(step)
        messages = collect_local_client_messages(state)
        rows.append(
            {
                "tick": int(step.get("tick", 0) or 0),
                "proof_anchor_path": str(step.get("proof_anchor_path", "")).strip(),
                "log_count": len(list(messages.get("log_events") or [])),
                "control_response_count": len(list(messages.get("control_responses") or [])),
                "tick_stream_count": len(list(messages.get("tick_stream") or [])),
            }
        )
        log_rows.extend(list(messages.get("log_events") or []))
        response_rows.extend(list(messages.get("control_responses") or []))
        tick_stream_rows.extend(list(messages.get("tick_stream") or []))
    runtime = dict((dict(boot.get("runtime") or {})))
    server = dict(runtime.get("server") or {})
    return {
        "result": "complete",
        "ticks": rows,
        "log_events": log_rows,
        "control_responses": response_rows,
        "tick_stream": tick_stream_rows,
        "final_tick": int(server.get("network_tick", 0) or 0),
        "deterministic_fingerprint": canonical_sha256(rows),
    }


def restart_local_singleplayer(controller: Mapping[str, object]) -> dict:
    state = dict(controller or {})
    launch_spec = dict(state.get("launch_spec") or {})
    return start_local_singleplayer(
        repo_root=str(launch_spec.get("repo_root", "")).strip(),
        seed=str(launch_spec.get("seed", "")).strip(),
        profile_bundle_path=str(launch_spec.get("profile_bundle_path", "")).strip(),
        pack_lock_path=str(launch_spec.get("pack_lock_path", "")).strip(),
        server_config_id=str(launch_spec.get("server_config_id", "")).strip(),
        authority_mode=str(launch_spec.get("authority_mode", "")).strip(),
        save_id=str(launch_spec.get("save_id", "")).strip(),
        session_spec_path=os.path.join(
            str(launch_spec.get("repo_root", "")).strip(),
            str(launch_spec.get("session_spec_path", "")).replace("/", os.sep),
        ),
    )


def supervise_spawned_server_process(
    *,
    repo_root: str,
    process_spec: Mapping[str, object],
    session_spec: Mapping[str, object] | None = None,
    save_id: str = "",
    max_polls: int = LOCAL_READY_POLL_ITERATIONS,
) -> dict:
    repo_root_abs = _repo_root_abs(repo_root)
    spawned = spawn_process(process_spec)
    if str(spawned.get("result", "")) != "complete":
        return dict(spawned)
    process = spawned.get("process")
    status = {}
    for _idx in range(max(1, int(max_polls or 1))):
        status = poll_process(process)
        if str(status.get("result", "")) == "exited":
            break
    if str(status.get("result", "")) != "exited":
        try:
            process.communicate(timeout=0.25)
        except subprocess.TimeoutExpired:
            return {"result": "running", "pid": int(status.get("pid", 0) or 0)}
        status = poll_process(process)
        if str(status.get("result", "")) != "exited":
            return {"result": "running", "pid": int(status.get("pid", 0) or 0)}
    output = collect_process_output(process)
    last_logs = []
    last_logs.extend(str(output.get("stdout_text", "")).splitlines())
    last_logs.extend(str(output.get("stderr_text", "")).splitlines())
    diag_path = _write_diag_stub(
        repo_root=repo_root_abs,
        save_id=str(save_id or (dict(session_spec or {})).get("save_id", "")).strip(),
        session_spec=dict(session_spec or {}),
        launch_spec=dict(process_spec),
        reason_code=REFUSAL_LOCAL_SERVER_CRASHED,
        failure_phase="spawned_process_exit",
        exit_code=int(output.get("exit_code", 0) or 0),
        last_logs=last_logs[-LOCAL_DIAG_LOG_LIMIT:],
    )
    return {
        "result": "complete",
        "exit_code": int(output.get("exit_code", 0) or 0),
        "diag_stub_path": diag_path,
        "stdout_text": str(output.get("stdout_text", "")),
        "stderr_text": str(output.get("stderr_text", "")),
    }
