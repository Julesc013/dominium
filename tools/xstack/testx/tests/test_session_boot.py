"""TestX checks for deterministic session boot/shutdown run-meta output."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.session.boot"
TEST_TAGS = ["smoke", "session", "registry", "lockfile"]


def _load_fixture(repo_root: str):
    fixture_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    return json.load(open(fixture_path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.runner import boot_session_spec

    fixture = _load_fixture(repo_root)
    save_id = str(fixture.get("save_id", "save.testx.session.fixture")) + ".boot"
    created = create_session_spec(
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
        privilege_level=str(fixture.get("privilege_level", "observer")),
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed before boot test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    first_boot = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
    )
    if first_boot.get("result") != "complete":
        return {"status": "fail", "message": "first session boot failed"}
    second_boot = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
    )
    if second_boot.get("result") != "complete":
        return {"status": "fail", "message": "second session boot failed"}

    keys = (
        "session_spec_hash",
        "pack_lock_hash",
        "deterministic_fields_hash",
        "selected_lens_id",
        "perceived_model_hash",
        "render_model_hash",
    )
    for key in keys:
        if str(first_boot.get(key, "")) != str(second_boot.get(key, "")):
            return {"status": "fail", "message": "deterministic boot field mismatch for '{}'".format(key)}
    if dict(first_boot.get("registry_hashes") or {}) != dict(second_boot.get("registry_hashes") or {}):
        return {"status": "fail", "message": "registry hashes differ across repeated boot inputs"}

    run_meta_rel = str(first_boot.get("run_meta_path", ""))
    run_meta_abs = os.path.join(repo_root, run_meta_rel.replace("/", os.sep))
    if not os.path.isfile(run_meta_abs):
        return {"status": "fail", "message": "run-meta artifact missing after boot"}
    run_meta_payload = json.load(open(run_meta_abs, "r", encoding="utf-8"))
    if int(run_meta_payload.get("start_tick", -1)) != 0 or int(run_meta_payload.get("stop_tick", -1)) != 0:
        return {"status": "fail", "message": "boot run-meta must be single-tick bootstrap (0->0)"}

    return {"status": "pass", "message": "session boot deterministic checks passed"}
