"""STRICT test: invalid authoritative envelope is refused deterministically."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.authoritative_refuse_invalid_envelope"
TEST_TAGS = ["strict", "net", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from net.policies.policy_server_authoritative import (
        build_client_intent_envelope,
        prepare_server_authoritative_baseline,
        run_authoritative_simulation,
    )
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.authoritative.invalid_envelope",
        client_peer_id="peer.client.alpha",
    )
    runtime = clone_runtime(fixture)
    baseline = prepare_server_authoritative_baseline(repo_root=repo_root, runtime=runtime)
    if str(baseline.get("result", "")) != "complete":
        return {"status": "fail", "message": "baseline sync failed before invalid envelope test"}

    built = build_client_intent_envelope(
        runtime=runtime,
        peer_id="peer.client.alpha",
        intent_id="intent.alpha.invalid",
        process_id="process.camera_move",
        inputs={"delta_local_mm": {"x": 1, "y": 1, "z": 0}, "dt_ticks": 1},
        submission_tick=1,
    )
    if str(built.get("result", "")) != "complete":
        return {"status": "fail", "message": "failed to build base envelope for invalid-envelope test"}
    invalid_envelope = dict(built.get("envelope") or {})
    if "deterministic_sequence_number" in invalid_envelope:
        del invalid_envelope["deterministic_sequence_number"]

    simulated = run_authoritative_simulation(
        repo_root=repo_root,
        runtime=runtime,
        envelopes=[invalid_envelope],
        ticks=1,
    )
    if str(simulated.get("result", "")) != "refused":
        return {"status": "fail", "message": "invalid envelope should refuse prior to simulation commit"}
    refusal_payload = dict(simulated.get("refusal") or {})
    if str(refusal_payload.get("reason_code", "")) != "refusal.net.envelope_invalid":
        return {"status": "fail", "message": "unexpected refusal code for invalid envelope"}

    return {"status": "pass", "message": "invalid authoritative envelope refusal is deterministic"}
