"""STRICT test: authority escalation attempts are rejected and logged deterministically."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.ac_authority_escalation"
TEST_TAGS = ["strict", "net", "anti_cheat"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.net.anti_cheat import check_authority_integrity
    from tools.xstack.testx.tests.net_anti_cheat_testlib import apply_anti_cheat_policy
    from tools.xstack.testx.tests.net_authoritative_testlib import clone_runtime, prepare_authoritative_runtime_fixture

    fixture = prepare_authoritative_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.ac.authority",
        client_peer_id="peer.client.alpha",
    )
    runtime = clone_runtime(fixture)
    ok, err = apply_anti_cheat_policy(runtime, dict(fixture.get("payloads") or {}), "policy.ac.casual_default")
    if not ok:
        return {"status": "fail", "message": err}

    checked = check_authority_integrity(
        repo_root=repo_root,
        runtime=runtime,
        tick=4,
        peer_id="peer.client.alpha",
        allowed=False,
        reason_code="refusal.net.authority_violation",
        evidence=["intent requested entitlement not granted by authority_context"],
        default_action_token="refuse",
    )
    if str(checked.get("result", "")) != "violation":
        return {"status": "fail", "message": "authority escalation should produce deterministic violation"}
    if str(checked.get("reason_code", "")) != "refusal.net.authority_violation":
        return {"status": "fail", "message": "unexpected authority violation reason code"}
    if str(checked.get("action", "")) != "refuse":
        return {"status": "fail", "message": "casual authority escalation should be refused"}

    server = dict(runtime.get("server") or {})
    events = list(server.get("anti_cheat_events") or [])
    if not events:
        return {"status": "fail", "message": "authority escalation should emit anti-cheat event evidence"}
    return {"status": "pass", "message": "authority escalation refusal and evidence are deterministic"}

