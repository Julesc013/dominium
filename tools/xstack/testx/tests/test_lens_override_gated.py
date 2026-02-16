"""STRICT test: control lens override requires entitlement.control.lens_override."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.control.lens_override_gated"
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

    save_id = "save.testx.control.lens_override_gated"
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
        rng_seed_string="seed.eb1.lens.refuse",
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string="seed.eb1.lens.refuse.universe",
        universe_id="",
        entitlements=[
            "session.boot",
            "entitlement.control.camera",
            "lens.nondiegetic.access",
            "ui.window.lab.nav",
        ],
        epistemic_scope_id="epistemic.lab.placeholder",
        visibility_level="placeholder",
        privilege_level="operator",
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "create_session_spec failed for lens override gating test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    script_abs = os.path.join(repo_root, "saves", save_id, "script.control.lens.refuse.v1.json")
    _write_json(
        script_abs,
        {
            "schema_version": "1.0.0",
            "script_id": "script.testx.control.lens.refuse.v1",
            "intents": [
                {
                    "intent_id": "intent.control.lens.001",
                    "process_id": "process.control_set_view_lens",
                    "inputs": {
                        "controller_id": "object.earth",
                        "camera_id": "camera.main",
                        "lens_id": "lens.nondiegetic.debug",
                    },
                }
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
    if str(first.get("result", "")) != "refused" or str(second.get("result", "")) != "refused":
        return {"status": "fail", "message": "missing lens override entitlement must refuse deterministically"}

    refusal_first = dict(first.get("refusal") or {})
    refusal_second = dict(second.get("refusal") or {})
    if str(refusal_first.get("reason_code", "")) != "refusal.control.entitlement_missing":
        return {"status": "fail", "message": "unexpected refusal code for missing lens override entitlement"}
    if int(first.get("script_step", -1)) != 0:
        return {"status": "fail", "message": "missing lens override entitlement must refuse at script step 0"}
    if refusal_first != refusal_second:
        return {"status": "fail", "message": "lens override entitlement refusal payload must be deterministic"}

    return {"status": "pass", "message": "lens override entitlement gating determinism check passed"}
