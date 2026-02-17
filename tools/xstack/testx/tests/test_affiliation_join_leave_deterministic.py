"""STRICT test: affiliation join/leave flow is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.affiliation_join_leave_deterministic"
TEST_TAGS = ["strict", "civilisation", "determinism"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.civ.affiliation",
        "allowed_processes": [
            "process.faction_create",
            "process.affiliation_join",
            "process.affiliation_leave",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.faction_create": "entitlement.civ.create_faction",
            "process.affiliation_join": "entitlement.civ.affiliation",
            "process.affiliation_leave": "entitlement.civ.affiliation",
        },
        "process_privilege_requirements": {
            "process.faction_create": "operator",
            "process.affiliation_join": "observer",
            "process.affiliation_leave": "observer",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "peer_id": "peer.alpha",
        "privilege_level": "operator",
        "entitlements": [
            "entitlement.civ.create_faction",
            "entitlement.civ.affiliation",
        ],
    }


def _state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "world_assemblies": [],
        "active_law_references": [],
        "session_references": [],
        "history_anchors": [],
        "agent_states": [
            {
                "agent_id": "agent.alpha",
                "state_hash": "0" * 64,
                "body_id": None,
                "owner_peer_id": "peer.alpha",
                "controller_id": None,
                "shard_id": "shard.0",
                "intent_scope_id": None,
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            }
        ],
    }


def _intents() -> list:
    return [
        {
            "intent_id": "intent.civ.affiliation.create",
            "process_id": "process.faction_create",
            "inputs": {
                "faction_id": "faction.alpha",
                "founder_agent_id": "agent.alpha",
                "governance_type_id": "gov.tribe",
            },
        },
        {
            "intent_id": "intent.civ.affiliation.join",
            "process_id": "process.affiliation_join",
            "inputs": {
                "subject_id": "agent.alpha",
                "faction_id": "faction.alpha",
                "role_id": "role.member",
            },
        },
        {
            "intent_id": "intent.civ.affiliation.leave",
            "process_id": "process.affiliation_leave",
            "inputs": {
                "subject_id": "agent.alpha",
            },
        },
    ]


def _run_once():
    from tools.xstack.sessionx.process_runtime import replay_intent_script

    return replay_intent_script(
        universe_state=copy.deepcopy(_state()),
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        intents=_intents(),
        navigation_indices={},
        policy_context={},
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "affiliation join/leave replay must complete"}
    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "affiliation join/leave final hash diverged"}
    if list(first.get("state_hash_anchors") or []) != list(second.get("state_hash_anchors") or []):
        return {"status": "fail", "message": "affiliation join/leave anchors diverged"}

    final_state = dict(first.get("universe_state") or {})
    affiliations = sorted(
        (dict(row) for row in list(final_state.get("affiliations") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("subject_id", "")),
    )
    if not affiliations:
        return {"status": "fail", "message": "expected affiliation row for subject after join/leave flow"}
    row = affiliations[0]
    if str(row.get("subject_id", "")) != "agent.alpha":
        return {"status": "fail", "message": "unexpected affiliation subject_id"}
    if row.get("faction_id") is not None:
        return {"status": "fail", "message": "subject should be unaffiliated after leave"}
    return {"status": "pass", "message": "affiliation join/leave deterministic replay passed"}

