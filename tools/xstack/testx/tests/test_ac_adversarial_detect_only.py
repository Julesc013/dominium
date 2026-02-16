"""STRICT test: adversarial client behavior emits deterministic anti-cheat events in detect-only mode."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.ac_adversarial_detect_only"
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
            envelope_id="env.replay.001",
            seen_envelope_ids=["env.replay.001"],
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
    return out


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.net_anti_cheat_testlib import apply_anti_cheat_policy
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.ac.adversarial.detect_only",
        client_peer_id="peer.client.alpha",
    )
    runtime = clone_runtime(fixture)
    ok, err = apply_anti_cheat_policy(runtime, dict(fixture.get("payloads") or {}), "policy.ac.detect_only")
    if not ok:
        return {"status": "fail", "message": err}

    results = _run_cases(repo_root=repo_root, runtime=runtime)
    actions = [str((row or {}).get("action", "")) for row in results]
    if any(action != "audit" for action in actions):
        return {"status": "fail", "message": "detect-only adversarial suite produced non-audit action"}

    server = dict(runtime.get("server") or {})
    events = list(server.get("anti_cheat_events") or [])
    refusals = list(server.get("anti_cheat_refusal_injections") or [])
    if len(events) < 7:
        return {"status": "fail", "message": "expected deterministic anti-cheat events for all adversarial cases"}
    if refusals:
        return {"status": "fail", "message": "detect-only policy must not inject refusal rows for adversarial suite"}

    fingerprints = [str((row or {}).get("deterministic_fingerprint", "")) for row in events]
    if any(not token for token in fingerprints):
        return {"status": "fail", "message": "adversarial detect-only suite emitted event without deterministic fingerprint"}

    return {"status": "pass", "message": "adversarial detect-only anti-cheat suite is deterministic and non-invasive"}

