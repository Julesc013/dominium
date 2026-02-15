"""STRICT test: macro/micro transitions preserve conserved mass_stub totals."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.session.region_conservation"
TEST_TAGS = ["strict", "session"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _load_fixture(repo_root: str, rel_path: str):
    return _load_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))


def _mass_total(state: dict) -> int:
    total = 0
    for row in state.get("macro_capsules") or []:
        if not isinstance(row, dict):
            continue
        conserved = row.get("conserved_quantities")
        if not isinstance(conserved, dict):
            continue
        total += int(conserved.get("mass_stub", 0) or 0)
    for row in state.get("micro_regions") or []:
        if not isinstance(row, dict):
            continue
        total += int(row.get("mass_stub", 0) or 0)
    return int(total)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.script_runner import run_intent_script

    session_fixture = _load_fixture(repo_root, "tools/xstack/testdata/session/session_create_input.fixture.json")
    script_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "script.region_traversal.fixture.json")
    save_id = str(session_fixture.get("save_id", "save.testx.session.fixture")) + ".region.conservation"
    created = create_session_spec(
        repo_root=repo_root,
        save_id=save_id,
        bundle_id=str(session_fixture.get("bundle_id", "bundle.base.lab")),
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
        return {"status": "fail", "message": "session create failed before conservation test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    state_abs = os.path.join(repo_root, str(created.get("universe_state_path", "")).replace("/", os.sep))
    first = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=str(session_fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
        workers=1,
        write_state=True,
    )
    if first.get("result") != "complete":
        return {"status": "fail", "message": "region traversal execution failed before conservation check"}
    first_state = _load_json(state_abs)
    first_total = _mass_total(first_state)
    if int(first_total) <= 0:
        return {"status": "fail", "message": "first region traversal did not initialize conserved mass_stub totals"}

    second = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=str(session_fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
        workers=1,
        write_state=True,
    )
    if second.get("result") != "complete":
        return {"status": "fail", "message": "second region traversal execution failed before conservation check"}
    second_state = _load_json(state_abs)
    second_total = _mass_total(second_state)
    if int(first_total) != int(second_total):
        return {
            "status": "fail",
            "message": "conserved mass_stub total changed across repeated traversals ({} -> {})".format(
                int(first_total),
                int(second_total),
            ),
        }
    return {"status": "pass", "message": "region conservation check passed"}
