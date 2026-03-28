"""STRICT test: SRZ hybrid cross-shard spectator follow obeys policy allow/deny switch."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.view.cross_shard_follow_policy"
TEST_TAGS = ["strict", "net", "session", "srz", "view", "camera"]


def _envelope(lock_payload: dict, law_profile_id: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "envelope_id": "env.peer.client.follow.cross_shard.tick.1.seq.0001",
        "authority_summary": {
            "authority_origin": "client",
            "law_profile_id": str(law_profile_id),
        },
        "source_peer_id": "peer.client.hybrid.alpha",
        "source_shard_id": "shard.0",
        "target_shard_id": "auto",
        "submission_tick": 1,
        "deterministic_sequence_number": 1,
        "intent_id": "intent.view.cross_shard_follow.001",
        "payload_schema_id": "dominium.intent.process.v1",
        "payload": {
            "process_id": "process.camera_bind_target",
            "inputs": {
                "controller_id": "object.earth",
                "camera_id": "camera.main",
                "target_type": "agent",
                "target_id": "object.luna",
                "view_mode_id": "view.follow.spectator",
            },
        },
        "pack_lock_hash": str(lock_payload.get("pack_lock_hash", "")),
        "registry_hashes": dict(lock_payload.get("registries") or {}),
        "signature": "",
        "extensions": {},
    }


def _run_once(repo_root: str, allow_cross_shard_follow: bool):
    from net.policies.policy_srz_hybrid import run_hybrid_simulation
    from tools.xstack.testx.tests.net_hybrid_testlib import clone_runtime, prepare_hybrid_runtime_fixture

    fixture = prepare_hybrid_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.view.cross_shard_follow_policy",
        client_peer_id="peer.client.hybrid.alpha",
    )
    runtime = clone_runtime(fixture)

    clients = dict(runtime.get("clients") or {})
    client = dict(clients.get("peer.client.hybrid.alpha") or {})
    authority_context = dict(client.get("authority_context") or {})
    authority_context["entitlements"] = sorted(
        set(
            list(authority_context.get("entitlements") or [])
            + [
                "entitlement.control.camera",
                "entitlement.view.follow",
                "entitlement.view.spectator",
            ]
        )
    )
    client["authority_context"] = authority_context
    clients["peer.client.hybrid.alpha"] = client
    runtime["clients"] = clients

    control_policy = dict(runtime.get("control_policy") or {})
    control_policy["allow_cross_shard_follow"] = bool(allow_cross_shard_follow)
    allowed_modes = sorted(set(list(control_policy.get("allowed_view_modes") or []) + ["view.follow.spectator"]))
    control_policy["allowed_view_modes"] = allowed_modes
    runtime["control_policy"] = control_policy

    law_profile_id = str((fixture.get("law_profile") or {}).get("law_profile_id", ""))
    lock_payload = dict(fixture.get("lock_payload") or {})
    envelope = _envelope(lock_payload=lock_payload, law_profile_id=law_profile_id)
    ran = run_hybrid_simulation(repo_root=repo_root, runtime=runtime, envelopes=[envelope], ticks=1)
    return {"runtime": runtime, "result": ran}


def _has_cross_shard_refusal(runtime: dict) -> bool:
    server = dict(runtime.get("server") or {})
    rows = [dict(row) for row in list(server.get("refusals") or []) if isinstance(row, dict)]
    codes = sorted(set(str(row.get("reason_code", "")) for row in rows))
    return "refusal.view.cross_shard_follow_forbidden" in codes


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    denied = _run_once(repo_root=repo_root, allow_cross_shard_follow=False)
    denied_result = dict(denied.get("result") or {})
    if str(denied_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "denied cross-shard follow run failed unexpectedly"}
    if not _has_cross_shard_refusal(dict(denied.get("runtime") or {})):
        return {"status": "fail", "message": "cross-shard follow denial did not emit refusal.view.cross_shard_follow_forbidden"}

    allowed = _run_once(repo_root=repo_root, allow_cross_shard_follow=True)
    allowed_result = dict(allowed.get("result") or {})
    if str(allowed_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "allowed cross-shard follow run failed unexpectedly"}
    if _has_cross_shard_refusal(dict(allowed.get("runtime") or {})):
        return {"status": "fail", "message": "cross-shard follow should not refuse when allow_cross_shard_follow=true"}

    denied_hash = str(denied_result.get("final_composite_hash", ""))
    denied_again = _run_once(repo_root=repo_root, allow_cross_shard_follow=False)
    denied_again_hash = str((dict(denied_again.get("result") or {})).get("final_composite_hash", ""))
    if denied_hash != denied_again_hash:
        return {"status": "fail", "message": "cross-shard follow denial path must be deterministic across replay"}

    return {"status": "pass", "message": "cross-shard follow policy allow/deny checks passed"}
