"""STRICT test: hybrid cross-shard movement target is handled deterministically."""

from __future__ import annotations

import sys


TEST_ID = "testx.embodiment.cross_shard_move_handling"
TEST_TAGS = ["strict", "net", "session", "embodiment", "movement", "srz"]


def _seed_embodied_agent(runtime: dict) -> None:
    state = dict(runtime.get("global_state") or {})
    state["agent_states"] = [
        {
            "agent_id": "agent.alpha",
            "state_hash": "0" * 64,
            "body_id": "body.agent.alpha",
            "owner_peer_id": "peer.client.hybrid.alpha",
            "controller_id": "controller.alpha",
            "shard_id": "shard.0",
            "intent_scope_id": "",
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
        }
    ]
    state["controller_assemblies"] = [
        {
            "assembly_id": "controller.alpha",
            "controller_type": "script",
            "owner_peer_id": "peer.client.hybrid.alpha",
            "allowed_actions": ["control.action.possess_agent"],
            "binding_ids": ["binding.control.possess.agent_alpha"],
            "status": "active",
        }
    ]
    state["control_bindings"] = [
        {
            "binding_id": "binding.control.possess.agent_alpha",
            "controller_id": "controller.alpha",
            "binding_type": "possess",
            "target_id": "agent.alpha",
            "created_tick": 0,
            "active": True,
            "required_entitlements": ["entitlement.control.possess"],
        }
    ]
    state["body_assemblies"] = [
        {
            "assembly_id": "body.agent.alpha",
            "owner_assembly_id": "agent.alpha",
            "owner_agent_id": "agent.alpha",
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
            "shard_id": "shard.0",
            "transform_mm": {"x": 0, "y": 0, "z": 0},
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
        }
    ]
    state["collision_state"] = {
        "last_tick_resolved_pairs": [],
        "last_tick_unresolved_pairs": [],
        "last_tick_pair_count": 0,
        "last_tick_anchor": "",
    }
    runtime["global_state"] = state


def _run_once(repo_root: str):
    from net.policies.policy_srz_hybrid import run_hybrid_simulation
    from tools.xstack.testx.tests.net_hybrid_testlib import clone_runtime, prepare_hybrid_runtime_fixture

    fixture = prepare_hybrid_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.embodiment.cross_shard_move",
        client_peer_id="peer.client.hybrid.alpha",
    )
    runtime = clone_runtime(fixture)
    _seed_embodied_agent(runtime)
    lock_payload = dict(fixture.get("lock_payload") or {})
    law_profile_id = str((fixture.get("law_profile") or {}).get("law_profile_id", ""))
    envelope = {
        "schema_version": "1.0.0",
        "envelope_id": "env.peer.client.hybrid.move.cross_shard.tick.1.seq.0001",
        "authority_summary": {
            "authority_origin": "client",
            "law_profile_id": law_profile_id,
        },
        "source_peer_id": "peer.client.hybrid.alpha",
        "source_shard_id": "shard.0",
        "target_shard_id": "shard.1",
        "submission_tick": 1,
        "deterministic_sequence_number": 1,
        "intent_id": "intent.agent.move.cross_shard.001",
        "payload_schema_id": "dominium.intent.process.v1",
        "payload": {
            "process_id": "process.agent_move",
            "inputs": {
                "agent_id": "agent.alpha",
                "controller_id": "controller.alpha",
                "owner_peer_id": "peer.client.hybrid.alpha",
                "move_vector_local": {"x": 1000, "y": 0, "z": 0},
                "tick_duration": 1,
            },
        },
        "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
        "registry_hashes": dict(lock_payload.get("registries") or {}),
        "signature": "",
        "extensions": {},
    }
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
        return {"status": "fail", "message": "cross-shard move handling run must complete with deterministic refusal entries"}

    first_server = dict((first.get("runtime") or {}).get("server") or {})
    second_server = dict((second.get("runtime") or {}).get("server") or {})
    first_refusals = [
        dict(row)
        for row in list(first_server.get("refusals") or [])
        if str(row.get("reason_code", "")) in ("refusal.net.shard_target_invalid", "refusal.agent.boundary_cross_forbidden")
    ]
    second_refusals = [
        dict(row)
        for row in list(second_server.get("refusals") or [])
        if str(row.get("reason_code", "")) in ("refusal.net.shard_target_invalid", "refusal.agent.boundary_cross_forbidden")
    ]
    if not first_refusals or not second_refusals:
        return {"status": "fail", "message": "expected cross-shard movement refusal was not recorded"}
    if first_refusals != second_refusals:
        return {"status": "fail", "message": "cross-shard movement refusal records must be deterministic"}
    if str(first_result.get("final_composite_hash", "")) != str(second_result.get("final_composite_hash", "")):
        return {"status": "fail", "message": "cross-shard movement refusal path must preserve deterministic final hash"}
    return {"status": "pass", "message": "cross-shard movement handling determinism check passed"}
