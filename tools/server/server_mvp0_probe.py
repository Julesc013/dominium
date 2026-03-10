"""Deterministic SERVER-MVP-0 probe helpers for replay and TestX reuse."""

from __future__ import annotations

import json
import os
import sys
from typing import Callable, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.net.transport.loopback import reset_loopback_state  # noqa: E402
from src.server.net.loopback_transport import (  # noqa: E402
    accept_loopback_connection,
    create_loopback_listener,
    send_client_hello,
)
from src.server.runtime.tick_loop import run_server_ticks  # noqa: E402
from src.server.server_boot import boot_server_runtime, materialize_server_session, submit_client_intent  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.sessionx.common import write_canonical_json  # noqa: E402
from tools.xstack.sessionx.net_protocol import decode_proto_message  # noqa: E402


DEFAULT_SERVER_MVP0_SEED = 0
DEFAULT_SERVER_TICKS = 8
DEFAULT_SERVER_CONFIG_ID = "server.mvp_default"
DEFAULT_PACK_LOCK_REL = os.path.join("locks", "pack_lock.mvp_default.json")
EXPECTED_UNAUTHORIZED_REASON_CODE = "refusal.client.unauthorized"


def _ensure_repo_root(repo_root: str) -> str:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or REPO_ROOT_HINT)))
    if repo_root_abs not in sys.path:
        sys.path.insert(0, repo_root_abs)
    return repo_root_abs


def _read_json(path: str) -> dict:
    return json.load(open(path, "r", encoding="utf-8"))


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    write_canonical_json(path, dict(payload))


def _pack_lock_abs(repo_root: str, pack_lock_path: str = "") -> str:
    token = str(pack_lock_path or DEFAULT_PACK_LOCK_REL).strip()
    if os.path.isabs(token):
        return os.path.normpath(token)
    return os.path.normpath(os.path.join(repo_root, token.replace("/", os.sep)))


def _artifact_paths(repo_root: str, created: Mapping[str, object]) -> tuple[str, str, str]:
    session_spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    save_id = str(created.get("save_id", "")).strip()
    save_dir = os.path.join(repo_root, "saves", save_id)
    return session_spec_abs, save_dir, save_id


def materialize_server_fixture(
    repo_root: str,
    *,
    save_suffix: str,
    seed: int = DEFAULT_SERVER_MVP0_SEED,
    pack_lock_path: str = "",
    server_config_id: str = DEFAULT_SERVER_CONFIG_ID,
) -> dict:
    repo_root_abs = _ensure_repo_root(repo_root)
    reset_loopback_state()
    save_id = "save.server_mvp0.{}".format(str(save_suffix).strip() or "fixture")
    created = materialize_server_session(
        repo_root=repo_root_abs,
        seed=str(int(seed)),
        profile_bundle_path="",
        pack_lock_path=_pack_lock_abs(repo_root_abs, pack_lock_path),
        server_config_id=str(server_config_id or DEFAULT_SERVER_CONFIG_ID),
        authority_mode="dev",
        save_id=save_id,
    )
    session_spec_abs = ""
    save_dir = ""
    if str(created.get("result", "")) == "complete":
        session_spec_abs, save_dir, save_id = _artifact_paths(repo_root_abs, created)
    return {
        "repo_root": repo_root_abs,
        "created": dict(created),
        "session_spec_abs": session_spec_abs,
        "save_dir": save_dir,
        "save_id": save_id,
        "pack_lock_abs": _pack_lock_abs(repo_root_abs, pack_lock_path),
    }


def boot_server_fixture(
    repo_root: str,
    *,
    save_suffix: str,
    seed: int = DEFAULT_SERVER_MVP0_SEED,
    pack_lock_path: str = "",
    server_config_id: str = DEFAULT_SERVER_CONFIG_ID,
    session_mutator: Callable[[dict], dict | None] | None = None,
) -> dict:
    fixture = materialize_server_fixture(
        repo_root,
        save_suffix=save_suffix,
        seed=seed,
        pack_lock_path=pack_lock_path,
        server_config_id=server_config_id,
    )
    created = dict(fixture.get("created") or {})
    if str(created.get("result", "")) != "complete":
        return dict(fixture, boot=dict(created))
    session_spec_abs = str(fixture.get("session_spec_abs", "")).strip()
    if session_mutator is not None:
        payload = _read_json(session_spec_abs)
        mutated = session_mutator(dict(payload))
        _write_json(session_spec_abs, dict(mutated if isinstance(mutated, dict) else payload))
    boot = boot_server_runtime(
        repo_root=str(fixture.get("repo_root", "")),
        session_spec_path=session_spec_abs,
        pack_lock_path=str(fixture.get("pack_lock_abs", "")),
        server_config_id=str(server_config_id or DEFAULT_SERVER_CONFIG_ID),
    )
    if str(boot.get("result", "")) == "complete":
        boot["repo_root"] = str(fixture.get("repo_root", ""))
    return dict(fixture, boot=dict(boot))


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


