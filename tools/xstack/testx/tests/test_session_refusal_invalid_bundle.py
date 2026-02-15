"""TestX refusal check: invalid bundle_id must refuse deterministically."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.session.refusal.invalid_bundle"
TEST_TAGS = ["smoke", "session", "bundle"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec

    fixture_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    fixture = json.load(open(fixture_path, "r", encoding="utf-8"))

    result = create_session_spec(
        repo_root=repo_root,
        save_id="save.testx.invalid.bundle",
        bundle_id="bundle.invalid.missing",
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
        compile_outputs=False,
        saves_root_rel="saves",
    )
    if result.get("result") != "refused":
        return {"status": "fail", "message": "invalid bundle_id must refuse"}
    refusal = result.get("refusal") or {}
    if str(refusal.get("reason_code", "")) != "REFUSE_BUNDLE_INVALID":
        return {"status": "fail", "message": "unexpected refusal reason_code for invalid bundle"}
    if "bundle.invalid.missing" not in str(refusal.get("message", "")):
        return {"status": "fail", "message": "invalid bundle refusal message missing bundle identifier"}
    return {"status": "pass", "message": "invalid bundle refusal check passed"}
