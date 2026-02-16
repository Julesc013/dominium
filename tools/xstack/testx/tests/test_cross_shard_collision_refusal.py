"""STRICT test: SRZ hybrid cross-shard body collisions are refused by default policy."""

from __future__ import annotations

import sys


TEST_ID = "testx.embodiment.cross_shard_collision_refusal"
TEST_TAGS = ["strict", "net", "session", "collision", "embodiment", "srz"]


def _envelope(lock_payload: dict, law_profile_id: str) -> dict:
    registry_hashes = dict(lock_payload.get("registries") or {})
    pack_lock_hash = str(lock_payload.get("pack_lock_hash", ""))
    return {
        "schema_version": "1.0.0",
        "envelope_id": "env.peer.client.body.cross_shard.tick.1.seq.0001",
        "authority_summary": {
            "authority_origin": "client",
            "law_profile_id": str(law_profile_id),
        },
        "source_peer_id": "peer.client.hybrid.alpha",
        "source_shard_id": "shard.0",
        "target_shard_id": "auto",
        "submission_tick": 1,
        "deterministic_sequence_number": 1,
        "intent_id": "intent.body.cross_shard.collision.001",
        "payload_schema_id": "dominium.intent.process.v1",
        "payload": {
            "process_id": "process.body_move_attempt",
            "inputs": {
                "body_id": "body.local",
                "delta_transform_mm": {"x": 100, "y": 0, "z": 0},
                "dt_ticks": 1,
            },
        },
        "pack_lock_hash": pack_lock_hash,
        "registry_hashes": registry_hashes,
        "signature": "",
        "extensions": {},
    }


def _seed_bodies(runtime: dict) -> None:
    state = dict(runtime.get("global_state") or {})
    state["body_assemblies"] = [
        {
            "assembly_id": "body.local",
            "owner_assembly_id": "object.earth",
            "shape_type": "capsule",
            "shape_parameters": {
                "radius_mm": 500,
                "height_mm": 1200,
                "half_extents_mm": {"x": 0, "y": 0, "z": 0},
                "vertex_ref_id": "",
            },
            "collision_layer": "layer.default",
            "dynamic": True,
            "ghost": False,
            "transform_mm": {"x": 0, "y": 0, "z": 0},
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
        },
        {
            "assembly_id": "body.foreign",
            "owner_assembly_id": "object.luna",
            "shape_type": "capsule",
            "shape_parameters": {
                "radius_mm": 500,
                "height_mm": 1200,
                "half_extents_mm": {"x": 0, "y": 0, "z": 0},
                "vertex_ref_id": "",
            },
            "collision_layer": "layer.default",
            "dynamic": True,
            "ghost": False,
            "transform_mm": {"x": 600, "y": 0, "z": 0},
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
        },
    ]
    state["collision_state"] = {
        "last_tick_resolved_pairs": [],
        "last_tick_unresolved_pairs": [],
        "last_tick_pair_count": 0,
        "last_tick_anchor": "",
    }
    runtime["global_state"] = state


def _run_once(repo_root: str):
    from src.net.policies.policy_srz_hybrid import run_hybrid_simulation
    from tools.xstack.testx.tests.net_hybrid_testlib import clone_runtime, prepare_hybrid_runtime_fixture

    fixture = prepare_hybrid_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.embodiment.cross_shard_collision_refusal",
        client_peer_id="peer.client.hybrid.alpha",
    )
    runtime = clone_runtime(fixture)
    _seed_bodies(runtime)

    clients = dict(runtime.get("clients") or {})
    client = dict(clients.get("peer.client.hybrid.alpha") or {})
    authority_context = dict(client.get("authority_context") or {})
    entitlements = sorted(
        set(
            str(item).strip()
            for item in list(authority_context.get("entitlements") or []) + ["entitlement.control.possess"]
            if str(item).strip()
        )
    )
    authority_context["entitlements"] = entitlements
    client["authority_context"] = authority_context
    clients["peer.client.hybrid.alpha"] = client
    runtime["clients"] = clients

    lock_payload = dict(fixture.get("lock_payload") or {})
    law_profile_id = str((fixture.get("law_profile") or {}).get("law_profile_id", ""))
    envelope = _envelope(lock_payload=lock_payload, law_profile_id=law_profile_id)
    ran = run_hybrid_simulation(
        repo_root=repo_root,
        runtime=runtime,
        envelopes=[envelope],
        ticks=1,
    )
    return {"result": ran, "runtime": runtime}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once(repo_root=repo_root)
    second = _run_once(repo_root=repo_root)
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "cross-shard collision run must complete with deterministic refusal entries"}

    first_runtime = dict(first.get("runtime") or {})
    second_runtime = dict(second.get("runtime") or {})
    first_server = dict(first_runtime.get("server") or {})
    second_server = dict(second_runtime.get("server") or {})
    first_refusals = [
        dict(row)
        for row in list(first_server.get("refusals") or [])
        if str(row.get("reason_code", "")) == "refusal.control.cross_shard_collision_forbidden"
    ]
    second_refusals = [
        dict(row)
        for row in list(second_server.get("refusals") or [])
        if str(row.get("reason_code", "")) == "refusal.control.cross_shard_collision_forbidden"
    ]
    if not first_refusals or not second_refusals:
        return {"status": "fail", "message": "expected refusal.control.cross_shard_collision_forbidden was not recorded"}
    if first_refusals != second_refusals:
        return {"status": "fail", "message": "cross-shard collision refusal records must be deterministic"}

    first_hash = str(first_result.get("final_composite_hash", ""))
    second_hash = str(second_result.get("final_composite_hash", ""))
    if first_hash != second_hash:
        return {"status": "fail", "message": "cross-shard collision refusal path must preserve deterministic final hash"}
    return {"status": "pass", "message": "cross-shard collision refusal determinism check passed"}

