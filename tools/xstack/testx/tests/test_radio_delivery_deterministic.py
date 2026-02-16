"""STRICT test: radio_text delivery scaffold is deterministic for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.diegetics.radio_delivery_deterministic"
TEST_TAGS = ["strict", "diegetics", "net", "epistemics"]


def _state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "camera_assemblies": [
            {
                "assembly_id": "camera.main",
                "frame_id": "frame.world",
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
                "lens_id": "lens.diegetic.sensor",
            }
        ],
        "instrument_assemblies": [
            {
                "assembly_id": "instrument.radio_text",
                "instrument_type": "radio_text",
                "instrument_type_id": "instr.radio_text",
                "carrier_agent_id": None,
                "station_site_id": None,
                "reading": {"messages": [], "message_count": 0},
                "state": {"inbox": []},
                "outputs": {"ch.diegetic.radio_text": {"messages": [], "message_count": 0}},
                "quality": "nominal",
                "quality_value": 1000,
                "last_update_tick": 0,
            }
        ],
    }


def _law() -> dict:
    return {
        "law_profile_id": "law.test.diegetic.radio",
        "allowed_processes": [
            "process.instrument_radio_send_text",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.instrument_radio_send_text": "entitlement.diegetic.radio_use",
        },
        "process_privilege_requirements": {
            "process.instrument_radio_send_text": "observer",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _authority() -> dict:
    return {
        "authority_origin": "client",
        "peer_id": "peer.alpha",
        "privilege_level": "observer",
        "entitlements": ["session.boot", "entitlement.diegetic.radio_use"],
    }


def _intents() -> list[dict]:
    return [
        {
            "intent_id": "intent.diegetic.radio.send.001",
            "process_id": "process.instrument_radio_send_text",
            "inputs": {
                "to": "peer.beta",
                "payload": {"text": "alpha->beta"},
            },
        },
        {
            "intent_id": "intent.diegetic.radio.send.002",
            "process_id": "process.instrument_radio_send_text",
            "inputs": {
                "to": "peer.gamma",
                "payload": {"text": "alpha->gamma"},
            },
        },
    ]


def _run_once():
    from tools.xstack.sessionx.process_runtime import replay_intent_script

    return replay_intent_script(
        universe_state=copy.deepcopy(_state()),
        law_profile=copy.deepcopy(_law()),
        authority_context=copy.deepcopy(_authority()),
        intents=copy.deepcopy(_intents()),
        navigation_indices={},
        policy_context={},
    )


def _radio_messages(result_payload: dict) -> list[dict]:
    universe = dict(result_payload.get("universe_state") or {})
    rows = list(universe.get("instrument_assemblies") or [])
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("assembly_id", "")) != "instrument.radio_text":
            continue
        state_payload = dict(row.get("state") or {})
        messages = list(state_payload.get("inbox") or [])
        return [dict(item) for item in messages if isinstance(item, dict)]
    return []


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "radio deterministic fixture replay did not complete"}

    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "radio delivery changed final state hash across identical runs"}
    if list(first.get("state_hash_anchors") or []) != list(second.get("state_hash_anchors") or []):
        return {"status": "fail", "message": "radio delivery changed anchor sequence across identical runs"}

    first_messages = _radio_messages(first)
    second_messages = _radio_messages(second)
    if first_messages != second_messages:
        return {"status": "fail", "message": "radio inbox payload diverged across identical runs"}
    if len(first_messages) != 2:
        return {"status": "fail", "message": "radio deterministic fixture expected exactly two delivered messages"}
    ordered_ids = [str(item.get("message_id", "")) for item in first_messages]
    if ordered_ids != sorted(ordered_ids):
        return {"status": "fail", "message": "radio messages are not deterministically ordered"}
    return {"status": "pass", "message": "radio text delivery scaffold is deterministic"}

