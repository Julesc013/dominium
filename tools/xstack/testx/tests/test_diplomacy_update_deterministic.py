"""STRICT test: diplomacy relation updates are deterministic and symmetric in CIV-1."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.diplomacy_update_deterministic"
TEST_TAGS = ["strict", "civilisation", "determinism"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.civ.diplomacy",
        "allowed_processes": ["process.diplomacy_set_relation"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.diplomacy_set_relation": "entitlement.civ.diplomacy",
        },
        "process_privilege_requirements": {
            "process.diplomacy_set_relation": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "peer_id": "peer.alpha",
        "privilege_level": "operator",
        "entitlements": ["entitlement.civ.diplomacy"],
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
        "faction_assemblies": [
            {
                "faction_id": "faction.alpha",
                "human_name": "Alpha",
                "description": "",
                "created_tick": 0,
                "founder_agent_id": None,
                "governance_type_id": "gov.none",
                "territory_ids": [],
                "diplomatic_relations": {},
                "status": "active",
                "extensions": {"owner_peer_id": "peer.alpha"},
            },
            {
                "faction_id": "faction.beta",
                "human_name": "Beta",
                "description": "",
                "created_tick": 0,
                "founder_agent_id": None,
                "governance_type_id": "gov.none",
                "territory_ids": [],
                "diplomatic_relations": {},
                "status": "active",
                "extensions": {"owner_peer_id": "peer.alpha"},
            },
        ],
    }


def _intents() -> list:
    return [
        {
            "intent_id": "intent.civ.diplomacy.set_relation",
            "process_id": "process.diplomacy_set_relation",
            "inputs": {
                "faction_a": "faction.beta",
                "faction_b": "faction.alpha",
                "relation_state": "allied",
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
        return {"status": "fail", "message": "diplomacy update replay must complete"}
    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "diplomacy update final hash diverged"}
    if list(first.get("state_hash_anchors") or []) != list(second.get("state_hash_anchors") or []):
        return {"status": "fail", "message": "diplomacy update anchor sequence diverged"}

    final_state = dict(first.get("universe_state") or {})
    relation_rows = sorted(
        (dict(row) for row in list(final_state.get("diplomatic_relations") or []) if isinstance(row, dict)),
        key=lambda row: (str(row.get("faction_a", "")), str(row.get("faction_b", ""))),
    )
    if len(relation_rows) != 1:
        return {"status": "fail", "message": "expected one canonical diplomatic relation row"}
    row = relation_rows[0]
    if str(row.get("faction_a", "")) != "faction.alpha" or str(row.get("faction_b", "")) != "faction.beta":
        return {"status": "fail", "message": "diplomatic relation pair should be canonicalized lexicographically"}
    if str(row.get("relation_state", "")) != "allied":
        return {"status": "fail", "message": "diplomatic relation_state mismatch"}

    factions = sorted(
        (dict(entry) for entry in list(final_state.get("faction_assemblies") or []) if isinstance(entry, dict)),
        key=lambda entry: str(entry.get("faction_id", "")),
    )
    if len(factions) != 2:
        return {"status": "fail", "message": "expected two faction rows in final state"}
    alpha = factions[0]
    beta = factions[1]
    alpha_map = dict(alpha.get("diplomatic_relations") or {}) if isinstance(alpha.get("diplomatic_relations"), dict) else {}
    beta_map = dict(beta.get("diplomatic_relations") or {}) if isinstance(beta.get("diplomatic_relations"), dict) else {}
    if str(alpha_map.get("faction.beta", "")) != "allied":
        return {"status": "fail", "message": "faction.alpha relation map missing allied edge to faction.beta"}
    if str(beta_map.get("faction.alpha", "")) != "allied":
        return {"status": "fail", "message": "faction.beta relation map missing allied edge to faction.alpha"}
    return {"status": "pass", "message": "diplomacy deterministic replay passed"}

