"""STRICT test: adversarial client behavior escalates deterministically under rank-strict anti-cheat policy."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.ac_adversarial_rank_strict"
TEST_TAGS = ["strict", "net", "anti_cheat", "multiplayer", "security"]


def _run_cases(repo_root: str, runtime: dict):
    from src.net.anti_cheat import (
        check_authority_integrity,
        check_input_integrity,
        check_replay_protection,
        check_sequence_integrity,
        check_state_integrity,
    )

    out = []
    out.append(
        check_sequence_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=1,
            peer_id="peer.client.alpha",
            sequence=1,
            expected_sequence=2,
            default_action_token="refuse",
        )
    )
    out.append(
        check_replay_protection(
            repo_root=repo_root,
            runtime=runtime,
            tick=1,
            peer_id="peer.client.alpha",
            envelope_id="env.replay.002",
            seen_envelope_ids=["env.replay.002"],
            default_action_token="refuse",
        )
    )
    out.append(
        check_authority_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=2,
            peer_id="peer.client.alpha",
            allowed=False,
            reason_code="refusal.net.authority_violation",
            evidence=["entitlement escalation attempt"],
            default_action_token="refuse",
        )
    )
    out.append(
        check_authority_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=2,
            peer_id="peer.client.alpha",
            allowed=False,
            reason_code="refusal.net.shard_target_invalid",
            evidence=["shard target spoof attempt"],
            default_action_token="refuse",
        )
    )
    out.append(
        check_input_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=3,
            peer_id="peer.client.alpha",
            valid=False,
            reason_code="refusal.net.envelope_invalid",
            evidence=["invalid schema payload"],
            default_action_token="refuse",
        )
    )
    out.append(
        check_input_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=3,
            peer_id="peer.client.alpha",
            valid=False,
            reason_code="refusal.net.sequence_violation",
            evidence=["intent spam burst exceeded deterministic tick budget"],
            default_action_token="throttle",
        )
    )
    out.append(
        check_state_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=4,
            peer_id="peer.client.alpha",
            expected_hash="a" * 64,
            actual_hash="b" * 64,
            reason_code="refusal.net.resync_required",
            default_action_token="audit",
        )
    )
    out.append(
        check_state_integrity(
            repo_root=repo_root,
            runtime=runtime,
            tick=5,
            peer_id="peer.client.alpha",
            expected_hash="a" * 64,
            actual_hash="c" * 64,
            reason_code="refusal.net.resync_required",
            default_action_token="audit",
        )
    )
    return out


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.net_anti_cheat_testlib import apply_anti_cheat_policy
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.ac.adversarial.rank_strict",
        client_peer_id="peer.client.alpha",
    )
    runtime = clone_runtime(fixture)
    ok, err = apply_anti_cheat_policy(runtime, dict(fixture.get("payloads") or {}), "policy.ac.rank_strict")
    if not ok:
        return {"status": "fail", "message": err}

    results = _run_cases(repo_root=repo_root, runtime=runtime)
    actions = [str((row or {}).get("action", "")) for row in results]
    if not any(token in ("refuse", "terminate", "require_attestation") for token in actions):
        return {"status": "fail", "message": "rank-strict adversarial suite failed to escalate enforcement actions"}

    server = dict(runtime.get("server") or {})
    events = list(server.get("anti_cheat_events") or [])
    refusals = list(server.get("anti_cheat_refusal_injections") or [])
    terminated = set(str(item).strip() for item in (server.get("terminated_peers") or []) if str(item).strip())
    if len(events) < 8:
        return {"status": "fail", "message": "expected deterministic anti-cheat events for rank-strict adversarial suite"}
    if not refusals:
        return {"status": "fail", "message": "rank-strict adversarial suite must emit refusal injections"}
    if "peer.client.alpha" not in terminated:
        return {"status": "fail", "message": "rank-strict adversarial suite should terminate peer after repeated severe violations"}

    return {"status": "pass", "message": "adversarial rank-strict anti-cheat suite escalates deterministically"}

