"""FAST test: region-management selection is deterministic for identical inputs."""

from __future__ import annotations

import copy
import json
import os
import sys


TEST_ID = "testx.session.interest_region_selection_determinism"
TEST_TAGS = ["smoke", "session", "registry"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _select_policy(rows: list, policy_id: str):
    for row in sorted(rows, key=lambda item: str(item.get("policy_id", ""))):
        if str(row.get("policy_id", "")).strip() == str(policy_id).strip():
            return dict(row)
    return {}


def _base_state():
    return {
        "schema_version": "1.0.0",
        "simulation_time": {
            "tick": 0,
            "timestamp_utc": "1970-01-01T00:00:00Z",
        },
        "agent_states": [],
        "world_assemblies": [
            "camera.main",
        ],
        "active_law_references": [
            "law.lab.unrestricted",
        ],
        "session_references": [
            "session.testx.region_selection",
        ],
        "history_anchors": [
            "history.anchor.tick.0",
        ],
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
        "interest_regions": [],
        "macro_capsules": [],
        "micro_regions": [],
        "performance_state": {
            "budget_policy_id": "policy.budget.default_lab",
            "fidelity_policy_id": "policy.fidelity.default_lab",
            "activation_policy_id": "policy.activation.default_lab",
            "compute_units_used": 0,
            "max_compute_units_per_tick": 240,
            "budget_outcome": "ok",
            "active_region_count": 0,
            "fidelity_tier_counts": {
                "coarse": 0,
                "medium": 0,
                "fine": 0,
            },
            "transition_log": [],
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.registry_compile.compiler import compile_bundle
    from tools.xstack.sessionx.process_runtime import execute_intent

    compiled = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=False,
    )
    if compiled.get("result") != "complete":
        return {"status": "fail", "message": "failed to compile bundle before region selection test"}

    astronomy_registry = _load_json(os.path.join(repo_root, "build", "registries", "astronomy.catalog.index.json"))
    activation_registry = _load_json(os.path.join(repo_root, "build", "registries", "activation_policy.registry.json"))
    budget_registry = _load_json(os.path.join(repo_root, "build", "registries", "budget_policy.registry.json"))
    fidelity_registry = _load_json(os.path.join(repo_root, "build", "registries", "fidelity_policy.registry.json"))
    law_registry = _load_json(os.path.join(repo_root, "build", "registries", "law.registry.json"))

    activation_policy = _select_policy(activation_registry.get("activation_policies") or [], "policy.activation.default_lab")
    budget_policy = _select_policy(budget_registry.get("budget_policies") or [], "policy.budget.default_lab")
    fidelity_policy = _select_policy(fidelity_registry.get("fidelity_policies") or [], "policy.fidelity.default_lab")
    if not activation_policy or not budget_policy or not fidelity_policy:
        return {"status": "fail", "message": "compiled policy registries missing required lab policies"}

    law_profile = {}
    for row in sorted(law_registry.get("law_profiles") or [], key=lambda item: str(item.get("law_profile_id", ""))):
        if str(row.get("law_profile_id", "")) == "law.lab.unrestricted":
            law_profile = dict(row)
            break
    if not law_profile:
        return {"status": "fail", "message": "missing law.lab.unrestricted in law registry"}

    authority_context = {
        "authority_origin": "client",
        "experience_id": "profile.lab.developer",
        "law_profile_id": "law.lab.unrestricted",
        "entitlements": ["session.boot"],
        "epistemic_scope": {"scope_id": "epistemic.lab.placeholder", "visibility_level": "placeholder"},
        "privilege_level": "observer",
    }
    intent = {
        "intent_id": "intent.testx.region_selection.001",
        "process_id": "process.region_management_tick",
        "inputs": {},
    }
    policy_context = {
        "activation_policy": activation_policy,
        "budget_policy": budget_policy,
        "fidelity_policy": fidelity_policy,
    }
    nav = {
        "astronomy_catalog_index": astronomy_registry,
    }

    state_a = _base_state()
    state_b = copy.deepcopy(state_a)
    first = execute_intent(
        state=state_a,
        intent=intent,
        law_profile=law_profile,
        authority_context=authority_context,
        navigation_indices=nav,
        policy_context=policy_context,
    )
    second = execute_intent(
        state=state_b,
        intent=intent,
        law_profile=law_profile,
        authority_context=authority_context,
        navigation_indices=nav,
        policy_context=policy_context,
    )
    if first.get("result") != "complete" or second.get("result") != "complete":
        return {"status": "fail", "message": "region-management process refused during determinism test"}
    if str(first.get("state_hash_anchor", "")) != str(second.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "region-management anchor hash mismatch for identical inputs"}
    if canonical_sha256(state_a) != canonical_sha256(state_b):
        return {"status": "fail", "message": "region-management produced divergent state payloads"}
    if not isinstance(state_a.get("interest_regions"), list) or not state_a.get("interest_regions"):
        return {"status": "fail", "message": "region-management did not project any interest_regions rows"}
    return {"status": "pass", "message": "interest region selection determinism check passed"}
