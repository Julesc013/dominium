"""STRICT test: server-authoritative midstream join uses snapshot baseline deterministically."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.authoritative_snapshot_join_midstream"
TEST_TAGS = ["strict", "net", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.net.policies.policy_server_authoritative import (
        POLICY_ID_SERVER_AUTHORITATIVE,
        build_client_intent_envelope,
        join_client_midstream,
        prepare_server_authoritative_baseline,
        run_authoritative_simulation,
    )
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.authoritative.midstream_join",
        client_peer_id="peer.client.alpha",
    )
    runtime = clone_runtime(fixture)
    baseline = prepare_server_authoritative_baseline(repo_root=repo_root, runtime=runtime)
    if str(baseline.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline sync failed before midstream join"}

    env = build_client_intent_envelope(
        runtime=runtime,
        peer_id="peer.client.alpha",
        intent_id="intent.alpha.move.midstream",
        process_id="process.camera_move",
        inputs={"delta_local_mm": {"x": 2, "y": 4, "z": 0}, "dt_ticks": 1},
        submission_tick=1,
    )
    if str(env.get("result", "")) != "complete":
        return {"status": "fail", "message": "failed to build deterministic intent envelope for alpha"}

    advanced = run_authoritative_simulation(
        repo_root=repo_root,
        runtime=runtime,
        envelopes=[dict(env.get("envelope") or {})],
        ticks=2,
    )
    if str(advanced.get("result", "")) != "complete":
        return {"status": "fail", "message": "failed to advance authoritative tick stream before join"}

    latest_snapshot_id = str((baseline.get("snapshot") or {}).get("snapshot_id", "")).strip()
    joined = join_client_midstream(
        repo_root=repo_root,
        runtime=runtime,
        peer_id="peer.client.gamma",
        authority_context=dict(fixture.get("authority_context") or {}),
        law_profile=dict(fixture.get("law_profile") or {}),
        lens_profile=dict(fixture.get("lens_profile") or {}),
        negotiated_policy_id=POLICY_ID_SERVER_AUTHORITATIVE,
        snapshot_id=latest_snapshot_id,
    )
    if str(joined.get("result", "")) != "complete":
        reason = str(((joined.get("refusal") or {}).get("reason_code", "")) if isinstance(joined, dict) else "")
        return {"status": "fail", "message": "midstream join refused ({})".format(reason)}

    clients = dict(runtime.get("clients") or {})
    gamma = dict(clients.get("peer.client.gamma") or {})
    if not gamma:
        return {"status": "fail", "message": "joined peer missing from runtime client map"}
    if int(gamma.get("last_applied_tick", -1)) < 0:
        return {"status": "fail", "message": "joined peer missing applied snapshot tick"}
    if str(gamma.get("last_perceived_hash", "")) != str(joined.get("perceived_hash", "")):
        return {"status": "fail", "message": "join result perceived hash does not match runtime peer cache"}

    return {"status": "pass", "message": "server-authoritative midstream join snapshot flow is deterministic"}
