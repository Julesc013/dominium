"""STRICT test: SessionSpec network payload deterministically controls net stage pipeline composition."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.pipeline_net_handshake_stage"
TEST_TAGS = ["strict", "session", "net"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.pipeline_contract import load_session_pipeline_contract

    local_result = create_session_spec(
        repo_root=repo_root,
        save_id="save.testx.net.pipeline.local",
        bundle_id="bundle.base.lab",
        scenario_id="scenario.lab.galaxy_nav",
        mission_id="",
        experience_id="profile.lab.developer",
        law_profile_id="law.lab.unrestricted",
        parameter_bundle_id="params.lab.placeholder",
        budget_policy_id="policy.budget.default_lab",
        fidelity_policy_id="policy.fidelity.default_lab",
        rng_seed_string="seed.mp2.pipeline.local",
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string="seed.mp2.pipeline.universe.local",
        universe_id="",
        entitlements=["session.boot", "entitlement.inspect"],
        epistemic_scope_id="epistemic.lab.placeholder",
        visibility_level="placeholder",
        privilege_level="operator",
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if str(local_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "local session create failed unexpectedly"}

    local_pipeline_id = "pipeline.client.default"
    local_contract = load_session_pipeline_contract(repo_root=repo_root, pipeline_id=local_pipeline_id)
    if str(local_contract.get("result", "")) != "complete":
        return {"status": "fail", "message": "failed to load pipeline.client.default contract"}
    local_stage_order = list(local_contract.get("stage_order") or [])
    if "stage.net_handshake" in local_stage_order:
        return {"status": "fail", "message": "pipeline.client.default must not include stage.net_handshake"}

    net_result = create_session_spec(
        repo_root=repo_root,
        save_id="save.testx.net.pipeline.net",
        bundle_id="bundle.base.lab",
        scenario_id="scenario.lab.galaxy_nav",
        mission_id="",
        experience_id="profile.lab.developer",
        law_profile_id="law.lab.unrestricted",
        parameter_bundle_id="params.lab.placeholder",
        budget_policy_id="policy.budget.default_lab",
        fidelity_policy_id="policy.fidelity.default_lab",
        rng_seed_string="seed.mp2.pipeline.net",
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string="seed.mp2.pipeline.universe.net",
        universe_id="",
        entitlements=["session.boot", "entitlement.inspect"],
        epistemic_scope_id="epistemic.lab.placeholder",
        visibility_level="placeholder",
        privilege_level="operator",
        net_endpoint="loopback://mp2.pipeline.stage",
        net_transport_id="transport.loopback",
        net_client_peer_id="peer.client.pipeline",
        net_server_peer_id="peer.server.pipeline",
        net_replication_policy_id="policy.net.lockstep",
        net_anti_cheat_policy_id="policy.ac.casual_default",
        net_server_policy_id="server.policy.private.default",
        net_securex_policy_id="",
        net_desired_law_profile_id="",
        net_schema_versions=[],
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if str(net_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "networked session create failed unexpectedly"}

    net_pipeline_id = "pipeline.client.multiplayer_stub"
    net_contract = load_session_pipeline_contract(repo_root=repo_root, pipeline_id=net_pipeline_id)
    if str(net_contract.get("result", "")) != "complete":
        return {"status": "fail", "message": "failed to load pipeline.client.multiplayer_stub contract"}
    net_stage_order = list(net_contract.get("stage_order") or [])
    required_net_chain = ["stage.net_handshake", "stage.net_sync_baseline", "stage.net_join_world"]
    if any(stage_id not in net_stage_order for stage_id in required_net_chain):
        return {"status": "fail", "message": "multiplayer pipeline missing required net stage chain"}
    positions = [net_stage_order.index(stage_id) for stage_id in required_net_chain]
    if positions != sorted(positions):
        return {"status": "fail", "message": "net stage chain order is nondeterministic"}

    return {"status": "pass", "message": "session pipeline net stage inclusion/exclusion is deterministic"}