def connect_loopback_client(
    boot_payload: Mapping[str, object],
    *,
    client_peer_id: str = "peer.client.loopback",
    account_id: str = "account.server_mvp0",
) -> dict:
    listener = create_loopback_listener(boot_payload)
    if str(listener.get("result", "")) != "complete":
        return {"result": "refused", "listener": dict(listener)}
    hello = send_client_hello(
        endpoint=str(listener.get("endpoint", "")),
        client_peer_id=str(client_peer_id),
        account_id=str(account_id),
    )
    if str(hello.get("result", "")) != "complete":
        return {"result": "refused", "listener": dict(listener), "hello": dict(hello)}
    accepted = accept_loopback_connection(boot_payload)
    if str(accepted.get("result", "")) != "complete":
        return {"result": "refused", "listener": dict(listener), "hello": dict(hello), "accepted": dict(accepted)}
    client_transport = hello.get("client_transport")
    ack_proto = {}
    if client_transport is not None:
        ack_proto = _decode_message(str((dict(boot_payload or {})).get("repo_root", "")), client_transport.recv())
    return {
        "result": "complete",
        "listener": dict(listener),
        "hello": {
            "result": str(hello.get("result", "")).strip(),
            "connection_id": str(hello.get("connection_id", "")).strip(),
            "client_peer_id": str(hello.get("client_peer_id", "")).strip(),
            "hello_payload": dict(hello.get("hello_payload") or {}),
        },
        "accepted": dict(accepted),
        "client_transport": client_transport,
        "ack_proto": ack_proto,
    }


def drain_client_messages(repo_root: str, client_transport: object) -> list[dict]:
    rows: list[dict] = []
    if client_transport is None:
        return rows
    while True:
        recv_result = client_transport.recv()
        if str((dict(recv_result or {})).get("result", "")).strip() != "complete":
            break
        proto_message = _decode_message(repo_root, recv_result)
        if not proto_message:
            break
        rows.append(proto_message)
    return rows


