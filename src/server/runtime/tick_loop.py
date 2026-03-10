"""SERVER-MVP-0 deterministic tick loop and replay-anchor wrappers."""

from __future__ import annotations

import os
from typing import Mapping

from src.net.policies.policy_server_authoritative import advance_authoritative_tick
from src.server.net.loopback_transport import broadcast_tick_stream, service_loopback_control_channel, stream_server_log_event
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.common import norm, write_canonical_json


def _runtime(server_boot_payload: Mapping[str, object] | None) -> dict:
    runtime = (dict(server_boot_payload or {})).get("runtime")
    if isinstance(runtime, dict):
        return runtime
    return {}


def _server_meta(runtime: Mapping[str, object] | None) -> dict:
    if not isinstance(runtime, dict):
        return {}
    meta = runtime.get("server_mvp")
    if isinstance(meta, dict):
        return meta
    meta = {}
    runtime["server_mvp"] = meta
    return meta


def _artifact_root_abs(repo_root: str, runtime: Mapping[str, object] | None) -> str:
    meta = _server_meta(runtime)
    rel = str(meta.get("artifact_root", "")).strip()
    if not rel:
        save_id = str((dict(runtime or {}).get("save_id", "")).strip() or "save.server.mvp")
        return os.path.join(repo_root, "build", "server", save_id)
    return os.path.join(repo_root, rel.replace("/", os.sep))


