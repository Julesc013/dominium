"""STRICT test: movement anti-cheat event emission is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.embodiment.movement_anti_cheat_event"
TEST_TAGS = ["strict", "net", "anti_cheat", "embodiment", "movement"]


def _seed_embodied_agent(runtime: dict) -> None:
    server = dict(runtime.get("server") or {})
    state = dict(server.get("universe_state") or {})
    state["agent_states"] = [
        {
            "agent_id": "agent.alpha",
            "state_hash": "0" * 64,
            "body_id": "body.agent.alpha",
            "owner_peer_id": "peer.client.alpha",
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
            "owner_peer_id": "peer.client.alpha",
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
    server["universe_state"] = state
    runtime["server"] = server


def _movement_events(runtime: dict) -> list:
    rows = []
    server = dict(runtime.get("server") or {})
    for row in list(server.get("anti_cheat_events") or []):
        if not isinstance(row, dict):
            continue
        reason_code = str(row.get("reason_code", ""))
        if not reason_code.startswith("ac.movement."):
            continue
        rows.append(
            {
                "tick": int(row.get("tick", 0) or 0),
                "peer_id": str(row.get("peer_id", "")),
                "module_id": str(row.get("module_id", "")),
                "reason_code": reason_code,
                "fingerprint": str(row.get("deterministic_fingerprint", "")),
            }
        )
    return sorted(rows, key=lambda row: (int(row["tick"]), row["peer_id"], row["module_id"], row["reason_code"], row["fingerprint"]))


def _run_once(repo_root: str):
    from net.policies.policy_server_authoritative import (
        advance_authoritative_tick,
        build_client_intent_envelope,
        queue_intent_envelope,
    )
    from tools.xstack.testx.tests.net_anti_cheat_testlib import apply_anti_cheat_policy
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.embodiment.movement_ac",
        client_peer_id="peer.client.alpha",
    )
    runtime = clone_runtime(fixture)
    ok, err = apply_anti_cheat_policy(runtime, dict(fixture.get("payloads") or {}), "policy.ac.detect_only")
    if not ok:
        return {"result": "fail", "message": err}
    anti = dict(runtime.get("anti_cheat") or {})
    ext = dict(anti.get("extensions") or {})
    ext["movement_max_displacement_mm_per_tick"] = 100
    ext["movement_intents_per_tick_max"] = 8
    anti["extensions"] = ext
    runtime["anti_cheat"] = anti
    _seed_embodied_agent(runtime)

    clients = dict(runtime.get("clients") or {})
    client = dict(clients.get("peer.client.alpha") or {})
    authority_context = dict(client.get("authority_context") or {})
    entitlements = sorted(
        set(
            str(item).strip()
            for item in list(authority_context.get("entitlements") or []) + ["entitlement.agent.move"]
            if str(item).strip()
        )
    )
    authority_context["entitlements"] = entitlements
    client["authority_context"] = authority_context
    clients["peer.client.alpha"] = client
    runtime["clients"] = clients

    envelope_result = build_client_intent_envelope(
        runtime=runtime,
        peer_id="peer.client.alpha",
        intent_id="intent.agent.move.ac.001",
        process_id="process.agent_move",
        inputs={
            "agent_id": "agent.alpha",
            "controller_id": "controller.alpha",
            "owner_peer_id": "peer.client.alpha",
            "move_vector_local": {"x": 600, "y": 0, "z": 0},
            "speed_scalar": 1000,
            "tick_duration": 1,
        },
        submission_tick=1,
    )
    if str(envelope_result.get("result", "")) != "complete":
        return {"result": "fail", "message": "build_client_intent_envelope failed"}

    queued = queue_intent_envelope(
        repo_root=repo_root,
        runtime=runtime,
        envelope=dict(envelope_result.get("envelope") or {}),
    )
    if str(queued.get("result", "")) != "complete":
        return {"result": "fail", "message": "movement envelope queue failed: {}".format(str((queued.get("refusal") or {}).get("reason_code", "")))}

    stepped = advance_authoritative_tick(repo_root=repo_root, runtime=runtime)
    if str(stepped.get("result", "")) != "complete":
        return {"result": "fail", "message": "advance_authoritative_tick failed"}

    return {
        "result": "complete",
        "runtime": runtime,
        "tick": int(stepped.get("tick", 0) or 0),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once(repo_root=repo_root)
    second = _run_once(repo_root=repo_root)
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": str(first.get("message", "first run failed"))}
    if str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": str(second.get("message", "second run failed"))}

    first_events = _movement_events(dict(first.get("runtime") or {}))
    second_events = _movement_events(dict(second.get("runtime") or {}))
    if not first_events or not second_events:
        return {"status": "fail", "message": "expected deterministic movement anti-cheat events were not emitted"}
    if first_events != second_events:
        return {"status": "fail", "message": "movement anti-cheat event fingerprints diverged across replay"}
    return {"status": "pass", "message": "movement anti-cheat event determinism check passed"}
