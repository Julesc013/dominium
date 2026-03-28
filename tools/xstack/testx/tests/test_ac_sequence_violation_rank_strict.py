"""STRICT test: sequence violations under ranked strict policy are enforcement-blocking."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.ac_sequence_violation_rank_strict"
TEST_TAGS = ["strict", "net", "anti_cheat"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from net.anti_cheat import action_blocks_submission, check_sequence_integrity
    from tools.xstack.testx.tests.net_anti_cheat_testlib import apply_anti_cheat_policy
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.ac.rank_strict.sequence",
        client_peer_id="peer.client.alpha",
    )
    runtime = clone_runtime(fixture)
    ok, err = apply_anti_cheat_policy(runtime, dict(fixture.get("payloads") or {}), "policy.ac.rank_strict")
    if not ok:
        return {"status": "fail", "message": err}

    checked = check_sequence_integrity(
        repo_root=repo_root,
        runtime=runtime,
        tick=2,
        peer_id="peer.client.alpha",
        sequence=21,
        expected_sequence=1,
        default_action_token="refuse",
    )
    if str(checked.get("result", "")) != "violation":
        return {"status": "fail", "message": "sequence mismatch should produce a deterministic violation event"}
    action = str(checked.get("action", ""))
    if action != "refuse":
        return {"status": "fail", "message": "ranked strict sequence violation should map to refuse action"}
    if not action_blocks_submission(action):
        return {"status": "fail", "message": "ranked strict sequence violation action must block submission"}

    server = dict(runtime.get("server") or {})
    refusals = list(server.get("anti_cheat_refusal_injections") or [])
    if not refusals:
        return {"status": "fail", "message": "ranked strict sequence violation must record refusal injection evidence"}

    return {"status": "pass", "message": "ranked strict sequence violation deterministically refuses submissions"}

