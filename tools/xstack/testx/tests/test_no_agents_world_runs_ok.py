"""STRICT test: CIV substrate runs deterministically in a world with zero agents."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.no_agents_world_runs_ok"
TEST_TAGS = ["strict", "civilisation", "smoke"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.civ.no_agents",
        "allowed_processes": ["process.faction_create"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.faction_create": "entitlement.civ.create_faction",
        },
        "process_privilege_requirements": {
            "process.faction_create": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "peer_id": "peer.no_agents",
        "privilege_level": "operator",
        "entitlements": ["entitlement.civ.create_faction"],
    }


def _state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "world_assemblies": [],
        "active_law_references": [],
        "session_references": [],
        "history_anchors": [],
        "agent_states": [],
    }


def _intents() -> list:
    return [
        {
            "intent_id": "intent.civ.no_agents.faction_create",
            "process_id": "process.faction_create",
            "inputs": {
                "faction_id": "faction.no_agents",
                "founder_agent_id": None,
                "governance_type_id": "gov.none",
                "human_name": "No Agents",
            },
        }
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
        return {"status": "fail", "message": "no-agent CIV script replay must complete"}
    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "no-agent CIV replay hash diverged"}

    final_state = dict(first.get("universe_state") or {})
    if list(final_state.get("agent_states") or []):
        return {"status": "fail", "message": "no-agent CIV baseline should keep agent_states empty"}
    factions = sorted(
        (dict(row) for row in list(final_state.get("faction_assemblies") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("faction_id", "")),
    )
    if len(factions) != 1:
        return {"status": "fail", "message": "expected one faction entry in no-agent CIV baseline"}
    row = factions[0]
    if row.get("founder_agent_id") is not None:
        return {"status": "fail", "message": "no-agent faction founder should remain null"}
    return {"status": "pass", "message": "no-agent world runs with CIV substrate"}

