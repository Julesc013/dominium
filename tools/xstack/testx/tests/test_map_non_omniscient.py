"""STRICT test: map_local instrument remains non-omniscient and memory-derived."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.diegetics.map_non_omniscient"
TEST_TAGS = ["strict", "diegetics", "epistemics", "observation"]


def _memory_store() -> dict:
    return {
        "schema_version": "1.0.0",
        "store_id": "memory.store.test.map",
        "owner_subject_id": "peer.alpha",
        "retention_policy_id": "ep.retention.session_basic",
        "items": [
            {
                "schema_version": "1.0.0",
                "memory_item_id": "mem.region.alpha",
                "owner_subject_id": "peer.alpha",
                "source_tick": 12,
                "last_refresh_tick": 14,
                "channel_id": "ch.diegetic.map_local",
                "subject_kind": "region",
                "subject_id": "region.alpha",
                "payload": {
                    "navigation_row": {
                        "kind": "terrain.plains"
                    }
                },
                "precision_tag": "coarse",
                "ttl_ticks": 64,
                "extensions": {},
            }
        ],
        "store_hash": "",
        "extensions": {},
    }


def _instrument_rows() -> list[dict]:
    return [
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
        }
    ]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from diegetics.instrument_kernel import compute_diegetic_instruments

    perceived_now = {
        "camera_viewpoint": {
            "position_mm": {"x": 0, "y": 0, "z": 1000},
            "orientation_mdeg": {"yaw": 90000, "pitch": 0, "roll": 0},
        },
        "time_state": {"tick": 20, "rate_permille": 1000, "paused": False},
        # Hidden truth-like payload should not appear in map output because map is memory-derived.
        "truth_overlay": {"hidden_region": "region.hidden"},
    }

    first = compute_diegetic_instruments(
        perceived_now=copy.deepcopy(perceived_now),
        memory_store=copy.deepcopy(_memory_store()),
        instrument_rows=copy.deepcopy(_instrument_rows()),
        requested_channels=["ch.diegetic.map_local"],
        simulation_tick=20,
    )
    second = compute_diegetic_instruments(
        perceived_now=copy.deepcopy(perceived_now),
        memory_store=copy.deepcopy(_memory_store()),
        instrument_rows=copy.deepcopy(_instrument_rows()),
        requested_channels=["ch.diegetic.map_local"],
        simulation_tick=20,
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "map_local instrument output diverged across identical inputs"}

    map_row = dict(first.get("instrument.map_local") or {})
    outputs = dict(map_row.get("outputs") or {})
    map_payload = dict(outputs.get("ch.diegetic.map_local") or {})
    entries = list(map_payload.get("entries") or [])
    entry_keys = sorted(str((row or {}).get("region_key", "")) for row in entries if isinstance(row, dict))
    if "region.alpha" not in entry_keys:
        return {"status": "fail", "message": "memory-derived discovered region missing from map_local output"}
    if "region.hidden" in entry_keys:
        return {"status": "fail", "message": "map_local leaked undiscovered region not present in memory inputs"}
    return {"status": "pass", "message": "map_local output remains non-omniscient and memory-derived"}

