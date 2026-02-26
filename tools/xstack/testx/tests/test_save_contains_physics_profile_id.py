"""FAST test: save artifacts persist UniverseIdentity.physics_profile_id."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.reality.save_contains_physics_profile_id"
TEST_TAGS = ["fast", "reality", "session"]


def _load_fixture(repo_root: str):
    fixture_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    return json.load(open(fixture_path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.runner import boot_session_spec

    fixture = _load_fixture(repo_root)
    save_id = str(fixture.get("save_id", "save.testx.session.fixture")) + ".physics_save"
    created = create_session_spec(
        repo_root=repo_root,
        save_id=save_id,
        bundle_id="bundle.null",
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
        physics_profile_id="physics.null",
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed for save profile persistence test"}

    identity_abs = os.path.join(repo_root, str(created.get("universe_identity_path", "")).replace("/", os.sep))
    if not os.path.isfile(identity_abs):
        return {"status": "fail", "message": "universe identity save file missing"}
    identity_payload = json.load(open(identity_abs, "r", encoding="utf-8"))
    identity_profile = str(identity_payload.get("physics_profile_id", "")).strip()
    if not identity_profile:
        return {"status": "fail", "message": "saved universe identity missing physics_profile_id"}
    if identity_profile != str(created.get("physics_profile_id", "")).strip():
        return {"status": "fail", "message": "returned profile id does not match saved universe identity"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    booted = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id="bundle.null",
        compile_if_missing=False,
    )
    if booted.get("result") != "complete":
        return {"status": "fail", "message": "boot failed while checking run-meta profile persistence"}

    run_meta_abs = os.path.join(repo_root, str(booted.get("run_meta_path", "")).replace("/", os.sep))
    run_meta_payload = json.load(open(run_meta_abs, "r", encoding="utf-8"))
    if str(run_meta_payload.get("physics_profile_id", "")).strip() != identity_profile:
        return {"status": "fail", "message": "run-meta physics_profile_id mismatch"}

    return {"status": "pass", "message": "physics_profile_id is persisted in save artifacts"}
