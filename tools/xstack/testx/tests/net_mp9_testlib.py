"""Shared MP-9 deterministic full-stack scenario helpers."""

from __future__ import annotations

import copy
from typing import Dict, List, Tuple

from src.net.testing import DeterministicNetDisorderSim
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.process_runtime import execute_intent
from tools.xstack.sessionx.srz import DEFAULT_SHARD_ID, build_single_shard, composite_hash, per_tick_hash


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _state_tick(state: dict) -> int:
    sim = state.get("simulation_time")
    if not isinstance(sim, dict):
        return 0
    return max(0, _as_int(sim.get("tick", 0), 0))


def _queue_sort_key(envelope: dict) -> Tuple[int, str, str, int, str]:
    return (
        _as_int(envelope.get("submission_tick", 0), 0),
        str(envelope.get("target_shard_id", "")),
        str(envelope.get("source_peer_id", "")),
        _as_int(envelope.get("deterministic_sequence_number", 0), 0),
        str(envelope.get("intent_id", "")),
    )


def _tick_hash(lock_payload: dict, state: dict, last_tick_hash: str) -> str:
    shard = build_single_shard(
        universe_state=dict(state),
        authority_origin="server",
        compatibility_version="1.0.0",
        last_hash_anchor=str(last_tick_hash or ""),
    )
    tick_hash = per_tick_hash(
        universe_state=dict(state),
        shards=[shard],
        pack_lock_hash=str(lock_payload.get("pack_lock_hash", "")),
        registry_hashes=dict(lock_payload.get("registries") or {}),
        last_tick_hash=str(last_tick_hash or ""),
    )
    shard["last_hash_anchor"] = tick_hash
    return str(composite_hash([shard]))


