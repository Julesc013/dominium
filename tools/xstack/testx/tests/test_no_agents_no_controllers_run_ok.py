"""STRICT test: session boot + script execution works with zero agents/controllers."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.control.no_agents_no_controllers_run_ok"
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
    from tools.xstack.sessionx.runner import boot_session_spec
    from tools.xstack.sessionx.script_runner import run_intent_script

    save_id = "save.testx.control.no_agents"
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
        rng_seed_string="seed.eb1.no_agents",
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string="seed.eb1.no_agents.universe",
        universe_id="",
        entitlements=[
            "session.boot",
            "entitlement.inspect",
            "ui.window.lab.nav",
        ],
        epistemic_scope_id="epistemic.lab.placeholder",
        visibility_level="placeholder",
        privilege_level="operator",
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "create_session_spec failed for no-agent test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    state_abs = os.path.join(repo_root, str(created.get("universe_state_path", "")).replace("/", os.sep))
    state_payload = json.load(open(state_abs, "r", encoding="utf-8"))
    state_payload["agent_states"] = []
    state_payload["controller_assemblies"] = []
    state_payload["control_bindings"] = []
    _write_json(state_abs, state_payload)

    booted = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id="bundle.base.lab",
        compile_if_missing=False,
    )
    if str(booted.get("result", "")) != "complete":
        return {"status": "fail", "message": "boot_session_spec refused for no-agent/no-controller state"}
    stage_ids = [str((row or {}).get("to_stage_id", "")) for row in (booted.get("stage_log") or [])]
    if "stage.session_ready" not in stage_ids:
        return {"status": "fail", "message": "no-agent boot must reach stage.session_ready"}

    script_abs = os.path.join(repo_root, "saves", save_id, "script.control.empty.json")
    _write_json(
        script_abs,
        {
            "schema_version": "1.0.0",
            "script_id": "script.testx.control.empty.v1",
            "intents": [],
        },
    )
    replayed = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_abs,
        bundle_id="bundle.base.lab",
        compile_if_missing=False,
        workers=1,
        write_state=False,
    )
    if str(replayed.get("result", "")) != "complete":
        return {"status": "fail", "message": "empty script replay must complete with zero agents/controllers"}

    return {"status": "pass", "message": "zero-agent/zero-controller session path is deterministic and valid"}
