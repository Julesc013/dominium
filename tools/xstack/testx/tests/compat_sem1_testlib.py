"""Shared fixtures for COMPAT-SEM-1 TestX coverage."""

from __future__ import annotations

import json
import os


def load_session_fixture(repo_root: str) -> dict:
    fixture_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    return json.load(open(fixture_path, "r", encoding="utf-8"))


def load_script_fixture_path(repo_root: str) -> str:
    return os.path.join(repo_root, "tools", "xstack", "testdata", "session", "script.camera_nav.fixture.json")


def create_session(repo_root: str, suffix: str):
    from tools.xstack.sessionx.creator import create_session_spec

    fixture = load_session_fixture(repo_root)
    save_id = str(fixture.get("save_id", "save.testx.session.fixture")) + ".compat_sem1." + str(suffix)
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
    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    save_dir = os.path.join(repo_root, "saves", save_id)
    return fixture, created, spec_abs, save_dir


def read_json(path: str) -> dict:
    return json.load(open(path, "r", encoding="utf-8"))


def write_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
