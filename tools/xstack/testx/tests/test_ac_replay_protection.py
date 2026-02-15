"""STRICT test: replayed envelopes are refused deterministically by anti-cheat replay module."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.ac_replay_protection"
TEST_TAGS = ["strict", "net", "anti_cheat"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.net.anti_cheat import check_replay_protection
    from tools.xstack.testx.tests.net_anti_cheat_testlib import apply_anti_cheat_policy
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.ac.replay",
        client_peer_id="peer.client.alpha",
    )
    runtime = clone_runtime(fixture)
    ok, err = apply_anti_cheat_policy(runtime, dict(fixture.get("payloads") or {}), "policy.ac.casual_default")
    if not ok:
        return {"status": "fail", "message": err}

    replay_id = "env.replay.same"
    checked = check_replay_protection(
        repo_root=repo_root,
        runtime=runtime,
        tick=3,
        peer_id="peer.client.alpha",
        envelope_id=replay_id,
        seen_envelope_ids=[replay_id],
        default_action_token="refuse",
    )
    if str(checked.get("result", "")) != "violation":
        return {"status": "fail", "message": "replayed envelope must produce deterministic violation"}
    if str(checked.get("reason_code", "")) != "refusal.net.replay_detected":
        return {"status": "fail", "message": "unexpected replay protection reason code"}
    if str(checked.get("action", "")) != "refuse":
        return {"status": "fail", "message": "casual replay protection should map to refuse action"}

    server = dict(runtime.get("server") or {})
    events = list(server.get("anti_cheat_events") or [])
    if not events:
        return {"status": "fail", "message": "replay protection violation should emit anti-cheat event"}
    return {"status": "pass", "message": "replay protection refusal is deterministic"}