def run_lockstep_full_stack(
    repo_root: str,
    *,
    save_id: str,
    ticks: int,
    disorder_profile_id: str,
    induce_divergence_tick: int = 0,
) -> Dict[str, object]:
    from src.net.policies.policy_lockstep import refusal_from_decision, validate_lockstep_envelope
    from tools.xstack.testx.tests.net_authoritative_testlib import prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id=str(save_id),
        client_peer_id="peer.client.alpha",
    )
    base_runtime = dict(fixture.get("runtime") or {})
    base_server = dict(base_runtime.get("server") or {})
    lock_payload = dict(fixture.get("lock_payload") or {})
    registry_payloads = dict(base_runtime.get("registry_payloads") or {})
    base_state = copy.deepcopy(dict(base_server.get("universe_state") or {}))
    law_profile = copy.deepcopy(dict(fixture.get("law_profile") or {}))
    authority = copy.deepcopy(dict(fixture.get("authority_context") or {}))

    server_tick = int(max(0, _state_tick(base_state)))
    peers = ["peer.client.alpha", "peer.client.beta"]
    peer_states = dict((peer, copy.deepcopy(base_state)) for peer in peers)
    peer_hashes = dict((peer, "") for peer in peers)
    peer_checkpoints = dict((peer, {int(server_tick): copy.deepcopy(base_state)}) for peer in peers)
    queue: List[dict] = []
    seen_ids: List[str] = []
    last_sequence_by_peer: Dict[str, int] = {}
    anchors: List[str] = []
    tick_lists: List[dict] = []
    server_checkpoints: Dict[int, dict] = {int(server_tick): copy.deepcopy(base_state)}
    resync_count = 0
    disorder = DeterministicNetDisorderSim(disorder_profile_id=str(disorder_profile_id))

    for _ in range(max(0, int(ticks))):
        submit_tick = int(server_tick + 1)
        outgoing = []
        for peer_index, peer_id in enumerate(peers):
            next_seq = _as_int(last_sequence_by_peer.get(peer_id, 0), 0) + 1
            outgoing.append(
                {
                    "schema_version": "1.0.0",
                    "envelope_id": "env.{}.tick.{}.seq.{}".format(peer_id, submit_tick, str(next_seq).zfill(4)),
                    "authority_summary": {"authority_origin": "client", "law_profile_id": str(law_profile.get("law_profile_id", ""))},
                    "source_peer_id": peer_id,
                    "source_shard_id": DEFAULT_SHARD_ID,
                    "target_shard_id": DEFAULT_SHARD_ID,
                    "submission_tick": submit_tick,
                    "deterministic_sequence_number": int(next_seq),
                    "intent_id": "intent.lockstep.{}.tick.{}".format(peer_id.replace(".", "_"), submit_tick),
                    "payload_schema_id": "dominium.intent.process.v1",
                    "payload": {
                        "process_id": "process.camera_move",
                        "inputs": {"delta_local_mm": {"x": int(2 + peer_index), "y": int(peer_index), "z": 0}, "dt_ticks": 1},
                    },
                    "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
                    "registry_hashes": dict(lock_payload.get("registries") or {}),
                    "signature": "",
                    "extensions": {},
                }
            )
        disorder.inject(channel_id="lockstep.client_to_server", tick=int(server_tick), messages=outgoing)
        delivered = disorder.deliver(channel_id="lockstep.client_to_server", tick=int(server_tick))
        for envelope in sorted((dict(row) for row in (delivered.get("messages") or []) if isinstance(row, dict)), key=_queue_sort_key):
            decision = validate_lockstep_envelope(
                repo_root=repo_root,
                runtime={"server": {"seen_envelope_ids": seen_ids, "last_sequence_by_peer": last_sequence_by_peer}, "clients": dict((peer, {}) for peer in peers)},
                envelope=dict(envelope),
                current_tick=int(server_tick),
                lead_ticks=1,
            )
            if str(decision.get("result", "")) != "complete":
                mapped = refusal_from_decision(
                    decision=decision,
                    peer_id=str(envelope.get("source_peer_id", "")),
                    fallback_reason="refusal.net.envelope_invalid",
                    message="lockstep envelope ingress refused by deterministic anti-cheat gate",
                    remediation="Submit monotonic sequence and valid lockstep tick target.",
                    path="$.intent_envelope",
                )
                if str(mapped.get("result", "")) == "complete":
                    continue
                return mapped
            queue.append(dict(envelope))
            queue = sorted(queue, key=_queue_sort_key)
            seen_ids = sorted(set(seen_ids + [str(envelope.get("envelope_id", ""))]))
            last_sequence_by_peer[str(envelope.get("source_peer_id", ""))] = _as_int(envelope.get("deterministic_sequence_number", 0), 0)

        due = [dict(row) for row in queue if _as_int(row.get("submission_tick", 0), 0) <= submit_tick]
        queue = [dict(row) for row in queue if _as_int(row.get("submission_tick", 0), 0) > submit_tick]
        due = sorted(due, key=_queue_sort_key)

        for envelope in due:
            payload = dict(envelope.get("payload") or {})
            intent = {"intent_id": str(envelope.get("intent_id", "")), "process_id": str(payload.get("process_id", "")), "inputs": dict(payload.get("inputs") or {})}
            executed = execute_intent(
                state=base_state,
                intent=intent,
                law_profile=dict(law_profile),
                authority_context=dict(authority),
                navigation_indices=dict(registry_payloads),
                policy_context=dict(registry_payloads),
            )
            if str(executed.get("result", "")) != "complete":
                return {"result": "refused", "refusal": dict(executed.get("refusal") or {})}
            for peer_id in peers:
                peer_exec = execute_intent(
                    state=peer_states[peer_id],
                    intent=intent,
                    law_profile=dict(law_profile),
                    authority_context=dict(authority),
                    navigation_indices=dict(registry_payloads),
                    policy_context=dict(registry_payloads),
                )
                if str(peer_exec.get("result", "")) != "complete":
                    return {"result": "refused", "refusal": dict(peer_exec.get("refusal") or {})}

        server_hash = _tick_hash(lock_payload=lock_payload, state=base_state, last_tick_hash=str(anchors[-1] if anchors else ""))
        anchors.append(server_hash)
        tick_lists.append({"tick": int(submit_tick), "envelopes": due})
        server_checkpoints[int(submit_tick)] = copy.deepcopy(base_state)
        for peer_id in peers:
            peer_hashes[peer_id] = _tick_hash(lock_payload=lock_payload, state=peer_states[peer_id], last_tick_hash=str(peer_hashes.get(peer_id, "")))
            peer_checkpoints[peer_id][int(submit_tick)] = copy.deepcopy(peer_states[peer_id])

        if int(induce_divergence_tick) > 0 and int(submit_tick) == int(induce_divergence_tick):
            camera_rows = list(peer_states["peer.client.beta"].get("camera_assemblies") or [])
            for row in camera_rows:
                if isinstance(row, dict) and str(row.get("assembly_id", "")) == "camera.main":
                    pos = dict(row.get("position_mm") or {"x": 0, "y": 0, "z": 0})
                    pos["x"] = _as_int(pos.get("x", 0), 0) + 1
                    row["position_mm"] = pos
            peer_states["peer.client.beta"]["camera_assemblies"] = camera_rows
            peer_states["peer.client.beta"] = copy.deepcopy(server_checkpoints.get(int(submit_tick - 1), {}))
            for row in sorted((dict(item) for item in tick_lists if isinstance(item, dict)), key=lambda item: _as_int(item.get("tick", 0), 0)):
                tick = _as_int(row.get("tick", 0), 0)
                if tick < int(induce_divergence_tick):
                    continue
                for envelope in sorted((dict(item) for item in (row.get("envelopes") or []) if isinstance(item, dict)), key=_queue_sort_key):
                    payload = dict(envelope.get("payload") or {})
                    intent = {"intent_id": str(envelope.get("intent_id", "")), "process_id": str(payload.get("process_id", "")), "inputs": dict(payload.get("inputs") or {})}
                    replayed = execute_intent(
                        state=peer_states["peer.client.beta"],
                        intent=intent,
                        law_profile=dict(law_profile),
                        authority_context=dict(authority),
                        navigation_indices=dict(registry_payloads),
                        policy_context=dict(registry_payloads),
                    )
                    if str(replayed.get("result", "")) != "complete":
                        return {"result": "refused", "refusal": {"reason_code": "refusal.net.resync_checkpoint_missing"}}
            resync_count += 1

        server_tick = int(submit_tick)

    return {
        "result": "complete",
        "policy_id": "policy.net.lockstep",
        "anchors": anchors,
        "final_composite_hash": str(anchors[-1] if anchors else ""),
        "peer_hashes": dict((peer, str(peer_hashes.get(peer, ""))) for peer in sorted(peer_hashes.keys())),
        "resync_count": int(resync_count),
        "runtime_fingerprint": canonical_sha256({"anchors": anchors, "peer_hashes": peer_hashes, "resync_count": int(resync_count)}),
    }