def build_server_proof_anchor(server_boot_payload: Mapping[str, object], step_payload: Mapping[str, object]) -> dict:
    runtime = _runtime(server_boot_payload)
    server = dict(runtime.get("server") or {})
    meta = _server_meta(runtime)
    connections = dict(runtime.get("server_mvp_connections") or {})
    frame = dict(step_payload.get("hash_anchor_frame") or {})
    bundle = dict(step_payload.get("control_proof_bundle") or {})
    tick = int(step_payload.get("tick", server.get("network_tick", 0)) or 0)
    negotiation_record_hashes = sorted(
        str((dict(row or {})).get("negotiation_record_hash", "")).strip()
        for row in connections.values()
        if str((dict(row or {})).get("negotiation_record_hash", "")).strip()
    )
    endpoint_descriptor_hashes = sorted(
        set(
            token
            for row in connections.values()
            for token in (
                str((dict(row or {})).get("client_endpoint_descriptor_hash", "")).strip(),
                str((dict(row or {})).get("server_endpoint_descriptor_hash", "")).strip(),
            )
            if token
        )
    )
    payload = {
        "schema_version": "1.0.0",
        "tick": int(tick),
        "pack_lock_hash": str(server.get("pack_lock_hash", "")).strip(),
        "contract_bundle_hash": str(meta.get("contract_bundle_hash", "")).strip(),
        "semantic_contract_registry_hash": str(meta.get("semantic_contract_registry_hash", "")).strip(),
        "mod_policy_id": str(meta.get("mod_policy_id", "")).strip(),
        "overlay_manifest_hash": str(meta.get("overlay_manifest_hash", "")).strip(),
        "tick_hash": str(server.get("last_tick_hash", "")).strip(),
        "hash_anchor_frame": frame,
        "control_proof_hash": str(bundle.get("control_proof_hash", "")).strip()
        or str((dict(frame.get("extensions") or {})).get("control_proof_hash", "")).strip(),
        "deterministic_fingerprint": "",
        "extensions": {
            "control_proof_bundle_ref": str(bundle.get("bundle_ref", "")).strip()
            or str((dict(frame.get("extensions") or {})).get("control_proof_bundle_ref", "")).strip(),
            "ledger_hash": str(step_payload.get("ledger_hash", "")).strip(),
            "official.negotiation_record_hashes": negotiation_record_hashes,
            "official.endpoint_descriptor_hashes": endpoint_descriptor_hashes,
        },
    }
    fingerprint_payload = dict(payload)
    fingerprint_payload["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = canonical_sha256(fingerprint_payload)
    return payload


def advance_server_tick(
    server_boot_payload: Mapping[str, object],
    *,
    emit_anchor: bool = True,
    stream_ticks: bool = True,
) -> dict:
    runtime = _runtime(server_boot_payload)
    repo_root = str((dict(server_boot_payload or {})).get("repo_root", "")).strip()
    control_channel = service_loopback_control_channel(server_boot_payload)
    step = advance_authoritative_tick(repo_root=repo_root, runtime=runtime)
    if str(step.get("result", "")) != "complete":
        return dict(step)

    tick = int(step.get("tick", 0) or 0)
    meta = _server_meta(runtime)
    interval = int(meta.get("proof_anchor_interval_ticks", 1) or 1)
    proof_anchor = {}
    proof_anchor_path = ""
    if emit_anchor and int(tick) % max(1, interval) == 0:
        proof_anchor = build_server_proof_anchor(server_boot_payload, step)
        anchor_dir = os.path.join(_artifact_root_abs(repo_root, runtime), "proof_anchors")
        os.makedirs(anchor_dir, exist_ok=True)
        proof_anchor_abs = os.path.join(anchor_dir, "anchor.tick.{}.json".format(int(tick)))
        write_canonical_json(proof_anchor_abs, proof_anchor)
        runtime_rows = list(runtime.get("server_mvp_proof_anchors") or [])
        runtime_rows.append(dict(proof_anchor))
        runtime["server_mvp_proof_anchors"] = sorted(
            (dict(row) for row in runtime_rows if isinstance(row, dict)),
            key=lambda row: int(row.get("tick", 0) or 0),
        )
        proof_anchor_path = norm(os.path.relpath(proof_anchor_abs, repo_root))
        stream_server_log_event(
            server_boot_payload,
            tick=int(tick),
            level="info",
            message="proof anchor emitted",
            source="server.tick_loop",
            message_key="server.proof_anchor.emitted",
            params={"proof_anchor_path": proof_anchor_path},
        )

    tick_stream = {}
    if stream_ticks:
        tick_stream = broadcast_tick_stream(
            server_boot_payload,
            tick=int(tick),
            tick_hash=str((dict(runtime.get("server") or {})).get("last_tick_hash", "")).strip(),
        )
    log_event = stream_server_log_event(
        server_boot_payload,
        tick=int(tick),
        level="info",
        message="server authoritative tick advanced",
        source="server.tick_loop",
        message_key="server.tick.advanced",
        params={
            "processed_envelope_count": int(len(list(step.get("processed_envelopes") or []))),
            "tick_hash": str((dict(runtime.get("server") or {})).get("last_tick_hash", "")).strip(),
        },
    )
    return {
        "result": "complete",
        "tick": int(tick),
        "processed_envelopes": list(step.get("processed_envelopes") or []),
        "control_channel": dict(control_channel),
        "proof_anchor": dict(proof_anchor),
        "proof_anchor_path": proof_anchor_path,
        "tick_stream": dict(tick_stream),
        "log_event": dict(log_event),
        "hash_anchor_frame": dict(step.get("hash_anchor_frame") or {}),
        "control_proof_bundle": dict(step.get("control_proof_bundle") or {}),
    }


def run_server_ticks(server_boot_payload: Mapping[str, object], ticks: int) -> dict:
    rows = []
    for _idx in range(max(0, int(ticks or 0))):
        step = advance_server_tick(server_boot_payload)
        if str(step.get("result", "")) != "complete":
            return dict(step)
        rows.append(
            {
                "tick": int(step.get("tick", 0) or 0),
                "proof_anchor_path": str(step.get("proof_anchor_path", "")).strip(),
                "hash_anchor_frame_hash": canonical_sha256(dict(step.get("hash_anchor_frame") or {})),
            }
        )
    return {
        "result": "complete",
        "ticks": rows,
        "final_tick": int(rows[-1]["tick"]) if rows else int((dict(_runtime(server_boot_payload).get("server") or {})).get("network_tick", 0) or 0),
        "deterministic_fingerprint": canonical_sha256(rows),
    }
