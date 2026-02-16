"""STRICT test: cosmetic assignment requires entitlement and refuses deterministically when missing."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.representation.cosmetic_assign_entitlement_required"
TEST_TAGS = ["strict", "session", "representation", "cosmetics"]


def _state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "history_anchors": [],
        "agent_states": [
            {
                "agent_id": "agent.alpha",
                "state_hash": "0" * 64,
                "body_id": "body.agent.alpha",
                "owner_peer_id": "peer.alpha",
                "controller_id": "controller.alpha",
                "shard_id": "shard.0",
                "intent_scope_id": "",
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            }
        ],
    }


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.cosmetic.assign",
        "allowed_processes": ["process.cosmetic_assign"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.cosmetic_assign": "entitlement.cosmetic.assign",
        },
        "process_privilege_requirements": {
            "process.cosmetic_assign": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _authority_context_missing() -> dict:
    return {
        "authority_origin": "tool",
        "privilege_level": "operator",
        "entitlements": [
            "session.boot",
        ],
    }


def _policy_context() -> dict:
    return {
        "cosmetic_policy_id": "policy.cosmetics.private_relaxed",
        "cosmetic_registry": {
            "cosmetics": [
                {
                    "cosmetic_id": "cosmetic.default.pill",
                    "render_proxy_id": "render.proxy.pill_default",
                    "extensions": {"pack_id": "pack.representation.base"},
                }
            ]
        },
        "cosmetic_policy_registry": {
            "policies": [
                {
                    "policy_id": "policy.cosmetics.private_relaxed",
                    "allow_unsigned_packs": True,
                    "require_signed_packs": False,
                    "allowed_cosmetic_ids": [],
                    "allowed_pack_ids": [],
                    "extensions": {},
                }
            ]
        },
        "resolved_packs": [
            {"pack_id": "pack.representation.base", "signature_status": "unsigned"},
        ],
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import replay_intent_script

    result = replay_intent_script(
        universe_state=copy.deepcopy(_state()),
        law_profile=copy.deepcopy(_law_profile()),
        authority_context=copy.deepcopy(_authority_context_missing()),
        intents=[
            {
                "intent_id": "intent.cosmetic.assign.entitlement.missing",
                "process_id": "process.cosmetic_assign",
                "inputs": {
                    "agent_id": "agent.alpha",
                    "cosmetic_id": "cosmetic.default.pill",
                },
            }
        ],
        navigation_indices={},
        policy_context=copy.deepcopy(_policy_context()),
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "cosmetic assignment should refuse without entitlement"}
    refusal_payload = dict(result.get("refusal") or {})
    if str(refusal_payload.get("reason_code", "")) != "refusal.cosmetic.forbidden":
        return {"status": "fail", "message": "unexpected cosmetic entitlement refusal code"}
    return {"status": "pass", "message": "cosmetic assignment entitlement gate refusal passed"}

