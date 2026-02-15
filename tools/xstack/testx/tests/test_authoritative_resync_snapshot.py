"""STRICT test: server-authoritative resync restores deterministic perceived cache."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.authoritative_resync_snapshot"
TEST_TAGS = ["strict", "net", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.net.policies.policy_server_authoritative import (
        build_client_intent_envelope,
        prepare_server_authoritative_baseline,
        request_resync_snapshot,
        run_authoritative_simulation,
    )
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.authoritative.resync",
        client_peer_id="peer.client.alpha",
    )
    runtime = clone_runtime(fixture)
    baseline = prepare_server_authoritative_baseline(repo_root=repo_root, runtime=runtime)
    if str(baseline.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline sync failed before resync test"}

    envelope = build_client_intent_envelope(
        runtime=runtime,
        peer_id="peer.client.alpha",
        intent_id="intent.alpha.move.resync",
        process_id="process.camera_move",
        inputs={"delta_local_mm": {"x": -3, "y": 1, "z": 0}, "dt_ticks": 1},
        submission_tick=1,
    )
    if str(envelope.get("result", "")) != "complete":
        return {"status": "fail", "message": "unable to build authoritative envelope for resync test"}

    stepped = run_authoritative_simulation(
        repo_root=repo_root,
        runtime=runtime,
        envelopes=[dict(envelope.get("envelope") or {})],
        ticks=2,
    )
    if str(stepped.get("result", "")) != "complete":
        return {"status": "fail", "message": "authoritative simulation failed prior to resync request"}

    clients = dict(runtime.get("clients") or {})
    alpha = dict(clients.get("peer.client.alpha") or {})
    if not alpha:
        return {"status": "fail", "message": "alpha peer missing before resync perturbation"}
    alpha["last_perceived_model"] = {"corrupt": True}
    alpha["last_perceived_hash"] = "0" * 64
    clients["peer.client.alpha"] = alpha
    runtime["clients"] = clients

    snapshots = list((runtime.get("server") or {}).get("snapshots") or [])
    if not snapshots:
        return {"status": "fail", "message": "no snapshots available for authoritative resync"}
    latest_snapshot_id = str(sorted((dict(row) for row in snapshots if isinstance(row, dict)), key=lambda row: str(row.get("snapshot_id", "")))[-1].get("snapshot_id", ""))

    resynced = request_resync_snapshot(
        repo_root=repo_root,
        runtime=runtime,
        peer_id="peer.client.alpha",
        snapshot_id=latest_snapshot_id,
    )
    if str(resynced.get("result", "")) != "complete":
        reason = str(((resynced.get("refusal") or {}).get("reason_code", "")) if isinstance(resynced, dict) else "")
        return {"status": "fail", "message": "authoritative resync refused ({})".format(reason)}

    alpha_after = dict((runtime.get("clients") or {}).get("peer.client.alpha") or {})
    if str(alpha_after.get("last_perceived_hash", "")) != str(resynced.get("perceived_hash", "")):
        return {"status": "fail", "message": "resync perceived hash mismatch between runtime and response"}
    if int(alpha_after.get("resync_count", 0) or 0) < 1:
        return {"status": "fail", "message": "resync_count did not increment"}

    return {"status": "pass", "message": "authoritative snapshot resync restored deterministic client state"}
