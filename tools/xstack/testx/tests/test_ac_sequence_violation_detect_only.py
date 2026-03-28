"""STRICT test: sequence violations in detect-only policy emit events without refusal."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.ac_sequence_violation_detect_only"
TEST_TAGS = ["strict", "net", "anti_cheat"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from net.anti_cheat import check_sequence_integrity
    from tools.xstack.testx.tests.net_anti_cheat_testlib import apply_anti_cheat_policy
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.ac.detect_only.sequence",
        client_peer_id="peer.client.alpha",
    )
    runtime = clone_runtime(fixture)
    ok, err = apply_anti_cheat_policy(runtime, dict(fixture.get("payloads") or {}), "policy.ac.detect_only")
    if not ok:
        return {"status": "fail", "message": err}

    checked = check_sequence_integrity(
        repo_root=repo_root,
        runtime=runtime,
        tick=1,
        peer_id="peer.client.alpha",
        sequence=8,
        expected_sequence=1,
        default_action_token="refuse",
    )
    if str(checked.get("result", "")) != "violation":
        return {"status": "fail", "message": "sequence mismatch should produce a deterministic violation event"}
    if str(checked.get("action", "")) != "audit":
        return {"status": "fail", "message": "detect-only policy must keep sequence violations in audit-only action mode"}

    server = dict(runtime.get("server") or {})
    events = list(server.get("anti_cheat_events") or [])
    actions = list(server.get("anti_cheat_enforcement_actions") or [])
    refusals = list(server.get("anti_cheat_refusal_injections") or [])
    if len(events) != 1 or len(actions) != 1:
        return {"status": "fail", "message": "detect-only sequence violation should emit exactly one event and one action record"}
    if refusals:
        return {"status": "fail", "message": "detect-only policy must not inject refusal records for sequence violations"}

    return {"status": "pass", "message": "detect-only sequence violations remain non-invasive and deterministic"}

