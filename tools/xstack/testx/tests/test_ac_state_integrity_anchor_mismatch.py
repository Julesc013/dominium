"""STRICT test: state-integrity mismatch escalates deterministically under rank-strict policy."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.ac_state_integrity_anchor_mismatch"
TEST_TAGS = ["strict", "net", "anti_cheat"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from net.anti_cheat import check_state_integrity
    from tools.xstack.testx.tests.net_anti_cheat_testlib import apply_anti_cheat_policy
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.ac.state_mismatch",
        client_peer_id="peer.client.alpha",
    )
    runtime = clone_runtime(fixture)
    ok, err = apply_anti_cheat_policy(runtime, dict(fixture.get("payloads") or {}), "policy.ac.rank_strict")
    if not ok:
        return {"status": "fail", "message": err}

    first = check_state_integrity(
        repo_root=repo_root,
        runtime=runtime,
        tick=5,
        peer_id="peer.client.alpha",
        expected_hash="a" * 64,
        actual_hash="b" * 64,
    )
    if str(first.get("result", "")) != "violation":
        return {"status": "fail", "message": "first anchor mismatch should produce deterministic violation"}
    if str(first.get("action", "")) != "refuse":
        return {"status": "fail", "message": "first rank-strict state mismatch should map to refuse"}

    second = check_state_integrity(
        repo_root=repo_root,
        runtime=runtime,
        tick=6,
        peer_id="peer.client.alpha",
        expected_hash="a" * 64,
        actual_hash="c" * 64,
    )
    if str(second.get("result", "")) != "violation":
        return {"status": "fail", "message": "second anchor mismatch should produce deterministic violation"}
    if str(second.get("action", "")) != "terminate":
        return {"status": "fail", "message": "second rank-strict mismatch should escalate to terminate per policy table"}

    server = dict(runtime.get("server") or {})
    terminated = set(str(item).strip() for item in (server.get("terminated_peers") or []) if str(item).strip())
    if "peer.client.alpha" not in terminated:
        return {"status": "fail", "message": "escalated terminate action must record peer in terminated_peers"}

    return {"status": "pass", "message": "rank-strict state-integrity escalation is deterministic"}

