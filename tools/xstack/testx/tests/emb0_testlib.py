"""Shared EMB-0 embodiment TestX fixtures."""

from __future__ import annotations

import copy


def law_profile(allowed_processes: list[str]) -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile as base_law_profile

    unique_processes = sorted(set(str(item).strip() for item in list(allowed_processes or []) if str(item).strip()))
    law = base_law_profile(unique_processes)
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    if "process.body_apply_input" in unique_processes:
        entitlements["process.body_apply_input"] = "entitlement.control.possess"
        privileges["process.body_apply_input"] = "operator"
    if "process.body_jump" in unique_processes:
        entitlements["process.body_jump"] = "ent.move.jump"
        privileges["process.body_jump"] = "operator"
    if "process.body_tick" in unique_processes:
        entitlements["process.body_tick"] = "session.boot"
        privileges["process.body_tick"] = "observer"
    if "process.camera_set_view_mode" in unique_processes:
        entitlements["process.camera_set_view_mode"] = "entitlement.control.camera"
        privileges["process.camera_set_view_mode"] = "observer"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    law["allowed_lenses"] = ["lens.diegetic.sensor", "lens.nondiegetic.debug"]
    return law


def authority_context(entitlements: list[str] | None = None, privilege_level: str = "operator") -> dict:
    from tools.xstack.testx.tests.construction_testlib import authority_context as base_authority_context

    rows = sorted(
        set(
            ["session.boot"]
            + [str(item).strip() for item in list(entitlements or []) if str(item).strip()]
        )
    )
    return base_authority_context(rows, privilege_level=privilege_level)


def policy_context(max_compute_units_per_tick: int = 512) -> dict:
    from tools.xstack.testx.tests.construction_testlib import policy_context as base_policy_context

    policy = copy.deepcopy(base_policy_context(max_compute_units_per_tick=int(max(1, int(max_compute_units_per_tick)))))
    policy["control_policy"] = {
        "allowed_view_modes": [
            "view.first_person.player",
            "view.third_person.player",
            "view.free.lab",
            "view.free.observer_truth",
        ],
        "allowed_view_policies": [
            "view.first_person_diegetic",
            "view.third_person_diegetic",
            "view.freecam_lab",
            "view.observer_truth",
        ],
        "allow_cross_shard_follow": True,
    }
    return policy


