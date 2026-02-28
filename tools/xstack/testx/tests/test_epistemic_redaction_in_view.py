"""FAST test: active view policy constrains epistemic policy and redaction deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_epistemic_redaction_in_view"
TEST_TAGS = ["fast", "control", "view", "epistemic"]


def _state() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "view_bindings": [
            {
                "schema_version": "1.0.0",
                "subject_id": "agent.alpha",
                "current_view_policy_id": "view.spectator_limited",
                "bound_spatial_id": None,
                "bound_pose_slot_id": None,
                "created_tick": 0,
                "deterministic_fingerprint": "",
                "extensions": {},
            }
        ],
    }


def _policy_context() -> dict:
    return {
        "view_policy_registry": {
            "view_policies": [
                {
                    "schema_version": "1.0.0",
                    "view_policy_id": "view.spectator_limited",
                    "description": "Limited spectator view.",
                    "camera_mode": "spectator",
                    "allowed_epistemic_policy_ids": ["epistemic.rank_restricted"],
                    "allowed_abstraction_levels": ["AL0", "AL1"],
                    "restrictions": {},
                    "extensions": {},
                }
            ]
        },
        "epistemic_policy_registry": {
            "policies": [
                {
                    "schema_version": "1.0.0",
                    "epistemic_policy_id": "epistemic.admin_full",
                    "description": "Admin full detail.",
                    "max_inspection_level": "micro",
                    "max_reenactment_level": "micro",
                    "redaction_rules": [],
                    "extensions": {},
                },
                {
                    "schema_version": "1.0.0",
                    "epistemic_policy_id": "epistemic.rank_restricted",
                    "description": "Rank restricted detail.",
                    "max_inspection_level": "meso",
                    "max_reenactment_level": "meso",
                    "redaction_rules": [
                        {
                            "channel_pattern": "ch.truth.overlay.*",
                            "redaction_mode": "masked",
                            "reason_code": "redaction.epistemic.rank_restricted",
                        }
                    ],
                    "extensions": {},
                },
            ]
        },
    }


def _authority_context() -> dict:
    return {
        "subject_id": "agent.alpha",
        "peer_id": "peer.alpha",
        "epistemic_scope": {"scope_id": "epistemic.admin_full", "visibility_level": "nondiegetic"},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.sessionx.process_runtime import _resolve_effective_epistemic_policy

    state = _state()
    policy_context = _policy_context()
    authority_context = _authority_context()
    law_profile = {"law_profile_id": "law.test.epistemic"}

    first = _resolve_effective_epistemic_policy(
        state=copy.deepcopy(state),
        authority_context=copy.deepcopy(authority_context),
        law_profile=copy.deepcopy(law_profile),
        policy_context=copy.deepcopy(policy_context),
    )
    second = _resolve_effective_epistemic_policy(
        state=copy.deepcopy(state),
        authority_context=copy.deepcopy(authority_context),
        law_profile=copy.deepcopy(law_profile),
        policy_context=copy.deepcopy(policy_context),
    )

    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "view-bound epistemic resolution drifted for identical inputs"}
    if str(first.get("epistemic_policy_id", "")) != "epistemic.rank_restricted":
        return {"status": "fail", "message": "view policy should constrain epistemic policy to epistemic.rank_restricted"}
    if str(first.get("max_inspection_level", "")) != "meso":
        return {"status": "fail", "message": "rank-restricted view should cap inspection to meso"}
    if not bool(first.get("inspection_redaction", False)):
        return {"status": "fail", "message": "rank-restricted view should enable inspection redaction"}
    return {"status": "pass", "message": "view-bound epistemic redaction check passed"}

