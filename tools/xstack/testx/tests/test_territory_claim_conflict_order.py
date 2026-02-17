"""STRICT test: territory conflict resolution is deterministic under claim order variation."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.territory_claim_conflict_order"
TEST_TAGS = ["strict", "civilisation", "determinism"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.civ.territory",
        "allowed_processes": ["process.territory_claim"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.territory_claim": "entitlement.civ.claim",
        },
        "process_privilege_requirements": {
            "process.territory_claim": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "peer_id": "peer.admin",
        "privilege_level": "operator",
        "entitlements": ["entitlement.civ.claim", "entitlement.civ.admin"],
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
        "time_control": {"rate_permille": 1000, "paused": True, "accumulator_permille": 0},
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
                "extensions": {"owner_peer_id": "peer.admin"},
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
                "extensions": {"owner_peer_id": "peer.admin"},
            },
        ],
    }


def _run_with_order(first_faction: str, second_faction: str):
    from tools.xstack.sessionx.process_runtime import replay_intent_script

    intents = [
        {
            "intent_id": "intent.civ.claim.{}".format(first_faction),
            "process_id": "process.territory_claim",
            "inputs": {
                "faction_id": first_faction,
                "territory_id": "territory.shared.001",
            },
        },
        {
            "intent_id": "intent.civ.claim.{}".format(second_faction),
            "process_id": "process.territory_claim",
            "inputs": {
                "faction_id": second_faction,
                "territory_id": "territory.shared.001",
            },
        },
    ]
    return replay_intent_script(
        universe_state=copy.deepcopy(_state()),
        law_profile=_law_profile(),
        authority_context=_authority_context(),
        intents=intents,
        navigation_indices={},
        policy_context={},
    )


def _territory_owner(result: dict) -> tuple:
    state = dict(result.get("universe_state") or {})
    rows = sorted(
        (dict(row) for row in list(state.get("territory_assemblies") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("territory_id", "")),
    )
    if not rows:
        return ("", "", [])
    row = rows[0]
    extensions = dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {}
    contested = sorted(str(item).strip() for item in (extensions.get("contested_by_faction_ids") or []) if str(item).strip())
    return (
        str(row.get("owner_faction_id", "")).strip(),
        str(row.get("claim_status", "")).strip(),
        contested,
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_with_order("faction.alpha", "faction.beta")
    second = _run_with_order("faction.beta", "faction.alpha")
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "territory conflict script replay must complete"}

    first_owner, first_status, first_contested = _territory_owner(first)
    second_owner, second_status, second_contested = _territory_owner(second)
    if first_owner != second_owner or first_status != second_status:
        return {"status": "fail", "message": "territory conflict outcome changed with intent order"}
    if first_owner != "faction.alpha":
        return {"status": "fail", "message": "territory owner should resolve to deterministic lexical first faction"}
    if first_status != "contested":
        return {"status": "fail", "message": "territory status should be contested under conflicting claims"}
    if first_contested != second_contested:
        return {"status": "fail", "message": "contested-by set diverged under order variation"}
    return {"status": "pass", "message": "territory claim conflict ordering is deterministic"}

