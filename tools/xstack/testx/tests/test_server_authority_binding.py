"""STRICT test: server gate enforces authority binding before running stage."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.server.authority_binding"
TEST_TAGS = ["strict", "session"]


def _load_fixture(repo_root: str):
    fixture_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    return json.load(open(fixture_path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.runner import boot_session_spec
    from tools.xstack.sessionx.server_gate import server_validate_transition

    fixture = _load_fixture(repo_root)
    save_id = str(fixture.get("save_id", "save.testx.session.fixture")) + ".server.authority"
    created = create_session_spec(
        repo_root=repo_root,
        save_id=save_id,
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        pipeline_id=str(fixture.get("pipeline_id", "pipeline.client.default")),
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
        return {"status": "fail", "message": "session create failed before server authority-binding test"}

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    boot = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(created.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
    )
    if boot.get("result") != "complete":
        return {"status": "fail", "message": "boot failed before server authority-binding test"}

    session_payload = json.load(open(spec_abs, "r", encoding="utf-8"))
    expected_authority = dict(session_payload.get("authority_context") or {})

    accepted = server_validate_transition(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        from_stage_id="stage.session_ready",
        to_stage_id="stage.session_running",
        authority_context=dict(expected_authority),
    )
    if accepted.get("result") != "complete":
        return {"status": "fail", "message": "server should accept matching authority binding"}

    mismatched_authority = dict(expected_authority)
    mismatched_authority["entitlements"] = sorted(set(str(item).strip() for item in (expected_authority.get("entitlements") or []) if str(item).strip()))
    mismatched_authority["entitlements"] = [token for token in mismatched_authority["entitlements"] if token != "entitlement.teleport"]
    refused = server_validate_transition(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        from_stage_id="stage.session_ready",
        to_stage_id="stage.session_running",
        authority_context=mismatched_authority,
    )
    if refused.get("result") != "refused":
        return {"status": "fail", "message": "server should refuse mismatched authority binding"}
    reason_code = str((refused.get("refusal") or {}).get("reason_code", ""))
    if reason_code != "refusal.server_authority_violation":
        return {"status": "fail", "message": "expected refusal.server_authority_violation, got '{}'".format(reason_code)}
    return {"status": "pass", "message": "server authority-binding checks passed"}
