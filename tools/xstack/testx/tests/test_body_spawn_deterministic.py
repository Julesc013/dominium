"""FAST test: EMB-0 body spawn helper is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_body_spawn_deterministic"
TEST_TAGS = ["fast", "embodiment", "session", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.embodiment import instantiate_body_system

    first = instantiate_body_system(
        subject_id="agent.emb.alpha",
        body_id="body.emb.alpha",
        position_mm={"x": 10, "y": 20, "z": 30},
        orientation_mdeg={"yaw": 90000, "pitch": 0, "roll": 0},
        created_tick=5,
        owner_agent_id="agent.emb.alpha",
        controller_id="controller.emb.alpha",
    )
    second = instantiate_body_system(
        subject_id="agent.emb.alpha",
        body_id="body.emb.alpha",
        position_mm={"x": 10, "y": 20, "z": 30},
        orientation_mdeg={"yaw": 90000, "pitch": 0, "roll": 0},
        created_tick=5,
        owner_agent_id="agent.emb.alpha",
        controller_id="controller.emb.alpha",
    )
    if dict(first) != dict(second):
        return {"status": "fail", "message": "instantiate_body_system must be deterministic for identical inputs"}
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "instantiate_body_system must complete"}
    if str((dict(first.get("body_template") or {})).get("template_id", "")) != "template.body.pill":
        return {"status": "fail", "message": "body spawn must resolve template.body.pill"}
    if str((dict(first.get("body_state") or {})).get("subject_id", "")) != "agent.emb.alpha":
        return {"status": "fail", "message": "body spawn must emit body_state for the subject"}
    if str(first.get("deterministic_fingerprint", "")) != str(second.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "body spawn fingerprint drifted across replay"}
    return {"status": "pass", "message": "EMB-0 body spawn determinism check passed"}
