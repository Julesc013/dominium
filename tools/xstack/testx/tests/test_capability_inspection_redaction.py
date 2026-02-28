"""FAST test: capability inspection section is epistemically redacted."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_capability_inspection_redaction"
TEST_TAGS = ["fast", "inspection", "capability", "epistemic"]


def _state() -> dict:
    return {
        "simulation_time": {"tick": 42},
        "machine_assemblies": [
            {
                "schema_version": "1.0.0",
                "machine_id": "machine.alpha",
                "machine_type_id": "machine.type.test",
                "ports": ["port.alpha"],
                "operational_state": "idle",
                "policy_ids": [],
                "extensions": {},
            }
        ],
        "machine_ports": [
            {
                "schema_version": "1.0.0",
                "port_id": "port.alpha",
                "machine_id": "machine.alpha",
                "parent_structure_id": None,
                "port_type_id": "port.type.generic",
                "accepted_material_tags": [],
                "accepted_material_ids": [],
                "capacity_mass": None,
                "current_contents": [],
                "connected_to": None,
                "visibility_policy_id": None,
                "extensions": {},
            }
        ],
        "agent_states": [
            {
                "agent_id": "agent.alpha",
                "body_id": "body.agent.alpha",
                "faction_id": "faction.alpha",
                "status": "active",
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
            }
        ],
    }


def _law_profile(*, allow_hidden_state_access: bool) -> dict:
    return {
        "law_profile_id": "law.test.capability.inspect",
        "allowed_processes": ["process.inspect_generate_snapshot"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.inspect_generate_snapshot": "entitlement.inspect",
        },
        "process_privilege_requirements": {
            "process.inspect_generate_snapshot": "observer",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {
            "max_view_radius_km": 1000,
            "allow_hidden_state_access": bool(allow_hidden_state_access),
        },
    }


def _authority_context(visibility_level: str) -> dict:
    return {
        "authority_origin": "client",
        "peer_id": "peer.test.capability.inspect",
        "subject_id": "agent.alpha",
        "law_profile_id": "law.test.capability.inspect",
        "entitlements": ["entitlement.inspect"],
        "epistemic_scope": {"scope_id": "scope.test.capability.inspect", "visibility_level": str(visibility_level)},
        "privilege_level": "observer",
    }


def _policy_context() -> dict:
    return {
        "physics_profile_id": "physics.test.capability.inspect",
        "pack_lock_hash": "a" * 64,
        "budget_policy": {
            "policy_id": "policy.budget.capability.inspect",
            "max_regions_micro": 0,
            "max_entities_micro": 0,
            "max_compute_units_per_tick": 0,
            "entity_compute_weight": 0,
            "fallback_behavior": "degrade_fidelity",
            "tier_compute_weights": {"coarse": 0, "medium": 0, "fine": 0},
        },
        "budget_envelope_id": "budget.capability.inspect",
        "budget_envelope_registry": {
            "envelopes": [
                {
                    "envelope_id": "budget.capability.inspect",
                    "max_micro_entities_per_shard": 0,
                    "max_micro_regions_per_shard": 0,
                    "max_solver_cost_units_per_tick": 0,
                    "max_inspection_cost_units_per_tick": 64,
                    "extensions": {},
                }
            ]
        },
        "inspection_cache_policy_id": "cache.off",
        "inspection_cache_policy_registry": {
            "policies": [
                {
                    "cache_policy_id": "cache.off",
                    "enable_caching": False,
                    "invalidation_rules": [],
                    "max_cache_entries": 0,
                    "eviction_rule_id": "evict.none",
                    "extensions": {},
                }
            ]
        },
        "capability_bindings": [
            {
                "entity_id": "machine.alpha",
                "capability_id": "capability.can_be_driven",
                "parameters": {"control_binding_id": "binding.driver.alpha"},
                "created_tick": 42,
            }
        ],
    }


def _inspect(repo_root: str, visibility_level: str, *, allow_hidden_state_access: bool):
    from tools.xstack.sessionx.process_runtime import execute_intent

    state = _state()
    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.inspect.capability.{}".format(str(visibility_level)),
            "process_id": "process.inspect_generate_snapshot",
            "inputs": {
                "target_id": "machine.alpha",
                "desired_fidelity": "macro",
                "cost_units": 4,
            },
        },
        law_profile=copy.deepcopy(_law_profile(allow_hidden_state_access=allow_hidden_state_access)),
        authority_context=copy.deepcopy(_authority_context(visibility_level)),
        navigation_indices={},
        policy_context=copy.deepcopy(_policy_context()),
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    diegetic = _inspect(repo_root, "diegetic", allow_hidden_state_access=False)
    lab = _inspect(repo_root, "lab", allow_hidden_state_access=True)
    if str(diegetic.get("result", "")) != "complete" or str(lab.get("result", "")) != "complete":
        return {"status": "fail", "message": "inspection snapshot generation failed for capability redaction fixture"}

    diegetic_snapshot = dict(diegetic.get("inspection_snapshot") or {})
    lab_snapshot = dict(lab.get("inspection_snapshot") or {})
    diegetic_section = dict((dict(diegetic_snapshot.get("summary_sections") or {}).get("section.capabilities_summary")) or {})
    lab_section = dict((dict(lab_snapshot.get("summary_sections") or {}).get("section.capabilities_summary")) or {})
    diegetic_data = dict(diegetic_section.get("data") or {})
    lab_data = dict(lab_section.get("data") or {})

    diegetic_visible = sorted(str(item).strip() for item in list(diegetic_data.get("visible_capability_ids") or []) if str(item).strip())
    if "capability.has_ports" not in diegetic_visible:
        return {"status": "fail", "message": "diegetic capability summary should expose capability.has_ports for machine inspection"}
    if "capability.can_be_driven" in diegetic_visible:
        return {"status": "fail", "message": "diegetic capability summary leaked capability.can_be_driven without seat context"}
    if str(diegetic_data.get("epistemic_redaction", "")).strip() not in {"diegetic_filtered", "coarse_summary"}:
        return {"status": "fail", "message": "diegetic capability redaction marker missing"}

    lab_visible = sorted(str(item).strip() for item in list(lab_data.get("visible_capability_ids") or []) if str(item).strip())
    lab_all = sorted(str(item).strip() for item in list(lab_data.get("all_capability_ids") or []) if str(item).strip())
    if "capability.can_be_driven" not in lab_visible or "capability.can_be_driven" not in lab_all:
        return {"status": "fail", "message": "lab capability summary should expose full can_be_driven capability"}
    if str(lab_data.get("epistemic_redaction", "")).strip() != "none":
        return {"status": "fail", "message": "lab capability summary should not be redacted"}

    return {"status": "pass", "message": "capability inspection redaction is policy-gated"}
