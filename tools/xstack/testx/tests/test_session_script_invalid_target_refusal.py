"""STRICT test: invalid teleport object/site ids refuse deterministically."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.session.invalid_target_refusal"
TEST_TAGS = ["strict", "session"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _load_fixture(repo_root: str, rel_path: str):
    return _load_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))


def _write_script(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _run_twice(repo_root: str, run_intent_script, spec_abs: str, bundle_id: str, script_path: str):
    first = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=bundle_id,
        compile_if_missing=False,
        workers=1,
        write_state=False,
    )
    second = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=bundle_id,
        compile_if_missing=False,
        workers=1,
        write_state=False,
    )
    return first, second


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.script_runner import run_intent_script

    session_fixture = _load_fixture(repo_root, "tools/xstack/testdata/session/session_create_input.fixture.json")
    save_id = str(session_fixture.get("save_id", "save.testx.session.fixture")) + ".invalid_target"
    bundle_id = str(session_fixture.get("bundle_id", "bundle.base.lab"))
    created = create_session_spec(
        repo_root=repo_root,
        save_id=save_id,
        bundle_id=bundle_id,
        scenario_id=str(session_fixture.get("scenario_id", "scenario.lab.galaxy_nav")),
        mission_id="",
        experience_id=str(session_fixture.get("experience_id", "profile.lab.developer")),
        law_profile_id=str(session_fixture.get("law_profile_id", "law.lab.unrestricted")),
        parameter_bundle_id=str(session_fixture.get("parameter_bundle_id", "params.lab.placeholder")),
        budget_policy_id=str(session_fixture.get("budget_policy_id", "policy.budget.default_lab")),
        fidelity_policy_id=str(session_fixture.get("fidelity_policy_id", "policy.fidelity.default_lab")),
        rng_seed_string=str(session_fixture.get("rng_seed_string", "seed.testx.session.fixture")),
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string=str(session_fixture.get("universe_seed_string", "seed.testx.universe.fixture")),
        universe_id="",
        entitlements=list(session_fixture.get("entitlements") or []),
        epistemic_scope_id=str(session_fixture.get("epistemic_scope_id", "epistemic.lab.placeholder")),
        visibility_level=str(session_fixture.get("visibility_level", "placeholder")),
        privilege_level=str(session_fixture.get("privilege_level", "operator")),
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed before invalid-target refusal test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    base_dir = os.path.join(repo_root, "saves", save_id)

    invalid_object_script = {
        "schema_version": "1.0.0",
        "script_id": "script.testx.invalid_object.v1",
        "intents": [
            {
                "intent_id": "intent.001",
                "process_id": "process.camera_teleport",
                "inputs": {
                    "target_object_id": "object.invalid.unknown"
                },
            }
        ],
    }
    invalid_object_path = os.path.join(base_dir, "script.invalid_object.fixture.json")
    _write_script(invalid_object_path, invalid_object_script)
    first_object, second_object = _run_twice(
        repo_root=repo_root,
        run_intent_script=run_intent_script,
        spec_abs=spec_abs,
        bundle_id=bundle_id,
        script_path=invalid_object_path,
    )
    if first_object.get("result") != "refused" or second_object.get("result") != "refused":
        return {"status": "fail", "message": "invalid target_object_id script must refuse"}
    if str((first_object.get("refusal") or {}).get("reason_code", "")) != "TARGET_NOT_FOUND":
        return {"status": "fail", "message": "invalid target_object_id must refuse with TARGET_NOT_FOUND"}
    if int(first_object.get("script_step", -1)) != 0:
        return {"status": "fail", "message": "invalid target_object_id must refuse at script step 0"}
    if dict(first_object.get("refusal") or {}) != dict(second_object.get("refusal") or {}):
        return {"status": "fail", "message": "invalid target_object_id refusal payload must be deterministic"}

    invalid_site_script = {
        "schema_version": "1.0.0",
        "script_id": "script.testx.invalid_site.v1",
        "intents": [
            {
                "intent_id": "intent.001",
                "process_id": "process.camera_teleport",
                "inputs": {
                    "target_site_id": "site.invalid.unknown"
                },
            }
        ],
    }
    invalid_site_path = os.path.join(base_dir, "script.invalid_site.fixture.json")
    _write_script(invalid_site_path, invalid_site_script)
    first_site, second_site = _run_twice(
        repo_root=repo_root,
        run_intent_script=run_intent_script,
        spec_abs=spec_abs,
        bundle_id=bundle_id,
        script_path=invalid_site_path,
    )
    if first_site.get("result") != "refused" or second_site.get("result") != "refused":
        return {"status": "fail", "message": "invalid target_site_id script must refuse"}
    if str((first_site.get("refusal") or {}).get("reason_code", "")) != "TARGET_NOT_FOUND":
        return {"status": "fail", "message": "invalid target_site_id must refuse with TARGET_NOT_FOUND"}
    if int(first_site.get("script_step", -1)) != 0:
        return {"status": "fail", "message": "invalid target_site_id must refuse at script step 0"}
    if dict(first_site.get("refusal") or {}) != dict(second_site.get("refusal") or {}):
        return {"status": "fail", "message": "invalid target_site_id refusal payload must be deterministic"}

    return {"status": "pass", "message": "invalid teleport target refusal checks passed"}
