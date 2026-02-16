"""STRICT test: control possession bind/release replay is deterministic."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.control.possession_deterministic"
TEST_TAGS = ["strict", "session", "control"]


def _write_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.script_runner import run_intent_script

    save_id = "save.testx.control.possession_det"
    created = create_session_spec(
        repo_root=repo_root,
        save_id=save_id,
        bundle_id="bundle.base.lab",
        scenario_id="scenario.lab.galaxy_nav",
        mission_id="",
        experience_id="profile.lab.developer",
        law_profile_id="law.lab.unrestricted",
        parameter_bundle_id="params.lab.placeholder",
        budget_policy_id="policy.budget.default_lab",
        fidelity_policy_id="policy.fidelity.default_lab",
        rng_seed_string="seed.eb1.possession.det",
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string="seed.eb1.possession.det.universe",
        universe_id="",
        entitlements=[
            "session.boot",
            "entitlement.control.camera",
            "entitlement.control.possess",
            "ui.window.lab.nav",
        ],
        epistemic_scope_id="epistemic.lab.placeholder",
        visibility_level="placeholder",
        privilege_level="operator",
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "create_session_spec failed for possession determinism test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    script_abs = os.path.join(repo_root, "saves", save_id, "script.control.possession.v1.json")
    _write_json(
        script_abs,
        {
            "schema_version": "1.0.0",
            "script_id": "script.testx.control.possession.v1",
            "intents": [
                {
                    "intent_id": "intent.control.001",
                    "process_id": "process.control_bind_camera",
                    "inputs": {
                        "controller_id": "object.earth",
                        "camera_id": "camera.main",
                    },
                },
                {
                    "intent_id": "intent.control.002",
                    "process_id": "process.control_possess_agent",
                    "inputs": {
                        "controller_id": "object.earth",
                        "agent_id": "object.earth",
                    },
                },
                {
                    "intent_id": "intent.control.003",
                    "process_id": "process.control_release_agent",
                    "inputs": {
                        "controller_id": "object.earth",
                        "agent_id": "object.earth",
                    },
                },
            ],
        },
    )

    first = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_abs,
        bundle_id="bundle.base.lab",
        compile_if_missing=False,
        workers=1,
        write_state=False,
    )
    second = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_abs,
        bundle_id="bundle.base.lab",
        compile_if_missing=False,
        workers=1,
        write_state=False,
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "possession script replay refused unexpectedly"}

    keys = (
        "pack_lock_hash",
        "deterministic_fields_hash",
        "final_state_hash",
        "composite_hash",
        "perceived_model_hash",
    )
    for key in keys:
        if str(first.get(key, "")) != str(second.get(key, "")):
            return {"status": "fail", "message": "possession deterministic replay mismatch for '{}'".format(key)}
    if list(first.get("state_hash_anchors") or []) != list(second.get("state_hash_anchors") or []):
        return {"status": "fail", "message": "possession state hash anchors mismatch across replay"}

    return {"status": "pass", "message": "possession bind/release replay determinism check passed"}
