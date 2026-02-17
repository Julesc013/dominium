"""STRICT test: faction creation is deterministic for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.faction_create_deterministic"
TEST_TAGS = ["strict", "civilisation", "determinism"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.civ.faction_create",
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
        "peer_id": "peer.alpha",
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
            "intent_id": "intent.civ.faction_create.001",
            "process_id": "process.faction_create",
            "inputs": {
                "founder_agent_id": None,
                "governance_type_id": "gov.band",
                "human_name": "Band Alpha",
            },
        }
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
        return {"status": "fail", "message": "faction create replay must complete"}
    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "faction create final hash diverged across runs"}
    if list(first.get("state_hash_anchors") or []) != list(second.get("state_hash_anchors") or []):
        return {"status": "fail", "message": "faction create anchor sequence diverged across runs"}

    final_state = dict(first.get("universe_state") or {})
    faction_rows = sorted(
        (dict(row) for row in list(final_state.get("faction_assemblies") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("faction_id", "")),
    )
    if len(faction_rows) != 1:
        return {"status": "fail", "message": "expected exactly one faction assembly after creation"}
    row = faction_rows[0]
    if str(row.get("governance_type_id", "")) != "gov.band":
        return {"status": "fail", "message": "faction governance_type_id mismatch"}
    if str(row.get("status", "")) != "active":
        return {"status": "fail", "message": "faction status should be active after create"}
    return {"status": "pass", "message": "faction create deterministic replay passed"}

