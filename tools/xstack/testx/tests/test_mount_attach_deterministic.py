"""STRICT test: mount_attach is deterministic and symmetric."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_mount_attach_deterministic"
TEST_TAGS = ["strict", "mount", "determinism"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.mount.attach",
        "allowed_processes": ["process.mount_attach"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.mount_attach": "entitlement.tool.operating",
        },
        "process_privilege_requirements": {
            "process.mount_attach": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }


def _base_mount_points() -> list[dict]:
    return [
        {
            "schema_version": "1.0.0",
            "mount_point_id": "mount.point.a",
            "parent_assembly_id": "assembly.railcar.a",
            "mount_tags": ["mount.rail_coupler"],
            "alignment_constraints": {"profile": "rail.standard"},
            "state_machine_id": "state.mount.a",
            "connected_to_mount_point_id": None,
            "extensions": {"state_id": "detached"},
        },
        {
            "schema_version": "1.0.0",
            "mount_point_id": "mount.point.b",
            "parent_assembly_id": "assembly.railcar.b",
            "mount_tags": ["mount.rail_coupler"],
            "alignment_constraints": {"profile": "rail.standard"},
            "state_machine_id": "state.mount.b",
            "connected_to_mount_point_id": None,
            "extensions": {"state_id": "detached"},
        },
    ]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.interaction_testlib import authority_context, base_state, policy_context

    state_a = base_state()
    state_a["mount_points"] = _base_mount_points()
    state_b = copy.deepcopy(state_a)

    intent = {
        "intent_id": "intent.mount.attach.001",
        "process_id": "process.mount_attach",
        "inputs": {
            "mount_point_a_id": "mount.point.a",
            "mount_point_b_id": "mount.point.b",
        },
    }
    auth = authority_context(entitlements=["entitlement.tool.operating"], privilege_level="operator")
    law = _law_profile()
    policy = policy_context()

    first = execute_intent(
        state=state_a,
        intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    second = execute_intent(
        state=state_b,
        intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "mount_attach refused unexpectedly"}
    if str(first.get("state_hash_anchor", "")) != str(second.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "mount_attach state hash diverged across equivalent runs"}
    if list(state_a.get("mount_points") or []) != list(state_b.get("mount_points") or []):
        return {"status": "fail", "message": "mount points diverged across deterministic replay"}

    rows = sorted((dict(item) for item in list(state_a.get("mount_points") or []) if isinstance(item, dict)), key=lambda item: str(item.get("mount_point_id", "")))
    by_id = dict((str(row.get("mount_point_id", "")).strip(), row) for row in rows if str(row.get("mount_point_id", "")).strip())
    if str((dict(by_id.get("mount.point.a") or {})).get("connected_to_mount_point_id", "")).strip() != "mount.point.b":
        return {"status": "fail", "message": "mount.point.a did not connect to mount.point.b"}
    if str((dict(by_id.get("mount.point.b") or {})).get("connected_to_mount_point_id", "")).strip() != "mount.point.a":
        return {"status": "fail", "message": "mount.point.b did not connect to mount.point.a"}
    return {"status": "pass", "message": "mount_attach deterministic symmetry verified"}