def run_server_window(
    repo_root: str = REPO_ROOT_HINT,
    *,
    seed: int = DEFAULT_SERVER_MVP0_SEED,
    ticks: int = DEFAULT_SERVER_TICKS,
    save_suffix: str = "replay",
    with_client: bool = True,
) -> dict:
    repo_root_abs = _ensure_repo_root(repo_root)
    fixture = boot_server_fixture(repo_root_abs, save_suffix=save_suffix, seed=seed)
    boot = dict(fixture.get("boot") or {})
    if str(boot.get("result", "")) != "complete":
        return {
            "result": str(boot.get("result", "refused")).strip() or "refused",
            "boot": boot,
            "deterministic_fingerprint": canonical_sha256({"boot": boot, "ticks": int(ticks), "with_client": bool(with_client)}),
        }

    handshake = {"result": "empty"}
    client_transport = None
    if with_client:
        handshake = connect_loopback_client(boot)
        if str(handshake.get("result", "")) != "complete":
            safe_handshake = {
                "result": str(handshake.get("result", "")).strip(),
                "listener": dict(handshake.get("listener") or {}),
                "hello": {
                    "result": str((dict(handshake.get("hello") or {})).get("result", "")).strip(),
                    "connection_id": str((dict(handshake.get("hello") or {})).get("connection_id", "")).strip(),
                    "client_peer_id": str((dict(handshake.get("hello") or {})).get("client_peer_id", "")).strip(),
                },
                "accepted": dict(handshake.get("accepted") or {}),
            }
            return {
                "result": "refused",
                "boot": boot,
                "handshake": safe_handshake,
                "deterministic_fingerprint": canonical_sha256({"boot": boot, "handshake": safe_handshake}),
            }
        client_transport = handshake.get("client_transport")

    tick_report = run_server_ticks(boot, int(max(0, int(ticks or 0))))
    runtime = dict(boot.get("runtime") or {})
    server = dict(runtime.get("server") or {})
    meta = dict(runtime.get("server_mvp") or {})
    connections = dict(runtime.get("server_mvp_connections") or {})
    anchors = [dict(row) for row in list(runtime.get("server_mvp_proof_anchors") or []) if isinstance(row, dict)]
    client_messages = drain_client_messages(repo_root_abs, client_transport)
    tick_stream_messages = [
        row
        for row in client_messages
        if str(row.get("msg_type", "")).strip() == "payload"
        and str(row.get("payload_schema_id", "")).strip() == "server.tick_stream.stub.v1"
    ]
    anchor_ticks = [int(row.get("tick", 0) or 0) for row in anchors]
    summary = {
        "result": "complete" if str(tick_report.get("result", "")) == "complete" else str(tick_report.get("result", "")).strip(),
        "save_id": str(fixture.get("save_id", "")).strip(),
        "tick_count_requested": int(ticks),
        "final_tick": int(server.get("network_tick", 0) or 0),
        "listener_endpoint": str(meta.get("listener_endpoint", "")).strip(),
        "client_count": len(connections),
        "connection_ids": sorted(str(item) for item in connections.keys()),
        "handshake": {
            "connection_id": str((dict(handshake.get("accepted") or {})).get("connection_id", "")).strip(),
            "account_id": str((dict(handshake.get("accepted") or {})).get("account_id", "")).strip(),
            "ack_msg_type": str((dict(handshake.get("ack_proto") or {})).get("msg_type", "")).strip(),
            "ack_payload_schema_id": str((dict(handshake.get("ack_proto") or {})).get("payload_schema_id", "")).strip(),
            "session_info": dict((dict((dict(handshake.get("ack_proto") or {}).get("payload_ref") or {})).get("inline_json") or {}).get("session_info") or {}),
            "authority_context_created": bool((dict(handshake.get("accepted") or {})).get("authority_context")),
        },
        "proof_anchor_interval_ticks": int(meta.get("proof_anchor_interval_ticks", 0) or 0),
        "proof_anchor_ticks": anchor_ticks,
        "proof_anchor_hashes": [canonical_sha256(row) for row in anchors],
        "proof_anchor_contract_hashes": [
            {
                "contract_bundle_hash": str(row.get("contract_bundle_hash", "")).strip(),
                "semantic_contract_registry_hash": str(row.get("semantic_contract_registry_hash", "")).strip(),
                "pack_lock_hash": str(row.get("pack_lock_hash", "")).strip(),
            }
            for row in anchors
        ],
        "tick_stream_count": len(tick_stream_messages),
        "tick_stream_ticks": [
            int((dict((dict(row.get("payload_ref") or {})).get("inline_json") or {})).get("tick", 0) or 0)
            for row in tick_stream_messages
        ],
        "tick_hash": str(server.get("last_tick_hash", "")).strip(),
        "overlay_manifest_hash": str(meta.get("overlay_manifest_hash", "")).strip(),
        "contract_bundle_hash": str(meta.get("contract_bundle_hash", "")).strip(),
        "semantic_contract_registry_hash": str(meta.get("semantic_contract_registry_hash", "")).strip(),
        "mod_policy_id": str(meta.get("mod_policy_id", "")).strip(),
        "deterministic_fingerprint": "",
    }
    summary["cross_platform_server_hash"] = canonical_sha256(
        {
            "final_tick": int(summary.get("final_tick", 0)),
            "connection_ids": list(summary.get("connection_ids") or []),
            "proof_anchor_hashes": list(summary.get("proof_anchor_hashes") or []),
            "tick_hash": str(summary.get("tick_hash", "")).strip(),
            "mod_policy_id": str(summary.get("mod_policy_id", "")).strip(),
            "contract_bundle_hash": str(summary.get("contract_bundle_hash", "")).strip(),
            "semantic_contract_registry_hash": str(summary.get("semantic_contract_registry_hash", "")).strip(),
        }
    )
    summary["deterministic_fingerprint"] = canonical_sha256(dict(summary, deterministic_fingerprint=""))
    return summary


def verify_server_window_replay(repo_root: str = REPO_ROOT_HINT) -> dict:
    repo_root_abs = _ensure_repo_root(repo_root)
    first = run_server_window(repo_root_abs, save_suffix="verify")
    second = run_server_window(repo_root_abs, save_suffix="verify")
    stable = canonical_sha256(first) == canonical_sha256(second)
    return {
        "result": "complete" if stable else "refused",
        "stable": bool(stable),
        "first_report": first,
        "second_report": second,
        "deterministic_fingerprint": canonical_sha256({"first": first, "second": second}),
    }


def unauthorized_intent_report(repo_root: str = REPO_ROOT_HINT) -> dict:
    repo_root_abs = _ensure_repo_root(repo_root)
    fixture = boot_server_fixture(repo_root_abs, save_suffix="authority")
    boot = dict(fixture.get("boot") or {})
    if str(boot.get("result", "")) != "complete":
        return {"result": "refused", "boot": boot}
    refusal_result = submit_client_intent(
        boot,
        connection_id="loop.conn.unauthorized",
        intent={"intent_id": "intent.server_mvp0.unauthorized", "target": "body.emb.test", "process_id": "process.agent_move"},
    )
    return {
        "result": str(refusal_result.get("result", "")).strip(),
        "reason_code": str((dict(refusal_result.get("refusal") or {})).get("reason_code", "")).strip(),
        "expected_reason_code": EXPECTED_UNAUTHORIZED_REASON_CODE,
        "deterministic_fingerprint": canonical_sha256(refusal_result),
    }


__all__ = [
    "DEFAULT_SERVER_CONFIG_ID",
    "DEFAULT_SERVER_MVP0_SEED",
    "DEFAULT_SERVER_TICKS",
    "boot_server_fixture",
    "connect_loopback_client",
    "drain_client_messages",
    "materialize_server_fixture",
    "run_server_window",
    "unauthorized_intent_report",
    "verify_server_window_replay",
]
