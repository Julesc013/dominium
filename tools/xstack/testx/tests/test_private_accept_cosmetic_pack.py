"""STRICT test: private cosmetic policy accepts unsigned cosmetic packs deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.representation.private_accept_cosmetic_pack"
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
        "law_profile_id": "law.test.cosmetic.assign.private",
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


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "privilege_level": "operator",
        "entitlements": [
            "session.boot",
            "entitlement.cosmetic.assign",
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
        "representation_state": {"assignments": {}, "events": []},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import replay_intent_script

    result = replay_intent_script(
        universe_state=copy.deepcopy(_state()),
        law_profile=copy.deepcopy(_law_profile()),
        authority_context=copy.deepcopy(_authority_context()),
        intents=[
            {
                "intent_id": "intent.cosmetic.assign.private.accept",
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
    if str(result.get("result", "")) != "complete":
        refusal_payload = dict(result.get("refusal") or {})
        return {
            "status": "fail",
            "message": "private cosmetic assignment unexpectedly refused ({})".format(
                str(refusal_payload.get("reason_code", ""))
            ),
        }
    return {"status": "pass", "message": "private cosmetic policy accepts unsigned cosmetic pack"}

