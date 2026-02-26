"""STRICT test: changing UniverseIdentity.physics_profile_id after boot is refused."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.reality.physics_profile_immutable"
TEST_TAGS = ["strict", "reality", "session"]


def _load_fixture(repo_root: str):
    fixture_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    return json.load(open(fixture_path, "r", encoding="utf-8"))


def _write_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.common import identity_hash_for_payload
    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.runner import boot_session_spec

    fixture = _load_fixture(repo_root)
    save_id = str(fixture.get("save_id", "save.testx.session.fixture")) + ".physics_immutable"
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
        physics_profile_id="physics.null",
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed before immutability check"}

    registry_abs = os.path.join(repo_root, "build", "registries", "universe_physics_profile.registry.json")
    registry_payload = json.load(open(registry_abs, "r", encoding="utf-8"))
    profile_rows = list(registry_payload.get("physics_profiles") or [])
    alternate_profiles = sorted(
        set(
            str(row.get("physics_profile_id", "")).strip()
            for row in profile_rows
            if isinstance(row, dict) and str(row.get("physics_profile_id", "")).strip() and str(row.get("physics_profile_id", "")).strip() != "physics.null"
        )
    )
    if not alternate_profiles:
        return {"status": "fail", "message": "expected at least one non-null physics profile for immutability test"}
    mutated_profile_id = alternate_profiles[0]

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    first_boot = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
    )
    if first_boot.get("result") != "complete":
        return {"status": "fail", "message": "initial boot failed before physics profile mutation check"}

    identity_abs = os.path.join(repo_root, str(created.get("universe_identity_path", "")).replace("/", os.sep))
    identity_payload = json.load(open(identity_abs, "r", encoding="utf-8"))
    identity_payload["physics_profile_id"] = mutated_profile_id
    identity_payload["identity_hash"] = identity_hash_for_payload(identity_payload)
    _write_json(identity_abs, identity_payload)

    second_boot = boot_session_spec(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        bundle_id=str(fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
    )
    if str(second_boot.get("result", "")) == "complete":
        return {"status": "fail", "message": "boot unexpectedly accepted mutated physics_profile_id"}
    refusal_code = str((second_boot.get("refusal") or {}).get("reason_code", ""))
    if refusal_code != "refusal.physics_profile_mismatch":
        return {"status": "fail", "message": "unexpected refusal code '{}', expected refusal.physics_profile_mismatch".format(refusal_code)}

    return {"status": "pass", "message": "physics_profile_id mutation after first boot is refused deterministically"}
