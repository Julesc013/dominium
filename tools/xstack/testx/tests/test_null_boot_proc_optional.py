"""FAST test: PROC constitution additions remain optional and do not break session boot."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_null_boot_proc_optional"
TEST_TAGS = ["fast", "proc", "null_boot"]


def _load_fixture(repo_root: str):
    fixture_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    return json.load(open(fixture_path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.runner import boot_session_spec

    fixture = _load_fixture(repo_root)
    save_id = str(fixture.get("save_id", "save.testx.session.fixture")) + ".proc_optional"

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
        privilege_level=str(fixture.get("privilege_level", "operator")),
        physics_profile_id="",
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed after PROC-0 registry/docs additions"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    booted = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
    )
    if booted.get("result") != "complete":
        return {"status": "fail", "message": "session boot failed with PROC-0 optional baseline"}

    return {"status": "pass", "message": "PROC baseline remains optional for boot path"}
