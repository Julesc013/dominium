"""STRICT test: SRZ hybrid routing/output are deterministic under differing envelope arrival order."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.srz_hybrid.cross_shard_routing_determinism"
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
                "process_id": "process.camera_move",
                "inputs": {"delta_local": [0.0, 0.0, 1.0]},
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
                "process_id": "process.time_resume",
                "inputs": {},
            },
        }
    )
    return [first, second]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from net.policies.policy_srz_hybrid import run_hybrid_simulation
    from tools.xstack.testx.tests.net_hybrid_testlib import clone_runtime, prepare_hybrid_runtime_fixture

    fixture = prepare_hybrid_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.srz_hybrid.routing",
        client_peer_id="peer.client.hybrid.alpha",
    )
    lock_payload = dict(fixture.get("lock_payload") or {})
    law_profile_id = str((fixture.get("law_profile") or {}).get("law_profile_id", ""))
    envelopes = _envelopes(lock_payload=lock_payload, law_profile_id=law_profile_id)

    runtime_a = clone_runtime(fixture)
    result_a = run_hybrid_simulation(
        repo_root=repo_root,
        runtime=runtime_a,
        envelopes=list(envelopes),
        ticks=2,
    )
    runtime_b = clone_runtime(fixture)
    result_b = run_hybrid_simulation(
        repo_root=repo_root,
        runtime=runtime_b,
        envelopes=list(reversed(envelopes)),
        ticks=2,
    )
    if str(result_a.get("result", "")) != "complete" or str(result_b.get("result", "")) != "complete":
        return {"status": "fail", "message": "hybrid routing determinism run refused unexpectedly"}

    steps_a = [str((row or {}).get("composite_hash", "")) for row in (result_a.get("steps") or [])]
    steps_b = [str((row or {}).get("composite_hash", "")) for row in (result_b.get("steps") or [])]
    if steps_a != steps_b:
        return {"status": "fail", "message": "composite hash sequence changed across envelope arrival order variation"}
    if str(result_a.get("final_composite_hash", "")) != str(result_b.get("final_composite_hash", "")):
        return {"status": "fail", "message": "final composite hash changed across envelope arrival order variation"}
    return {"status": "pass", "message": "srz hybrid routing determinism check passed"}