def run_authoritative_full_stack(
    repo_root: str,
    *,
    save_id: str,
    ticks: int,
    disorder_profile_id: str,
) -> Dict[str, object]:
    from src.net.policies.policy_server_authoritative import (
        POLICY_ID_SERVER_AUTHORITATIVE,
        advance_authoritative_tick,
        build_client_intent_envelope,
        join_client_midstream,
        prepare_server_authoritative_baseline,
        queue_intent_envelope,
        request_resync_snapshot,
    )
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(repo_root=repo_root, save_id=str(save_id), client_peer_id="peer.client.alpha")
    runtime = clone_runtime(fixture)
    baseline = prepare_server_authoritative_baseline(repo_root=repo_root, runtime=runtime)
    if str(baseline.get("result", "")) != "complete":
        return baseline
    joined = join_client_midstream(
        repo_root=repo_root,
        runtime=runtime,
        peer_id="peer.client.beta",
        authority_context=dict(fixture.get("authority_context") or {}),
        law_profile=dict(fixture.get("law_profile") or {}),
        lens_profile=dict(fixture.get("lens_profile") or {}),
        negotiated_policy_id=POLICY_ID_SERVER_AUTHORITATIVE,
        snapshot_id=str((baseline.get("snapshot") or {}).get("snapshot_id", "")),
    )
    if str(joined.get("result", "")) != "complete":
        return joined

    disorder = DeterministicNetDisorderSim(disorder_profile_id=str(disorder_profile_id))
    resync_count = 0
    for _ in range(max(0, int(ticks))):
        current_tick = _as_int(((runtime.get("server") or {}).get("network_tick", 0)), 0)
        alpha = build_client_intent_envelope(
            runtime=runtime,
            peer_id="peer.client.alpha",
            intent_id="intent.auth.alpha.tick.{}".format(int(current_tick + 1)),
            process_id="process.camera_move",
            inputs={"delta_local_mm": {"x": 3, "y": 0, "z": 0}, "dt_ticks": 1},
            submission_tick=int(current_tick + 1),
        )
        beta = build_client_intent_envelope(
            runtime=runtime,
            peer_id="peer.client.beta",
            intent_id="intent.auth.beta.tick.{}".format(int(current_tick + 1)),
            process_id="process.camera_move",
            inputs={"delta_local_mm": {"x": 0, "y": 2, "z": 0}, "dt_ticks": 1},
            submission_tick=int(current_tick + 1),
        )
        if str(alpha.get("result", "")) != "complete" or str(beta.get("result", "")) != "complete":
            return {"result": "refused", "refusal": {"reason_code": "refusal.net.envelope_invalid"}}
        disorder.inject(
            channel_id="authoritative.client_to_server",
            tick=int(current_tick),
            messages=[dict(alpha.get("envelope") or {}), dict(beta.get("envelope") or {})],
        )
        delivered = disorder.deliver(channel_id="authoritative.client_to_server", tick=int(current_tick))
        for envelope in sorted((dict(row) for row in (delivered.get("messages") or []) if isinstance(row, dict)), key=_queue_sort_key):
            queued = queue_intent_envelope(repo_root=repo_root, runtime=runtime, envelope=dict(envelope))
            if str(queued.get("result", "")) not in ("complete", "dropped"):
                return queued
        stepped = advance_authoritative_tick(repo_root=repo_root, runtime=runtime)
        if str(stepped.get("result", "")) != "complete":
            return stepped
        if int(stepped.get("tick", 0)) == 2:
            clients = dict(runtime.get("clients") or {})
            beta_client = dict(clients.get("peer.client.beta") or {})
            beta_client["last_perceived_hash"] = "deadbeef" * 8
            clients["peer.client.beta"] = beta_client
            runtime["clients"] = clients
            snapshots = list((runtime.get("server") or {}).get("snapshots") or [])
            snapshot_id = str((snapshots[-1] if snapshots else {}).get("snapshot_id", ""))
            repaired = request_resync_snapshot(repo_root=repo_root, runtime=runtime, peer_id="peer.client.beta", snapshot_id=snapshot_id)
            if str(repaired.get("result", "")) != "complete":
                return repaired
            resync_count += 1

    frames = list((runtime.get("server") or {}).get("hash_anchor_frames") or [])
    anchors = [str((row or {}).get("composite_hash", "")) for row in frames]
    return {
        "result": "complete",
        "policy_id": "policy.net.server_authoritative",
        "anchors": anchors,
        "final_composite_hash": str((anchors[-1] if anchors else "")),
        "resync_count": int(resync_count),
        "runtime_fingerprint": canonical_sha256({"anchors": anchors, "resync_count": int(resync_count)}),
    }


