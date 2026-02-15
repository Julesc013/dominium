"""STRICT test: SRZ hybrid two-shard coordinator matches single-shard equivalent for same intent stream."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.net.srz_hybrid.two_shard_equivalence"
TEST_TAGS = ["strict", "net", "session", "srz"]


def _envelopes(lock_payload: dict, law_profile_id: str) -> list:
    registry_hashes = dict(lock_payload.get("registries") or {})
    pack_lock_hash = str(lock_payload.get("pack_lock_hash", ""))
    base = {
        "schema_version": "1.0.0",
        "authority_summary": {
            "authority_origin": "client",
            "law_profile_id": str(law_profile_id),
        },
        "source_peer_id": "peer.client.hybrid.alpha",
        "source_shard_id": "shard.0",
        "target_shard_id": "auto",
        "submission_tick": 1,
        "payload_schema_id": "dominium.intent.process.v1",
        "pack_lock_hash": pack_lock_hash,
        "registry_hashes": registry_hashes,
        "signature": "",
        "extensions": {},
    }
    first = dict(base)
    first.update(
        {
            "envelope_id": "env.peer.client.hybrid.alpha.tick.1.seq.0001",
            "deterministic_sequence_number": 1,
            "intent_id": "intent.001",
            "payload": {
                "process_id": "process.camera_teleport",
                "inputs": {"target_object_id": "object.earth"},
            },
        }
    )
    second = dict(base)
    second.update(
        {
            "envelope_id": "env.peer.client.hybrid.alpha.tick.1.seq.0002",
            "deterministic_sequence_number": 2,
            "intent_id": "intent.002",
            "payload": {
                "process_id": "process.time_pause",
                "inputs": {},
            },
        }
    )
    return [first, second]


def _single_shard_server_policy(payload: dict) -> dict:
    out = copy.deepcopy(dict(payload or {}))
    rows = out.get("policies")
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("policy_id", "")).strip() != "server.policy.private.default":
            continue
        extensions = dict(row.get("extensions") or {})
        extensions["default_shard_map_id"] = "shard_map.default.single_shard"
        row["extensions"] = extensions
    out["policies"] = rows
    return out


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.net.policies.policy_srz_hybrid import initialize_hybrid_runtime, run_hybrid_simulation
    from tools.xstack.testx.tests.net_hybrid_testlib import clone_runtime, prepare_hybrid_runtime_fixture

    fixture = prepare_hybrid_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.srz_hybrid.two_shard_equivalence",
        client_peer_id="peer.client.hybrid.alpha",
    )
    two_shard_runtime = clone_runtime(fixture)
    lock_payload = dict(fixture.get("lock_payload") or {})
    envelopes = _envelopes(lock_payload=lock_payload, law_profile_id=str((fixture.get("law_profile") or {}).get("law_profile_id", "")))

    two_result = run_hybrid_simulation(
        repo_root=repo_root,
        runtime=two_shard_runtime,
        envelopes=envelopes,
        ticks=2,
    )
    if str(two_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "two-shard hybrid run refused unexpectedly"}

    payloads = dict(fixture.get("payloads") or {})
    single_init = initialize_hybrid_runtime(
        repo_root=repo_root,
        save_id="save.testx.net.srz_hybrid.two_shard_equivalence.single",
        session_spec=dict(fixture.get("session_spec") or {}),
        lock_payload=lock_payload,
        universe_identity=dict((fixture.get("runtime") or {}).get("universe_identity") or {}),
        universe_state=dict((fixture.get("runtime") or {}).get("global_state") or {}),
        law_profile=dict(fixture.get("law_profile") or {}),
        lens_profile=dict(fixture.get("lens_profile") or {}),
        authority_context=dict(fixture.get("authority_context") or {}),
        anti_cheat_policy_registry=dict(payloads.get("anti_cheat_policy_registry_hash") or {}),
        anti_cheat_module_registry=dict(payloads.get("anti_cheat_module_registry_hash") or {}),
        replication_policy_registry=dict(payloads.get("net_replication_policy_registry_hash") or {}),
        server_policy_registry=_single_shard_server_policy(dict(payloads.get("net_server_policy_registry_hash") or {})),
        shard_map_registry=dict(payloads.get("shard_map_registry_hash") or {}),
        perception_interest_policy_registry=dict(payloads.get("perception_interest_policy_registry_hash") or {}),
        registry_payloads={
            "astronomy_catalog_index": dict(payloads.get("astronomy_catalog_index_hash") or {}),
            "site_registry_index": dict(payloads.get("site_registry_index_hash") or {}),
            "ephemeris_registry": dict(payloads.get("ephemeris_registry_hash") or {}),
            "terrain_tile_registry": dict(payloads.get("terrain_tile_registry_hash") or {}),
            "activation_policy_registry": dict(payloads.get("activation_policy_registry_hash") or {}),
            "budget_policy_registry": dict(payloads.get("budget_policy_registry_hash") or {}),
            "fidelity_policy_registry": dict(payloads.get("fidelity_policy_registry_hash") or {}),
        },
    )
    if str(single_init.get("result", "")) != "complete":
        return {"status": "fail", "message": "single-shard hybrid runtime initialization refused unexpectedly"}
    single_runtime = dict(single_init.get("runtime") or {})
    single_result = run_hybrid_simulation(
        repo_root=repo_root,
        runtime=single_runtime,
        envelopes=envelopes,
        ticks=2,
    )
    if str(single_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "single-shard hybrid run refused unexpectedly"}

    two_steps = [str((row or {}).get("composite_hash", "")) for row in (two_result.get("steps") or [])]
    single_steps = [str((row or {}).get("composite_hash", "")) for row in (single_result.get("steps") or [])]
    if two_steps != single_steps:
        return {"status": "fail", "message": "per-tick composite hashes diverged between two-shard and single-shard hybrid runs"}
    if str(two_result.get("final_composite_hash", "")) != str(single_result.get("final_composite_hash", "")):
        return {"status": "fail", "message": "final composite hash diverged between two-shard and single-shard hybrid runs"}
    return {"status": "pass", "message": "srz hybrid two-shard equivalence check passed"}

