"""STRICT test: notebook note writing requires deterministic entitlement gating."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.diegetics.notebook_write_entitlement"
TEST_TAGS = ["strict", "diegetics", "control", "epistemics"]


def _state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "camera_assemblies": [
            {
                "assembly_id": "camera.main",
                "frame_id": "frame.world",
                "position_mm": {"x": 0, "y": 0, "z": 1000},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
                "lens_id": "lens.diegetic.sensor",
            }
        ],
        "instrument_assemblies": [
            {
                "assembly_id": "instrument.notebook",
                "instrument_type": "notebook",
                "instrument_type_id": "instr.notebook",
                "carrier_agent_id": None,
                "station_site_id": None,
                "reading": {"entries": []},
                "state": {"user_notes": []},
                "outputs": {"ch.diegetic.notebook": {"entries": [], "entry_count": 0}},
                "quality": "nominal",
                "quality_value": 1000,
                "last_update_tick": 0,
            }
        ],
    }


def _law() -> dict:
    return {
        "law_profile_id": "law.test.diegetic.notebook",
        "allowed_processes": [
            "process.instrument_notebook_add_note",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.instrument_notebook_add_note": "entitlement.diegetic.notebook_write",
        },
        "process_privilege_requirements": {
            "process.instrument_notebook_add_note": "observer",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
    }


def _authority_without_write() -> dict:
    return {
        "authority_origin": "tool",
        "privilege_level": "observer",
        "entitlements": ["session.boot"],
    }


def _intent() -> dict:
    return {
        "intent_id": "intent.diegetic.notebook.add_note.001",
        "process_id": "process.instrument_notebook_add_note",
        "inputs": {
            "text": "landmark logged",
        },
    }


def _run_once():
    from tools.xstack.sessionx.process_runtime import replay_intent_script

    return replay_intent_script(
        universe_state=copy.deepcopy(_state()),
        law_profile=copy.deepcopy(_law()),
        authority_context=copy.deepcopy(_authority_without_write()),
        intents=[_intent()],
        navigation_indices={},
        policy_context={},
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "refused" or str(second.get("result", "")) != "refused":
        return {"status": "fail", "message": "notebook add_note without entitlement must refuse deterministically"}

    reason_first = str((dict(first.get("refusal") or {}).get("reason_code", "")))
    reason_second = str((dict(second.get("refusal") or {}).get("reason_code", "")))
    allowed_reason_codes = {
        "ENTITLEMENT_MISSING",
        "refusal.control.entitlement_missing",
    }
    if reason_first not in allowed_reason_codes or reason_second not in allowed_reason_codes:
        return {"status": "fail", "message": "unexpected notebook write entitlement refusal code"}
    if dict(first.get("refusal") or {}) != dict(second.get("refusal") or {}):
        return {"status": "fail", "message": "notebook entitlement refusal payload must be deterministic"}
    return {"status": "pass", "message": "notebook write entitlement gating determinism check passed"}

