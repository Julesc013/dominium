"""FAST test: SRZ single-shard status initializes deterministically for a session save."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.srz.init"
TEST_TAGS = ["smoke", "session"]


def _load_fixture(repo_root: str, rel_path: str):
    path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.srz_status import srz_status

    fixture = _load_fixture(repo_root, "tools/xstack/testdata/session/session_create_input.fixture.json")
    save_id = str(fixture.get("save_id", "save.testx.session.fixture")) + ".srz.init"
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
        return {"status": "fail", "message": "session create failed before SRZ status test"}

    session_path = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    status = srz_status(repo_root=repo_root, session_spec_path=session_path)
    if status.get("result") != "complete":
        return {"status": "fail", "message": "srz_status refused for valid session save"}
    if str(status.get("runtime_mode", "")) != "single_shard":
        return {"status": "fail", "message": "runtime_mode must be single_shard"}
    if int(status.get("shard_count", 0)) != 1:
        return {"status": "fail", "message": "SRZ init must expose exactly one shard in lab runtime"}
    shards = list(status.get("shards") or [])
    if len(shards) != 1:
        return {"status": "fail", "message": "SRZ status shard row count mismatch"}
    shard = dict(shards[0] or {})
    if str(shard.get("shard_id", "")) != "shard.0":
        return {"status": "fail", "message": "single-shard runtime must use shard.0"}
    if int(shard.get("owned_entities_count", 0)) < 1:
        return {"status": "fail", "message": "shard.0 must own at least one entity in initialized lab save"}
    return {"status": "pass", "message": "SRZ single-shard initialization check passed"}