def run_hybrid_full_stack(
    repo_root: str,
    *,
    save_id: str,
    ticks: int,
    disorder_profile_id: str,
) -> Dict[str, object]:
    from src.net.policies.policy_srz_hybrid import (
        advance_hybrid_tick,
        build_client_intent_envelope,
        prepare_hybrid_baseline,
        queue_intent_envelope,
        request_hybrid_resync,
    )
    from tools.xstack.testx.tests.net_hybrid_testlib import clone_runtime, prepare_hybrid_runtime_fixture

    fixture = prepare_hybrid_runtime_fixture(repo_root=repo_root, save_id=str(save_id), client_peer_id="peer.client.hybrid.alpha")
    runtime = clone_runtime(fixture)
    baseline = prepare_hybrid_baseline(repo_root=repo_root, runtime=runtime)
    if str(baseline.get("result", "")) != "complete":
        return baseline

    disorder = DeterministicNetDisorderSim(disorder_profile_id=str(disorder_profile_id))
    resync_count = 0
    for _ in range(max(0, int(ticks))):
        current_tick = _as_int(((runtime.get("server") or {}).get("network_tick", 0)), 0)
        alpha = build_client_intent_envelope(
            runtime=runtime,
            peer_id="peer.client.hybrid.alpha",
            intent_id="intent.hybrid.alpha.tick.{}".format(int(current_tick + 1)),
            process_id="process.camera_teleport",
            inputs={"target_object_id": "object.earth"},
            submission_tick=int(current_tick + 1),
        )
        if str(alpha.get("result", "")) != "complete":
            return {"result": "refused", "refusal": {"reason_code": "refusal.net.envelope_invalid"}}
        disorder.inject(channel_id="hybrid.client_to_gateway", tick=int(current_tick), messages=[dict(alpha.get("envelope") or {})])
        delivered = disorder.deliver(channel_id="hybrid.client_to_gateway", tick=int(current_tick))
        for envelope in sorted((dict(row) for row in (delivered.get("messages") or []) if isinstance(row, dict)), key=_queue_sort_key):
            queued = queue_intent_envelope(repo_root=repo_root, runtime=runtime, envelope=dict(envelope))
            if str(queued.get("result", "")) not in ("complete", "dropped"):
                return queued
        stepped = advance_hybrid_tick(repo_root=repo_root, runtime=runtime)
        if str(stepped.get("result", "")) != "complete":
            return stepped
        if int(stepped.get("tick", 0)) == 2:
            clients = dict(runtime.get("clients") or {})
            alpha_client = dict(clients.get("peer.client.hybrid.alpha") or {})
            alpha_client["last_perceived_hash"] = "feedface" * 8
            clients["peer.client.hybrid.alpha"] = alpha_client
            runtime["clients"] = clients
            snapshots = list((runtime.get("server") or {}).get("snapshots") or [])
            snapshot_id = str((snapshots[-1] if snapshots else {}).get("snapshot_id", ""))
            repaired = request_hybrid_resync(
                repo_root=repo_root,
                runtime=runtime,
                peer_id="peer.client.hybrid.alpha",
                snapshot_id=snapshot_id,
            )
            if str(repaired.get("result", "")) != "complete":
                return repaired
            resync_count += 1

    frames = list((runtime.get("server") or {}).get("hash_anchor_frames") or [])
    anchors = [str((row or {}).get("composite_hash", "")) for row in frames]
    return {
        "result": "complete",
        "policy_id": "policy.net.srz_hybrid",
        "anchors": anchors,
        "final_composite_hash": str((anchors[-1] if anchors else "")),
        "resync_count": int(resync_count),
        "runtime_fingerprint": canonical_sha256({"anchors": anchors, "resync_count": int(resync_count)}),
    }