def seed_embodied_state(
    *,
    subject_id: str = "agent.emb.test",
    body_id: str = "body.emb.test",
    controller_id: str = "controller.emb.test",
    peer_id: str = "peer.emb.test",
    mass_value: int = 5,
    gravity_vector: dict | None = None,
    include_camera: bool = True,
) -> dict:
    from embodiment import instantiate_body_system
    from fields import build_field_cell, build_field_layer
    from tools.xstack.testx.tests.construction_testlib import base_state

    state = copy.deepcopy(base_state())
    spawned = instantiate_body_system(
        subject_id=str(subject_id),
        body_id=str(body_id),
        position_mm={"x": 0, "y": 0, "z": 0},
        orientation_mdeg={"yaw": 0, "pitch": 0, "roll": 0},
        created_tick=0,
        shard_id="shard.0",
        owner_agent_id=str(subject_id),
        controller_id=str(controller_id),
    )
    momentum_state = dict(spawned.get("momentum_state") or {})
    momentum_state["mass_value"] = int(max(1, int(mass_value)))

    state["body_assemblies"] = [dict(spawned.get("body_assembly") or {})]
    state["body_states"] = [dict(spawned.get("body_state") or {})]
    state["momentum_states"] = [momentum_state]
    state["system_template_instance_record_rows"] = [dict(spawned.get("template_instance_record") or {})]
    state["template_instance_record_hash_chain"] = ""
    state["force_application_rows"] = []
    state["field_layers"] = []
    state["field_cells"] = []
    state["agent_states"] = [
        {
            "agent_id": str(subject_id),
            "state_hash": "0" * 64,
            "body_id": str(body_id),
            "owner_peer_id": str(peer_id),
            "controller_id": str(controller_id),
            "shard_id": "shard.0",
            "intent_scope_id": "",
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
        }
    ]
    state["controller_assemblies"] = [
        {
            "assembly_id": str(controller_id),
            "controller_type": "script",
            "owner_peer_id": str(peer_id),
            "allowed_actions": ["control.action.possess_agent", "control.action.camera"],
            "binding_ids": [
                "binding.control.possess.emb",
                "binding.control.camera.emb",
            ],
            "status": "active",
        }
    ]
    state["control_bindings"] = [
        {
            "binding_id": "binding.control.possess.emb",
            "controller_id": str(controller_id),
            "binding_type": "possess",
            "target_id": str(subject_id),
            "created_tick": 0,
            "active": True,
            "required_entitlements": ["entitlement.control.possess"],
        },
        {
            "binding_id": "binding.control.camera.emb",
            "controller_id": str(controller_id),
            "binding_type": "camera",
            "target_id": "camera.main",
            "created_tick": 0,
            "active": True,
            "required_entitlements": ["entitlement.control.camera"],
        },
    ]
    state["camera_assemblies"] = [
        {
            "assembly_id": "camera.main",
            "frame_id": "frame.world",
            "position_mm": {"x": 0, "y": 0, "z": 1600},
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
            "lens_id": "lens.diegetic.sensor",
            "binding_id": "binding.control.camera.emb",
            "view_mode_id": "view.first_person.player",
            "owner_peer_id": str(peer_id),
            "target_type": "agent",
            "target_id": str(subject_id),
            "offset_params": {"x_mm": 0, "y_mm": 0, "z_mm": 0, "yaw_mdeg": 0, "pitch_mdeg": 0, "roll_mdeg": 0},
        }
    ] if include_camera else []
    state["collision_state"] = {
        "last_tick_resolved_pairs": [],
        "last_tick_unresolved_pairs": [],
        "last_tick_pair_count": 0,
        "last_tick_anchor": "",
    }

    if isinstance(gravity_vector, dict):
        state["field_layers"] = [
            build_field_layer(
                field_id="field.gravity_vector",
                field_type_id="field.gravity_vector",
                spatial_scope_id="spatial.emb.test",
                resolution_level="macro",
                update_policy_id="field.static",
                extensions={},
            )
        ]
        state["field_cells"] = [
            build_field_cell(
                field_id="field.gravity_vector",
                cell_id="cell.0.0.0",
                value={
                    "x": int(gravity_vector.get("x", 0) or 0),
                    "y": int(gravity_vector.get("y", 0) or 0),
                    "z": int(gravity_vector.get("z", 0) or 0),
                },
                last_updated_tick=0,
                value_kind="vector",
                extensions={},
            )
        ]
    return state


def replay_body_motion(
    *,
    gravity_vector: dict | None = None,
    include_lens_update: bool = False,
) -> dict:
    from tools.xstack.sessionx.process_runtime import replay_intent_script

    allowed_processes = ["process.body_apply_input", "process.body_tick"]
    entitlements = ["entitlement.control.possess"]
    if include_lens_update:
        entitlements.extend(["entitlement.control.camera"])
    return replay_intent_script(
        universe_state=seed_embodied_state(gravity_vector=gravity_vector, include_camera=True),
        law_profile=law_profile(allowed_processes),
        authority_context=authority_context(entitlements, privilege_level="operator"),
        intents=[
            {
                "intent_id": "intent.emb.body_apply_input.001",
                "process_id": "process.body_apply_input",
                "inputs": {
                    "body_id": "body.emb.test",
                    "move_vector_local": {"x": 1000, "y": 0, "z": 0},
                    "look_vector": {"x": 0, "y": 0, "z": 0},
                    "dt_ticks": 1,
                },
            },
            {
                "intent_id": "intent.emb.body_tick.001",
                "process_id": "process.body_tick",
                "inputs": {
                    "body_id": "body.emb.test",
                    "dt_ticks": 1,
                    "camera_id": "camera.main" if include_lens_update else "",
                    "lens_profile_id": "lens.fp" if include_lens_update else "",
                },
            },
        ],
        navigation_indices={},
        policy_context=policy_context(),
    )
