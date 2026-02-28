"""STRICT test: camera binding engine output is deterministic for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_camera_binding_deterministic"
TEST_TAGS = ["strict", "control", "view", "camera", "determinism"]


def _registry() -> dict:
    return {
        "view_policies": [
            {
                "schema_version": "1.0.0",
                "view_policy_id": "view.freecam_lab",
                "description": "Lab freecam",
                "camera_mode": "freecam",
                "allowed_epistemic_policy_ids": ["epistemic.admin_full"],
                "allowed_abstraction_levels": ["AL0", "AL1", "AL2", "AL3", "AL4"],
                "restrictions": {},
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "view_policy_id": "view.third_person_diegetic",
                "description": "Diegetic third person",
                "camera_mode": "third_person",
                "allowed_epistemic_policy_ids": ["epistemic.diegetic_default"],
                "allowed_abstraction_levels": ["AL0", "AL1", "AL2"],
                "restrictions": {},
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "view_policy_id": "view.first_person_diegetic",
                "description": "Diegetic first person",
                "camera_mode": "first_person",
                "allowed_epistemic_policy_ids": ["epistemic.diegetic_default"],
                "allowed_abstraction_levels": ["AL0", "AL1", "AL2"],
                "restrictions": {},
                "extensions": {},
            },
        ]
    }


def _existing_bindings() -> list:
    return [
        {
            "schema_version": "1.0.0",
            "subject_id": "agent.beta",
            "current_view_policy_id": "view.first_person_diegetic",
            "bound_spatial_id": None,
            "bound_pose_slot_id": None,
            "created_tick": 1,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control.view import apply_view_binding
    from tools.xstack.compatx.canonical_json import canonical_sha256

    kwargs = {
        "subject_id": "agent.alpha",
        "requested_view_policy_id": "view.freecam_lab",
        "view_policy_registry": _registry(),
        "existing_view_bindings": _existing_bindings(),
        "created_tick": 7,
        "bound_spatial_id": "",
        "bound_pose_slot_id": "",
        "allowed_view_policy_patterns": ["view.*"],
        "entitlements": ["entitlement.control.camera"],
        "ranked_server": True,
        "extensions": {"camera_id": "camera.main"},
    }
    first = apply_view_binding(**copy.deepcopy(kwargs))
    second = apply_view_binding(**copy.deepcopy(kwargs))

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "camera binding should succeed for deterministic fixture"}
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "camera binding output drifted for identical inputs"}
    if str(first.get("resolved_view_policy_id", "")).strip().lower().find("freecam") != -1:
        return {"status": "fail", "message": "ranked camera binding should not resolve to freecam"}
    if str(first.get("downgrade_reason", "")).strip() != "downgrade.rank_fairness":
        return {"status": "fail", "message": "ranked camera binding should record downgrade.rank_fairness"}
    return {"status": "pass", "message": "camera binding determinism check passed"}

