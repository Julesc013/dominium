"""TestX checks for deterministic SessionSpec creator flow."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.session.create"
TEST_TAGS = ["smoke", "session", "bundle", "lockfile", "schema"]


def _load_fixture(repo_root: str):
    fixture_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    return json.load(open(fixture_path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.validator import validate_instance
    from tools.xstack.sessionx.creator import create_session_spec

    fixture = _load_fixture(repo_root)
    base_save_id = str(fixture.get("save_id", "save.testx.session.fixture"))
    first_save = base_save_id + ".a"
    second_save = base_save_id + ".b"

    first = create_session_spec(
        repo_root=repo_root,
        save_id=first_save,
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
    if first.get("result") != "complete":
        return {"status": "fail", "message": "session creator refused first fixture request"}

    second = create_session_spec(
        repo_root=repo_root,
        save_id=second_save,
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
    if second.get("result") != "complete":
        return {"status": "fail", "message": "session creator refused second fixture request"}

    session_rel = str(first.get("session_spec_path", ""))
    if not session_rel:
        return {"status": "fail", "message": "session creator did not return session_spec_path"}
    session_abs = os.path.join(repo_root, session_rel.replace("/", os.sep))
    if not os.path.isfile(session_abs):
        return {"status": "fail", "message": "session_spec.json file was not written"}
    session_payload = json.load(open(session_abs, "r", encoding="utf-8"))
    validated = validate_instance(repo_root=repo_root, schema_name="session_spec", payload=session_payload, strict_top_level=True)
    if not bool(validated.get("valid", False)):
        return {"status": "fail", "message": "generated session_spec is not schema valid"}

    lockfile_path = os.path.join(repo_root, "build", "lockfile.json")
    if not os.path.isfile(lockfile_path):
        return {"status": "fail", "message": "lockfile was not generated during session create"}
    lockfile_payload = json.load(open(lockfile_path, "r", encoding="utf-8"))
    if str(lockfile_payload.get("bundle_id", "")) != str(fixture.get("bundle_id", "bundle.base.lab")):
        return {"status": "fail", "message": "lockfile bundle_id mismatch"}

    first_identity_path = os.path.join(repo_root, str(first.get("universe_identity_path", "")).replace("/", os.sep))
    second_identity_path = os.path.join(repo_root, str(second.get("universe_identity_path", "")).replace("/", os.sep))
    first_identity = json.load(open(first_identity_path, "r", encoding="utf-8"))
    second_identity = json.load(open(second_identity_path, "r", encoding="utf-8"))
    if str(first_identity.get("identity_hash", "")) != str(second_identity.get("identity_hash", "")):
        return {"status": "fail", "message": "universe identity hash must be deterministic for identical seed input"}

    return {"status": "pass", "message": "session creator deterministic checks passed"}
