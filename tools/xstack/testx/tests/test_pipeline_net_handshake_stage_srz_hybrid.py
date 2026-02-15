"""STRICT test: multiplayer pipeline executes net baseline/join stages for SRZ hybrid policy."""

from __future__ import annotations

import os
import sys


TEST_ID = "testx.net.pipeline_net_handshake_stage_srz_hybrid"
TEST_TAGS = ["strict", "session", "net", "srz"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.runner import boot_session_spec

    created = create_session_spec(
        repo_root=repo_root,
        save_id="save.testx.net.pipeline.srz_hybrid",
        bundle_id="bundle.base.lab",
        scenario_id="scenario.lab.galaxy_nav",
        mission_id="",
        experience_id="profile.lab.developer",
        law_profile_id="law.lab.unrestricted",
        parameter_bundle_id="params.lab.placeholder",
        budget_policy_id="policy.budget.default_lab",
        fidelity_policy_id="policy.fidelity.default_lab",
        rng_seed_string="seed.mp5.pipeline.srz_hybrid",
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string="seed.mp5.pipeline.srz_hybrid.universe",
        universe_id="",
        entitlements=[
            "session.boot",
            "entitlement.inspect",
            "entitlement.teleport",
            "entitlement.camera_control",
            "entitlement.time_control",
            "ui.window.lab.nav",
            "lens.nondiegetic.access",
        ],
        epistemic_scope_id="epistemic.lab.placeholder",
        visibility_level="placeholder",
        privilege_level="operator",
        net_endpoint="loopback://mp5.pipeline.srz_hybrid",
        net_transport_id="transport.loopback",
        net_client_peer_id="peer.client.pipeline.srz",
        net_server_peer_id="peer.server.pipeline.srz",
        net_replication_policy_id="policy.net.srz_hybrid",
        net_anti_cheat_policy_id="policy.ac.casual_default",
        net_server_policy_id="server.policy.private.default",
        net_securex_policy_id="",
        net_desired_law_profile_id="law.lab.unrestricted",
        net_schema_versions=[],
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "create_session_spec failed for SRZ hybrid pipeline stage test"}

    session_spec_rel = str(created.get("session_spec_path", "")).strip()
    session_spec_abs = os.path.join(repo_root, session_spec_rel.replace("/", os.sep))
    booted = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=session_spec_abs,
        bundle_id="bundle.base.lab",
        compile_if_missing=True,
    )
    if str(booted.get("result", "")) != "complete":
        reason = str(((booted.get("refusal") or {}).get("reason_code", "")) if isinstance(booted, dict) else "")
        return {"status": "fail", "message": "boot_session_spec refused ({})".format(reason)}

    stage_rows = list(booted.get("stage_log") or [])
    observed_stages = [str((row or {}).get("to_stage_id", "")) for row in stage_rows]
    required = ("stage.net_handshake", "stage.net_sync_baseline", "stage.net_join_world")
    for stage_id in required:
        if stage_id not in observed_stages:
            return {"status": "fail", "message": "stage log missing '{}'".format(stage_id)}

    sync = dict(booted.get("network_sync_baseline") or {})
    join = dict(booted.get("network_join_world") or {})
    if not bool(sync.get("executed", False)):
        return {"status": "fail", "message": "network_sync_baseline summary did not execute"}
    if not bool(join.get("executed", False)):
        return {"status": "fail", "message": "network_join_world summary did not execute"}
    if str(sync.get("policy_id", "")) != "policy.net.srz_hybrid":
        return {"status": "fail", "message": "unexpected baseline policy id in SRZ hybrid run summary"}
    if not str(sync.get("snapshot_id", "")).strip():
        return {"status": "fail", "message": "SRZ hybrid baseline summary missing snapshot_id"}
    if not str(join.get("snapshot_id", "")).strip():
        return {"status": "fail", "message": "SRZ hybrid join summary missing snapshot_id"}

    return {"status": "pass", "message": "srz hybrid net stage chain executed deterministically"}

