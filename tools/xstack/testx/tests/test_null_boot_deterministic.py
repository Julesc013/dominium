"""STRICT test: null boot with zero packs remains deterministic."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.reality.null_boot_deterministic"
TEST_TAGS = ["strict", "reality", "session"]


def _load_fixture(repo_root: str):
    fixture_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    return json.load(open(fixture_path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.runner import boot_session_spec

    fixture = _load_fixture(repo_root)
    save_id = str(fixture.get("save_id", "save.testx.session.fixture")) + ".null_boot"
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
        return {"status": "fail", "message": "null bundle session create refused"}
    if str(created.get("physics_profile_id", "")) != "physics.null":
        return {"status": "fail", "message": "null bundle must resolve physics.null profile"}

    state_abs = os.path.join(repo_root, str(created.get("universe_state_path", "")).replace("/", os.sep))
    if not os.path.isfile(state_abs):
        return {"status": "fail", "message": "null boot universe_state.json missing"}
    state_payload = json.load(open(state_abs, "r", encoding="utf-8"))
    if list((state_payload.get("assemblies") or [])):
        return {"status": "fail", "message": "null boot should start with zero assemblies"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    first = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id="bundle.null",
        compile_if_missing=False,
    )
    second = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id="bundle.null",
        compile_if_missing=False,
    )
    if first.get("result") != "complete" or second.get("result") != "complete":
        return {"status": "fail", "message": "null boot session boot failed"}

    fields = (
        "session_spec_hash",
        "pack_lock_hash",
        "deterministic_fields_hash",
        "perceived_model_hash",
        "render_model_hash",
        "physics_profile_id",
    )
    for field in fields:
        if str(first.get(field, "")) != str(second.get(field, "")):
            return {"status": "fail", "message": "null boot deterministic mismatch for '{}'".format(field)}
    if dict(first.get("registry_hashes") or {}) != dict(second.get("registry_hashes") or {}):
        return {"status": "fail", "message": "null boot registry hashes changed across identical boots"}

    run_meta_abs = os.path.join(repo_root, str(first.get("run_meta_path", "")).replace("/", os.sep))
    run_meta = json.load(open(run_meta_abs, "r", encoding="utf-8"))
    if str(run_meta.get("physics_profile_id", "")) != "physics.null":
        return {"status": "fail", "message": "run-meta must persist physics_profile_id for null boot"}

    return {"status": "pass", "message": "null boot deterministic hash anchors are stable"}
