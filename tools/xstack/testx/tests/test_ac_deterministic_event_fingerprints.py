"""STRICT test: anti-cheat event/action fingerprints are deterministic across identical runs."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.ac_deterministic_event_fingerprints"
TEST_TAGS = ["strict", "net", "anti_cheat"]


def _fingerprints_from_runtime(runtime: dict):
    server = dict(runtime.get("server") or {})
    events = sorted(
        (dict(row) for row in (server.get("anti_cheat_events") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("event_id", "")),
    )
    actions = sorted(
        (dict(row) for row in (server.get("anti_cheat_enforcement_actions") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("action_id", "")),
    )
    event_fps = [str(row.get("deterministic_fingerprint", "")) for row in events]
    action_fps = [str(row.get("deterministic_fingerprint", "")) for row in actions]
    return event_fps, action_fps


def _run_sequence(repo_root: str, runtime: dict):
    from src.net.anti_cheat import check_authority_integrity, check_replay_protection, check_sequence_integrity, check_state_integrity

    check_sequence_integrity(
        repo_root=repo_root,
        runtime=runtime,
        tick=7,
        peer_id="peer.client.alpha",
        sequence=99,
        expected_sequence=1,
        default_action_token="refuse",
    )
    check_replay_protection(
        repo_root=repo_root,
        runtime=runtime,
        tick=8,
        peer_id="peer.client.alpha",
        envelope_id="env.same",
        seen_envelope_ids=["env.same"],
        default_action_token="refuse",
    )
    check_authority_integrity(
        repo_root=repo_root,
        runtime=runtime,
        tick=9,
        peer_id="peer.client.alpha",
        allowed=False,
        reason_code="refusal.net.authority_violation",
        evidence=["forbidden process for authority_context"],
        default_action_token="refuse",
    )
    check_state_integrity(
        repo_root=repo_root,
        runtime=runtime,
        tick=10,
        peer_id="peer.client.alpha",
        expected_hash="d" * 64,
        actual_hash="e" * 64,
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.net_anti_cheat_testlib import apply_anti_cheat_policy
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.ac.fingerprints",
        client_peer_id="peer.client.alpha",
    )

    runtime_a = clone_runtime(fixture)
    ok, err = apply_anti_cheat_policy(runtime_a, dict(fixture.get("payloads") or {}), "policy.ac.rank_strict")
    if not ok:
        return {"status": "fail", "message": err}
    _run_sequence(repo_root, runtime_a)
    event_a, action_a = _fingerprints_from_runtime(runtime_a)

    runtime_b = clone_runtime(fixture)
    ok, err = apply_anti_cheat_policy(runtime_b, dict(fixture.get("payloads") or {}), "policy.ac.rank_strict")
    if not ok:
        return {"status": "fail", "message": err}
    _run_sequence(repo_root, runtime_b)
    event_b, action_b = _fingerprints_from_runtime(runtime_b)

    if event_a != event_b:
        return {"status": "fail", "message": "anti-cheat event fingerprints differ across identical deterministic inputs"}
    if action_a != action_b:
        return {"status": "fail", "message": "anti-cheat action fingerprints differ across identical deterministic inputs"}

    return {"status": "pass", "message": "anti-cheat event/action fingerprints are deterministic"}

