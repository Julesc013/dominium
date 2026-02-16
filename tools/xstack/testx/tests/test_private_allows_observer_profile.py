"""STRICT test: private relaxed server profile accepts observer truth law profile requests."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.private_allows_observer_profile"
TEST_TAGS = ["strict", "net", "security", "diegetic"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.net_handshake import run_loopback_handshake
    from tools.xstack.testx.tests.net_testlib import prepare_handshake_fixture

    fixture = prepare_handshake_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.private_allows_observer_profile",
        requested_replication_policy_id="policy.net.server_authoritative",
        anti_cheat_policy_id="policy.ac.private_relaxed",
        server_profile_id="server.profile.private_relaxed",
        server_policy_id="server.policy.private.default",
        securex_policy_id="securex.policy.private_relaxed",
        desired_law_profile_id="law.observer.truth",
    )
    result = run_loopback_handshake(
        repo_root=repo_root,
        session_spec=dict(fixture["session_spec"]),
        lock_payload=dict(fixture["lock_payload"]),
        replication_registry=dict(fixture["replication_registry"]),
        anti_cheat_registry=dict(fixture["anti_cheat_registry"]),
        server_policy_registry=dict(fixture["server_policy_registry"]),
        securex_policy_registry=dict(fixture["securex_policy_registry"]),
        server_profile_registry=dict(fixture["server_profile_registry"]),
        authority_context=dict(fixture["authority_context"]),
    )
    if str(result.get("result", "")) != "complete":
        refusal_code = str((dict(result.get("refusal") or {}).get("reason_code", "")))
        return {
            "status": "fail",
            "message": "private relaxed server should accept observer truth profile (got refusal '{}')".format(refusal_code or "<none>"),
        }
    negotiated = str(result.get("server_law_profile_id", ""))
    if negotiated != "law.observer.truth":
        return {"status": "fail", "message": "private relaxed handshake negotiated unexpected law profile '{}'".format(negotiated)}
    return {"status": "pass", "message": "private relaxed server accepts observer truth profile deterministically"}
