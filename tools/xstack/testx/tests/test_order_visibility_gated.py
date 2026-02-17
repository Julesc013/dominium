"""STRICT test: order visibility in PerceivedModel is entitlement gated."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.order_visibility_gated"
TEST_TAGS = ["strict", "civilisation", "orders", "epistemics"]


def _truth_model() -> dict:
    return {
        "universe_state": {
            "simulation_time": {"tick": 12},
            "agent_states": [{"agent_id": "agent.alpha"}],
            "controller_assemblies": [
                {
                    "assembly_id": "controller.alpha",
                    "controller_type": "script",
                    "owner_peer_id": "peer.alpha",
                    "binding_ids": [],
                    "status": "active",
                }
            ],
            "control_bindings": [],
            "order_assemblies": [
                {
                    "order_id": "order.alpha",
                    "order_type_id": "order.move",
                    "issuer_subject_id": "peer.alpha",
                    "target_kind": "cohort",
                    "target_id": "cohort.alpha",
                    "created_tick": 10,
                    "status": "queued",
                    "priority": 80,
                    "payload": {"destination": "region.beta"},
                    "required_entitlements": ["entitlement.civ.order"],
                    "refusal": None,
                    "extensions": {},
                }
            ],
            "order_queue_assemblies": [
                {
                    "queue_id": "queue.alpha",
                    "owner_kind": "cohort",
                    "owner_id": "cohort.alpha",
                    "order_ids": ["order.alpha"],
                    "last_update_tick": 10,
                    "extensions": {},
                }
            ],
            "institution_assemblies": [
                {
                    "institution_id": "institution.alpha",
                    "institution_type_id": "inst.band_council",
                    "faction_id": "faction.alpha",
                    "status": "active",
                    "created_tick": 9,
                    "extensions": {},
                }
            ],
            "role_assignment_assemblies": [
                {
                    "assignment_id": "role_assignment.alpha",
                    "institution_id": "institution.alpha",
                    "subject_id": "cohort.alpha",
                    "role_id": "role.leader",
                    "granted_entitlements": ["entitlement.civ.order", "entitlement.civ.view_orders"],
                    "created_tick": 9,
                    "extensions": {},
                }
            ],
        }
    }


def _lens() -> dict:
    return {
        "lens_id": "lens.nondiegetic.debug",
        "lens_type": "nondiegetic",
        "required_entitlements": ["entitlement.inspect"],
        "observation_channels": ["ch.core.time", "ch.nondiegetic.entity_inspector"],
        "epistemic_constraints": {"visibility_policy": "debug"},
    }


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.order.visibility",
        "allowed_lenses": ["lens.nondiegetic.debug"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }


def _authority(entitlements: list[str]) -> dict:
    return {
        "authority_origin": "tool",
        "experience_id": "profile.lab.developer",
        "law_profile_id": "law.test.order.visibility",
        "entitlements": sorted(set(str(item).strip() for item in list(entitlements or []) if str(item).strip())),
        "epistemic_scope": {"scope_id": "scope.order.visibility", "visibility_level": "nondiegetic"},
        "privilege_level": "operator",
    }


def _epistemic_policy() -> dict:
    return {
        "epistemic_policy_id": "ep.policy.lab_broad",
        "allowed_observation_channels": ["ch.core.time", "ch.nondiegetic.entity_inspector"],
        "forbidden_channels": [],
        "retention_policy_id": "ep.retention.none",
        "inference_policy_id": "ep.infer.none",
        "max_precision_rules": [],
        "deterministic_filters": ["filter.channel_allow_deny.v1"],
        "extensions": {},
    }


def _retention_policy() -> dict:
    return {
        "retention_policy_id": "ep.retention.none",
        "memory_allowed": False,
        "max_memory_items": 0,
        "decay_model_id": "ep.decay.none",
        "deterministic_eviction_rule_id": "evict.oldest_first",
        "extensions": {},
    }


def _observe(entitlements: list[str]) -> dict:
    from tools.xstack.sessionx.observation import observe_truth

    return observe_truth(
        truth_model=copy.deepcopy(_truth_model()),
        lens=copy.deepcopy(_lens()),
        law_profile=copy.deepcopy(_law_profile()),
        authority_context=_authority(entitlements),
        viewpoint_id="view.order.visibility",
        epistemic_policy=copy.deepcopy(_epistemic_policy()),
        retention_policy=copy.deepcopy(_retention_policy()),
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    hidden = _observe(["entitlement.inspect", "lens.nondiegetic.access"])
    visible = _observe(["entitlement.inspect", "lens.nondiegetic.access", "entitlement.civ.view_orders"])

    if str(hidden.get("result", "")) != "complete" or str(visible.get("result", "")) != "complete":
        return {"status": "fail", "message": "observation runs should complete for valid nondiegetic inspector lens"}

    hidden_control = dict((dict(hidden.get("perceived_model") or {})).get("control") or {})
    visible_control = dict((dict(visible.get("perceived_model") or {})).get("control") or {})
    if list(hidden_control.get("orders") or []) or list(hidden_control.get("order_queues") or []):
        return {"status": "fail", "message": "orders should be hidden without entitlement.civ.view_orders"}
    if list(visible_control.get("orders") or []) == []:
        return {"status": "fail", "message": "orders should be visible with entitlement.civ.view_orders"}
    if list(visible_control.get("role_assignments") or []) == []:
        return {"status": "fail", "message": "role assignments should be visible with entitlement.civ.view_orders"}
    return {"status": "pass", "message": "order visibility gating passed"}

