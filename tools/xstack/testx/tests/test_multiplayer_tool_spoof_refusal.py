"""STRICT test: multiplayer interaction path refuses tool spoof attempts and records anti-cheat evidence."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_multiplayer_tool_spoof_refusal"
TEST_TAGS = ["strict", "interaction", "multiplayer", "anti_cheat", "tool"]


def _anti_cheat_runtime() -> dict:
    return {
        "anti_cheat": {
            "policy_id": "policy.ac.rank_strict",
            "modules_enabled": ["ac.module.authority_integrity"],
            "default_actions": {
                "ac.module.authority_integrity": "audit",
            },
            "extensions": {},
            "module_registry_map": {
                "ac.module.authority_integrity": {
                    "module_id": "ac.module.authority_integrity",
                }
            },
        },
        "server": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from client.interaction.interaction_dispatch import run_interaction_command
    from net.anti_cheat.anti_cheat_engine import ensure_runtime_channels
    from tools.xstack.testx.tests.interaction_testlib import authority_context, base_state, policy_context

    perceived_model = {
        "schema_version": "1.0.0",
        "viewpoint_id": "camera.main",
        "time_state": {"tick": 21},
        "channels": ["ch.core.entities"],
        "entities": {
            "entries": [
                {
                    "entity_id": "assembly.test.spoof",
                    "semantic_id": "assembly.test.spoof",
                    "entity_kind": "installed_structure",
                    "action_surfaces": [
                        {
                            "surface_type_id": "surface.handle",
                            "allowed_process_ids": ["process.tool_use_prepare"],
                            "visibility_policy_id": "visibility.default",
                            "local_transform": {
                                "position_mm": {"x": 0, "y": 0, "z": 0},
                                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                                "scale_permille": 1000,
                            },
                        }
                    ],
                }
            ]
        },
        "populations": {"entries": []},
        "control": {"orders": [], "institutions": []},
    }
    interaction_action_registry = {
        "actions": [
            {
                "action_id": "interaction.tool_use_prepare",
                "process_id": "process.tool_use_prepare",
                "display_name": "Prepare Tool",
                "target_kinds": ["installed_structure"],
                "parameter_schema_id": "dominium.intent.tool_prepare",
                "preview_mode": "cheap",
                "required_lens_channels": ["ch.core.entities"],
                "default_ui_hints": {},
                "extensions": {},
            }
        ]
    }
    law_profile = {
        "law_profile_id": "law.test.tool.spoof",
        "allowed_processes": ["process.tool_use_prepare"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.tool_use_prepare": "entitlement.tool.use",
        },
        "process_privilege_requirements": {
            "process.tool_use_prepare": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }
    auth = authority_context(entitlements=["entitlement.tool.use"], privilege_level="operator")
    auth["peer_id"] = "peer.test.tool.spoof"

    state = base_state()
    state["tool_assemblies"] = []
    state["tool_bindings"] = []

    policy = policy_context()
    policy["net_policy_id"] = "net.policy.server_authoritative.v1"
    runtime = _anti_cheat_runtime()
    ensure_runtime_channels(runtime)
    policy["anti_cheat_runtime"] = runtime

    listed = run_interaction_command(
        command="interact.list_affordances",
        perceived_model=copy.deepcopy(perceived_model),
        law_profile=copy.deepcopy(law_profile),
        authority_context=copy.deepcopy(auth),
        interaction_action_registry=copy.deepcopy(interaction_action_registry),
        target_semantic_id="assembly.test.spoof",
        state=state,
        policy_context=policy,
        include_disabled=True,
        repo_root=repo_root,
    )
    if str(listed.get("result", "")) != "complete":
        return {"status": "fail", "message": "interact.list_affordances refused unexpectedly"}
    affordances = list((dict(listed.get("affordance_list") or {})).get("affordances") or [])
    if len(affordances) != 1:
        return {"status": "fail", "message": "expected one affordance for spoof test target"}
    affordance_id = str((dict(affordances[0])).get("affordance_id", "")).strip()
    if not affordance_id:
        return {"status": "fail", "message": "missing affordance_id for spoof test"}

    executed = run_interaction_command(
        command="interact.execute",
        perceived_model=copy.deepcopy(perceived_model),
        law_profile=copy.deepcopy(law_profile),
        authority_context=copy.deepcopy(auth),
        interaction_action_registry=copy.deepcopy(interaction_action_registry),
        target_semantic_id="assembly.test.spoof",
        affordance_id=affordance_id,
        parameters={"subject_id": "agent.alpha"},
        state=state,
        policy_context=policy,
        peer_id="peer.test.tool.spoof",
        deterministic_sequence_number=2,
        submission_tick=21,
        include_disabled=True,
        repo_root=repo_root,
    )
    if str(executed.get("result", "")) != "refused":
        return {"status": "fail", "message": "tool spoof interaction should be refused"}
    reason_code = str((dict(executed.get("refusal") or {})).get("reason_code", "")).strip()
    if reason_code != "refusal.tool.bind_required":
        return {"status": "fail", "message": "tool spoof refusal reason code mismatch"}

    server_rows = dict(runtime.get("server") or {})
    events = list(server_rows.get("anti_cheat_events") or [])
    if not events:
        return {"status": "fail", "message": "tool spoof attempt did not produce anti-cheat event"}
    latest = dict(events[-1] or {})
    if str(latest.get("reason_code", "")).strip() != "refusal.tool.bind_required":
        return {"status": "fail", "message": "anti-cheat event reason code mismatch for spoof attempt"}
    return {"status": "pass", "message": "tool spoof refusal + anti-cheat evidence verified"}
