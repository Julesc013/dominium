"""STRICT test: server-authoritative two-client tick stream is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.authoritative_two_clients_determinism"
TEST_TAGS = ["strict", "net", "session"]


def _anchors(runtime: dict):
    server = dict(runtime.get("server") or {})
    rows = list(server.get("hash_anchor_frames") or [])
    return [str((row or {}).get("composite_hash", "")) for row in rows]


def _client_hashes(runtime: dict):
    rows = dict(runtime.get("clients") or {})
    return dict(
        (peer_id, str((row or {}).get("last_perceived_hash", "")))
        for peer_id, row in sorted(rows.items(), key=lambda item: str(item[0]))
    )


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
        save_id="save.testx.net.authoritative.determinism",
        client_peer_id="peer.client.alpha",
    )

    def run_once(reverse_submit: bool):
        runtime = clone_runtime(fixture)
        baseline = prepare_server_authoritative_baseline(repo_root=repo_root, runtime=runtime)
        if str(baseline.get("result", "")) != "complete":
            return {}, "baseline_failed"
        snapshot_id = str((baseline.get("snapshot") or {}).get("snapshot_id", ""))
        joined = join_client_midstream(
            repo_root=repo_root,
            runtime=runtime,
            peer_id="peer.client.beta",
            authority_context=dict(fixture.get("authority_context") or {}),
            law_profile=dict(fixture.get("law_profile") or {}),
            lens_profile=dict(fixture.get("lens_profile") or {}),
            negotiated_policy_id=POLICY_ID_SERVER_AUTHORITATIVE,
            snapshot_id=snapshot_id,
        )
        if str(joined.get("result", "")) != "complete":
            return {}, "join_failed"

        env_a = build_client_intent_envelope(
            runtime=runtime,
            peer_id="peer.client.alpha",
            intent_id="intent.alpha.move.01",
            process_id="process.camera_move",
            inputs={"delta_local_mm": {"x": 7, "y": 0, "z": 0}, "dt_ticks": 1},
            submission_tick=1,
        )
        env_b = build_client_intent_envelope(
            runtime=runtime,
            peer_id="peer.client.beta",
            intent_id="intent.beta.move.01",
            process_id="process.camera_move",
            inputs={"delta_local_mm": {"x": 0, "y": 3, "z": 0}, "dt_ticks": 1},
            submission_tick=1,
        )
        if str(env_a.get("result", "")) != "complete" or str(env_b.get("result", "")) != "complete":
            return {}, "envelope_build_failed"

        envelopes = [dict(env_a.get("envelope") or {}), dict(env_b.get("envelope") or {})]
        if reverse_submit:
            envelopes = list(reversed(envelopes))
        simulated = run_authoritative_simulation(
            repo_root=repo_root,
            runtime=runtime,
            envelopes=envelopes,
            ticks=3,
        )
        if str(simulated.get("result", "")) != "complete":
            return {}, "simulation_failed"

        client_hashes = _client_hashes(runtime)
        return {
            "anchors": _anchors(runtime),
            "client_hashes": client_hashes,
            "final_hash": str(simulated.get("final_composite_hash", "")),
        }, ""

    first, first_err = run_once(reverse_submit=False)
    if first_err:
        return {"status": "fail", "message": "first deterministic run failed ({})".format(first_err)}
    second, second_err = run_once(reverse_submit=True)
    if second_err:
        return {"status": "fail", "message": "second deterministic run failed ({})".format(second_err)}

    if list(first.get("anchors") or []) != list(second.get("anchors") or []):
        return {"status": "fail", "message": "authoritative hash_anchor_frame sequence diverged across identical inputs"}
    if dict(first.get("client_hashes") or {}) != dict(second.get("client_hashes") or {}):
        return {"status": "fail", "message": "peer perceived hashes diverged across deterministic rerun"}

    peer_hashes = dict(first.get("client_hashes") or {})
    alpha_hash = str(peer_hashes.get("peer.client.alpha", ""))
    beta_hash = str(peer_hashes.get("peer.client.beta", ""))
    if not alpha_hash or not beta_hash:
        return {"status": "fail", "message": "client perceived hashes missing after authoritative simulation"}

    return {"status": "pass", "message": "server-authoritative two-client deterministic hashes are stable"}
