"""STRICT test: deterministic instrument outputs for identical perceived inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.diegetics.instrument_determinism"
TEST_TAGS = ["strict", "diegetics", "epistemics", "observation"]


def _memory_store() -> dict:
    return {
        "schema_version": "1.0.0",
        "store_id": "memory.store.test.instrument",
        "owner_subject_id": "peer.alpha",
        "retention_policy_id": "ep.retention.session_basic",
        "items": [
            {
                "schema_version": "1.0.0",
                "memory_item_id": "mem.event.001",
                "owner_subject_id": "peer.alpha",
                "source_tick": 6,
                "last_refresh_tick": 9,
                "channel_id": "ch.core.process_log",
                "subject_kind": "event",
                "subject_id": "event.alpha",
                "payload": {"kind": "event.scan"},
                "precision_tag": "coarse",
                "ttl_ticks": 64,
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "memory_item_id": "mem.region.001",
                "owner_subject_id": "peer.alpha",
                "source_tick": 7,
                "last_refresh_tick": 11,
                "channel_id": "ch.diegetic.map_local",
                "subject_kind": "region",
                "subject_id": "region.alpha",
                "payload": {"navigation_row": {"kind": "terrain.hills"}},
                "precision_tag": "coarse",
                "ttl_ticks": 64,
                "extensions": {},
            },
        ],
        "store_hash": "",
        "extensions": {},
    }


def _instrument_rows() -> list[dict]:
    return [
        {
            "assembly_id": "instrument.radio_text",
            "instrument_type": "radio_text",
            "instrument_type_id": "instr.radio_text",
            "carrier_agent_id": None,
            "station_site_id": None,
            "reading": {},
            "state": {
                "inbox": [
                    {
                        "schema_version": "1.0.0",
                        "message_id": "msg.radio.beta",
                        "author_subject_id": "peer.beta",
                        "created_tick": 5,
                        "channel_id": "msg.radio",
                        "payload": {"to": "peer.alpha", "text": "beta"},
                        "signature": None,
                        "extensions": {},
                    },
                    {
                        "schema_version": "1.0.0",
                        "message_id": "msg.radio.alpha",
                        "author_subject_id": "peer.alpha",
                        "created_tick": 4,
                        "channel_id": "msg.radio",
                        "payload": {"to": "peer.beta", "text": "alpha"},
                        "signature": None,
                        "extensions": {},
                    },
                ]
            },
            "outputs": {},
            "quality": "nominal",
            "quality_value": 1000,
            "last_update_tick": 0,
        },
        {
            "assembly_id": "instrument.notebook",
            "instrument_type": "notebook",
            "instrument_type_id": "instr.notebook",
            "carrier_agent_id": None,
            "station_site_id": None,
            "reading": {},
            "state": {
                "user_notes": [
                    {
                        "schema_version": "1.0.0",
                        "message_id": "msg.notebook.beta",
                        "author_subject_id": "peer.beta",
                        "created_tick": 10,
                        "channel_id": "msg.notebook",
                        "payload": {"text": "beta note"},
                        "signature": None,
                        "extensions": {},
                    },
                    {
                        "schema_version": "1.0.0",
                        "message_id": "msg.notebook.alpha",
                        "author_subject_id": "peer.alpha",
                        "created_tick": 8,
                        "channel_id": "msg.notebook",
                        "payload": {"text": "alpha note"},
                        "signature": None,
                        "extensions": {},
                    },
                ]
            },
            "outputs": {},
            "quality": "nominal",
            "quality_value": 1000,
            "last_update_tick": 0,
        },
        {
            "assembly_id": "instrument.map_local",
            "instrument_type": "map_local",
            "instrument_type_id": "instr.map_local",
            "carrier_agent_id": None,
            "station_site_id": None,
            "reading": {},
            "state": {"entries": []},
            "outputs": {},
            "quality": "nominal",
            "quality_value": 1000,
            "last_update_tick": 0,
        },
        {
            "assembly_id": "instrument.compass",
            "instrument_type": "compass",
            "instrument_type_id": "instr.compass",
            "carrier_agent_id": None,
            "station_site_id": None,
            "reading": {},
            "state": {},
            "outputs": {},
            "quality": "nominal",
            "quality_value": 1000,
            "last_update_tick": 0,
        },
        {
            "assembly_id": "instrument.clock",
            "instrument_type": "clock",
            "instrument_type_id": "instr.clock",
            "carrier_agent_id": None,
            "station_site_id": None,
            "reading": {},
            "state": {},
            "outputs": {},
            "quality": "nominal",
            "quality_value": 1000,
            "last_update_tick": 0,
        },
    ]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from diegetics.instrument_kernel import compute_diegetic_instruments
    from tools.xstack.compatx.canonical_json import canonical_sha256

    perceived_now = {
        "camera_viewpoint": {
            "position_mm": {"x": 1250, "y": -500, "z": 4200},
            "orientation_mdeg": {"yaw": 12345, "pitch": 0, "roll": 0},
        },
        "time_state": {"tick": 12, "rate_permille": 1000, "paused": False},
    }
    requested = [
        "ch.diegetic.clock",
        "ch.diegetic.compass",
        "ch.diegetic.map_local",
        "ch.diegetic.notebook",
        "ch.diegetic.radio_text",
    ]

    first = compute_diegetic_instruments(
        perceived_now=copy.deepcopy(perceived_now),
        memory_store=copy.deepcopy(_memory_store()),
        instrument_rows=copy.deepcopy(_instrument_rows()),
        requested_channels=list(requested),
        simulation_tick=12,
    )
    second = compute_diegetic_instruments(
        perceived_now=copy.deepcopy(perceived_now),
        memory_store=copy.deepcopy(_memory_store()),
        instrument_rows=list(reversed(copy.deepcopy(_instrument_rows()))),
        requested_channels=list(reversed(requested)),
        simulation_tick=12,
    )
    first_hash = canonical_sha256(first)
    second_hash = canonical_sha256(second)
    if first_hash != second_hash:
        return {"status": "fail", "message": "instrument output hash diverged across equivalent input permutations"}
    if dict(first) != dict(second):
        return {"status": "fail", "message": "instrument payload diverged across equivalent input permutations"}
    return {"status": "pass", "message": "instrument outputs are deterministic for identical perceived inputs"}

