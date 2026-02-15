"""STRICT test: restrictive law fixture must refuse teleport with PROCESS_FORBIDDEN."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.session.script_law_forbidden_refusal"
TEST_TAGS = ["strict", "session"]


def _load_fixture(repo_root: str, rel_path: str):
    path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import replay_intent_script

    restrictive_law = _load_fixture(repo_root, "tools/xstack/testdata/session/law_profile.restrictive.fixture.json")
    script_payload = _load_fixture(repo_root, "tools/xstack/testdata/session/script.camera_nav.fixture.json")
    authority_context = {
        "authority_origin": "client",
        "experience_id": "profile.lab.developer",
        "law_profile_id": str(restrictive_law.get("law_profile_id", "")),
        "entitlements": [
            "session.boot",
            "entitlement.camera_control",
            "entitlement.teleport",
            "entitlement.time_control",
        ],
        "epistemic_scope": {
            "scope_id": "epistemic.lab.placeholder",
            "visibility_level": "placeholder",
        },
        "privilege_level": "operator",
    }
    universe_state = {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "agent_states": [],
        "world_assemblies": ["camera.main"],
        "active_law_references": [str(restrictive_law.get("law_profile_id", ""))],
        "session_references": ["session.testx.fixture"],
        "history_anchors": ["history.anchor.tick.0"],
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
        "time_control": {
            "rate_permille": 1000,
            "paused": False,
            "accumulator_permille": 0,
        },
        "process_log": [],
    }
    result = replay_intent_script(
        universe_state=universe_state,
        law_profile=restrictive_law,
        authority_context=authority_context,
        intents=list(script_payload.get("intents") or []),
    )
    if result.get("result") != "refused":
        return {"status": "fail", "message": "restrictive law fixture should refuse teleport process"}
    refusal = result.get("refusal") or {}
    if str(refusal.get("reason_code", "")) != "PROCESS_FORBIDDEN":
        return {"status": "fail", "message": "unexpected refusal reason for law-forbidden teleport"}
    if int(result.get("script_step", -1)) != 2:
        return {"status": "fail", "message": "restrictive law should refuse teleport deterministically at script step 2"}
    return {"status": "pass", "message": "law-forbidden teleport refusal check passed"}
