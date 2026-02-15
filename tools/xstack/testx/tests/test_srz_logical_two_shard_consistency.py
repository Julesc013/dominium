"""STRICT test: logical two-shard harness remains equivalent to single-shard runtime."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.srz.logical_two_shard_consistency"
TEST_TAGS = ["strict", "session"]


def _load_fixture(repo_root: str, rel_path: str):
    path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return json.load(open(path, "r", encoding="utf-8"))


def _create_session(repo_root: str, suffix: str) -> dict:
    from tools.xstack.sessionx.creator import create_session_spec

    fixture = _load_fixture(repo_root, "tools/xstack/testdata/session/session_create_input.fixture.json")
    save_id = str(fixture.get("save_id", "save.testx.session.fixture")) + suffix
    return create_session_spec(
        repo_root=repo_root,
        save_id=save_id,
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
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


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.script_runner import run_intent_script

    created = _create_session(repo_root, ".srz.logical_two")
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed before logical two-shard test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    script_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "script.camera_nav.fixture.json")
    bundle_id = str(created.get("bundle_id", "bundle.base.lab"))

    single = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=bundle_id,
        compile_if_missing=False,
        workers=1,
        write_state=False,
        logical_shards=1,
    )
    logical_two = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=bundle_id,
        compile_if_missing=False,
        workers=1,
        write_state=False,
        logical_shards=2,
    )
    if single.get("result") != "complete" or logical_two.get("result") != "complete":
        return {"status": "fail", "message": "script replay failed for logical shard consistency check"}
    if str(single.get("final_state_hash", "")) != str(logical_two.get("final_state_hash", "")):
        return {"status": "fail", "message": "final state changed under logical two-shard harness"}
    if str(single.get("composite_hash", "")) != str(logical_two.get("composite_hash", "")):
        return {"status": "fail", "message": "composite hash changed under logical two-shard harness"}
    if list(single.get("tick_hash_anchors") or []) != list(logical_two.get("tick_hash_anchors") or []):
        return {"status": "fail", "message": "per-tick hash anchors changed under logical two-shard harness"}

    srz_payload = dict(logical_two.get("srz") or {})
    if int(srz_payload.get("logical_shard_count_requested", 0) or 0) != 2:
        return {"status": "fail", "message": "SRZ payload must record logical_shard_count_requested=2"}
    if str(srz_payload.get("runtime_mode", "")) != "single_shard":
        return {"status": "fail", "message": "logical harness must preserve single_shard runtime mode"}
    return {"status": "pass", "message": "logical two-shard SRZ consistency check passed"}
