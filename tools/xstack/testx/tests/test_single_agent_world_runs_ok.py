"""STRICT test: CIV substrate runs deterministically in a single-agent world."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.single_agent_world_runs_ok"
TEST_TAGS = ["strict", "civilisation", "smoke"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.civ.single_agent",
        "allowed_processes": [
            "process.faction_create",
            "process.affiliation_join",
            "process.territory_claim",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.faction_create": "entitlement.civ.create_faction",
            "process.affiliation_join": "entitlement.civ.affiliation",
            "process.territory_claim": "entitlement.civ.claim",
        },
        "process_privilege_requirements": {
            "process.faction_create": "operator",
            "process.affiliation_join": "observer",
            "process.territory_claim": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "peer_id": "peer.single",
        "privilege_level": "operator",
        "entitlements": [
            "entitlement.civ.create_faction",
            "entitlement.civ.affiliation",
            "entitlement.civ.claim",
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
                "agent_id": "agent.single",
                "state_hash": "1" * 64,
                "body_id": None,
                "owner_peer_id": "peer.single",
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
            "intent_id": "intent.civ.single.faction_create",
            "process_id": "process.faction_create",
            "inputs": {
                "faction_id": "faction.single",
                "founder_agent_id": "agent.single",
                "governance_type_id": "gov.band",
            },
        },
        {
            "intent_id": "intent.civ.single.affiliation_join",
            "process_id": "process.affiliation_join",
            "inputs": {
                "subject_id": "agent.single",
                "faction_id": "faction.single",
            },
        },
        {
            "intent_id": "intent.civ.single.territory_claim",
            "process_id": "process.territory_claim",
            "inputs": {
                "faction_id": "faction.single",
                "territory_id": "territory.single.001",
            },
        },
    ]


def _run_once() -> dict:
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
        return {"status": "fail", "message": "single-agent CIV script replay must complete"}
    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "single-agent CIV replay hash diverged"}

    final_state = dict(first.get("universe_state") or {})
    factions = sorted(
        (dict(row) for row in list(final_state.get("faction_assemblies") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("faction_id", "")),
    )
    if len(factions) != 1:
        return {"status": "fail", "message": "single-agent world should contain one faction after script"}
    if str(factions[0].get("faction_id", "")) != "faction.single":
        return {"status": "fail", "message": "single-agent faction_id mismatch"}

    affiliations = sorted(
        (dict(row) for row in list(final_state.get("affiliations") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("subject_id", "")),
    )
    if len(affiliations) != 1:
        return {"status": "fail", "message": "single-agent world should contain one affiliation row"}
    affiliation = affiliations[0]
    if str(affiliation.get("subject_id", "")) != "agent.single" or str(affiliation.get("faction_id", "")) != "faction.single":
        return {"status": "fail", "message": "single-agent affiliation mapping mismatch"}

    territories = sorted(
        (dict(row) for row in list(final_state.get("territory_assemblies") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("territory_id", "")),
    )
    if len(territories) != 1:
        return {"status": "fail", "message": "single-agent world should contain one territory row"}
    territory = territories[0]
    if str(territory.get("owner_faction_id", "")) != "faction.single":
        return {"status": "fail", "message": "single-agent territory owner mismatch"}
    if str(territory.get("claim_status", "")) != "claimed":
        return {"status": "fail", "message": "single-agent territory claim status mismatch"}
    return {"status": "pass", "message": "single-agent world runs with CIV substrate"}

