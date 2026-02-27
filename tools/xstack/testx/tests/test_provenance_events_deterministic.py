"""FAST test: construction provenance events are deterministic across identical runs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.provenance_events_deterministic"
TEST_TAGS = ["fast", "materials", "construction", "provenance", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_inventory,
    )

    state = with_inventory(
        with_inventory(
            base_state(),
            node_id="node.alpha",
            material_id="material.wood_basic",
            mass=10_000_000_000,
            batch_id="batch.wood.seed",
        ),
        node_id="node.alpha",
        material_id="material.stone_basic",
        mass=10_000_000_000,
        batch_id="batch.stone.seed",
    )
    law = law_profile(["process.construction_project_create", "process.construction_project_tick"])
    authority = authority_context(["entitlement.control.admin", "session.boot"], privilege_level="operator")
    policy = policy_context()

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.construction.project.create.provenance",
            "process_id": "process.construction_project_create",
            "inputs": {
                "blueprint_id": "blueprint.house.basic",
                "site_ref": "site.alpha",
                "logistics_node_id": "node.alpha",
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return {"result": created, "state": state}

    for index in range(8):
        ticked = execute_intent(
            state=state,
            intent={
                "intent_id": "intent.construction.project.tick.provenance.{}".format(index),
                "process_id": "process.construction_project_tick",
                "inputs": {"max_projects_per_tick": 16},
            },
            law_profile=copy.deepcopy(law),
            authority_context=copy.deepcopy(authority),
            navigation_indices={},
            policy_context=copy.deepcopy(policy),
        )
        if str(ticked.get("result", "")) != "complete":
            return {"result": ticked, "state": state}

    project_rows = sorted(
        [dict(row) for row in list(state.get("construction_projects") or []) if isinstance(row, dict)],
        key=lambda row: str(row.get("project_id", "")),
    )
    if not project_rows:
        return {"result": {"result": "refused"}, "state": state}
    project_id = str(project_rows[0].get("project_id", ""))
    events = sorted(
        [
            dict(row)
            for row in list(state.get("construction_provenance_events") or [])
            if isinstance(row, dict) and str(row.get("linked_project_id", "")) == project_id
        ],
        key=lambda row: (int(row.get("tick", 0) or 0), str(row.get("event_id", ""))),
    )
    return {"result": {"result": "complete"}, "state": state, "project_id": project_id, "events": events}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str((dict(first.get("result") or {})).get("result", "")) != "complete":
        return {"status": "fail", "message": "first provenance determinism run failed"}
    if str((dict(second.get("result") or {})).get("result", "")) != "complete":
        return {"status": "fail", "message": "second provenance determinism run failed"}

    first_state = copy.deepcopy(dict(first.get("state") or {}))
    second_state = copy.deepcopy(dict(second.get("state") or {}))
    if first_state != second_state:
        return {"status": "fail", "message": "construction provenance state diverged across identical runs"}

    first_events = list(first.get("events") or [])
    second_events = list(second.get("events") or [])
    if first_events != second_events:
        return {"status": "fail", "message": "construction provenance event stream diverged across identical runs"}
    if not first_events:
        return {"status": "fail", "message": "expected provenance events for deterministic construction run"}
    required_event_types = {
        "event.construct_project_created",
        "event.construct_step_started",
        "event.construct_step_completed",
        "event.material_consumed",
        "event.batch_created",
        "event.install_part",
    }
    observed_types = set(str(row.get("event_type_id", "")) for row in first_events)
    if not required_event_types.issubset(observed_types):
        return {"status": "fail", "message": "construction provenance stream missing required event types"}
    for row in first_events:
        if not str(row.get("event_id", "")).strip():
            return {"status": "fail", "message": "construction provenance event_id missing"}
        if not str(row.get("deterministic_fingerprint", "")).strip():
            return {"status": "fail", "message": "construction provenance deterministic_fingerprint missing"}
    return {"status": "pass", "message": "construction provenance events deterministic behavior passed"}

