"""STRICT test: refinement must not expose hidden-inventory/internal-state payloads."""

from __future__ import annotations

import json
import sys


TEST_ID = "testx.epistemics.lod_hidden_inventory_not_exposed"
TEST_TAGS = ["strict", "epistemics", "lod", "observation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.lod_invariance_testlib import (
        base_state,
        execute_region_transition,
        observe_state,
    )

    state = base_state(camera_x_mm=12345)
    # Seed suspicious truth-side tokens; perceived output must remain redacted.
    agent_rows = list(state.get("agent_states") or [])
    if agent_rows and isinstance(agent_rows[0], dict):
        agent_rows[0]["hidden_inventory"] = {"slot.alpha": "artifact.secret"}
        agent_rows[0]["internal_state"] = {"stress": 9001}
        state["agent_states"] = agent_rows
    body_rows = list(state.get("body_assemblies") or [])
    if body_rows and isinstance(body_rows[0], dict):
        body_rows[0]["micro_solver"] = {"native_precision": 123456}
        state["body_assemblies"] = body_rows

    expanded = execute_region_transition(
        state=state,
        process_id="process.region_expand",
        strict_contracts=True,
        memory_enabled=False,
        desired_tier="fine",
    )
    if str(expanded.get("result", "")) != "complete":
        return {"status": "fail", "message": "region_expand refused unexpectedly during hidden-state exposure check"}

    lod_summary = dict(expanded.get("lod_invariance") or {})
    if str(lod_summary.get("status", "")) != "ok":
        return {"status": "fail", "message": "lod invariance status is not ok after hidden-state seeded refinement"}
    if list(lod_summary.get("sensitive_paths") or []):
        return {"status": "fail", "message": "lod invariance detected sensitive paths after redaction: {}".format(",".join(lod_summary.get("sensitive_paths") or []))}

    observed = observe_state(state=state, memory_enabled=False)
    if str(observed.get("result", "")) != "complete":
        return {"status": "fail", "message": "observation refused unexpectedly during hidden-state exposure check"}
    serialized = json.dumps(dict(observed.get("perceived_model") or {}), sort_keys=True, separators=(",", ":")).lower()
    for token in ("hidden_inventory", "internal_state", "micro_solver", "native_precision"):
        if token in serialized:
            return {"status": "fail", "message": "perceived model leaked forbidden token '{}'".format(token)}
    return {"status": "pass", "message": "hidden inventory/internal-state remained non-exposed after refinement"}

