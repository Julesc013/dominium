"""STRICT test: mismatched intent target_shard_id refuses deterministically."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.srz.target_shard_invalid_refusal"
TEST_TAGS = ["strict", "session"]


def _load_fixture(repo_root: str, rel_path: str):
    path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return json.load(open(path, "r", encoding="utf-8"))


def _write_script(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.script_runner import run_intent_script

    fixture = _load_fixture(repo_root, "tools/xstack/testdata/session/session_create_input.fixture.json")
    save_id = str(fixture.get("save_id", "save.testx.session.fixture")) + ".srz.invalid_target"
    bundle_id = str(fixture.get("bundle_id", "bundle.base.lab"))
    created = create_session_spec(
        repo_root=repo_root,
        save_id=save_id,
        bundle_id=bundle_id,
        scenario_id=str(fixture.get("scenario_id", "scenario.lab.galaxy_nav")),
        mission_id="",
        experience_id=str(fixture.get("experience_id", "profile.lab.developer")),
        law_profile_id=str(fixture.get("law_profile_id", "law.lab.unrestricted")),
        parameter_bundle_id=str(fixture.get("parameter_bundle_id", "params.lab.placeholder")),
        budget_policy_id=str(fixture.get("budget_policy_id", "policy.budget.default_lab")),
        fidelity_policy_id=str(fixture.get("fidelity_policy_id", "policy.fidelity.default_lab")),
        rng_seed_string=str(fixture.get("rng_seed_string", "seed.testx.session.fixture")),
        rng_roots=[],
        universe_identity_path="",
        universe_seed_string=str(fixture.get("universe_seed_string", "seed.testx.universe.fixture")),
        universe_id="",
        entitlements=list(fixture.get("entitlements") or []),
        epistemic_scope_id=str(fixture.get("epistemic_scope_id", "epistemic.lab.placeholder")),
        visibility_level=str(fixture.get("visibility_level", "placeholder")),
        privilege_level=str(fixture.get("privilege_level", "operator")),
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed before shard-target refusal test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    script_path = os.path.join(repo_root, "saves", save_id, "script.srz.invalid_target.json")
    script_payload = {
        "schema_version": "1.0.0",
        "script_id": "script.testx.srz.invalid_target.v1",
        "intents": [
            {
                "intent_id": "intent.001",
                "process_id": "process.camera_teleport",
                "target_shard_id": "shard.9",
                "inputs": {
                    "target_object_id": "object.earth"
                }
            }
        ]
    }
    _write_script(script_path, script_payload)

    first = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=bundle_id,
        compile_if_missing=False,
        workers=1,
        write_state=False,
        logical_shards=1,
    )
    second = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=bundle_id,
        compile_if_missing=False,
        workers=1,
        write_state=False,
        logical_shards=1,
    )
    if first.get("result") != "refused" or second.get("result") != "refused":
        return {"status": "fail", "message": "invalid target_shard_id must refuse deterministically"}
    reason = str((first.get("refusal") or {}).get("reason_code", ""))
    if reason != "SHARD_TARGET_INVALID":
        return {"status": "fail", "message": "invalid target_shard_id must emit SHARD_TARGET_INVALID"}
    if int(first.get("script_step", -1)) != 0:
        return {"status": "fail", "message": "invalid target_shard_id must refuse at script step 0"}
    if dict(first.get("refusal") or {}) != dict(second.get("refusal") or {}):
        return {"status": "fail", "message": "target_shard refusal payload must be deterministic"}
    return {"status": "pass", "message": "invalid target_shard refusal determinism check passed"}
