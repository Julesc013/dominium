"""STRICT test: selecting constraints from a bundle without constraint pack must refuse."""

from __future__ import annotations

import json
import os
import shutil
import sys


TEST_ID = "testx.worldgen.remove_constraint_pack_runtime_safety"
TEST_TAGS = ["strict", "worldgen", "session"]


def _load_json(path: str) -> dict:
    return json.load(open(path, "r", encoding="utf-8"))


def _write_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _fixture(repo_root: str) -> dict:
    path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "session_create_input.fixture.json")
    return _load_json(path)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec

    bundles_root = os.path.join(repo_root, "bundles")
    bundle_id = "bundle.testx.no_constraints"
    bundle_dir = os.path.join(bundles_root, bundle_id)
    bundle_path = os.path.join(bundle_dir, "bundle.json")
    if os.path.isdir(bundle_dir):
        shutil.rmtree(bundle_dir)
    os.makedirs(bundle_dir, exist_ok=True)

    try:
        base_bundle = _load_json(os.path.join(repo_root, "bundles", "bundle.base.lab", "bundle.json"))
        packs = [str(item).strip() for item in (base_bundle.get("pack_ids") or []) if str(item).strip()]
        packs = [item for item in packs if item != "constraints.worldgen.default_lab"]
        test_bundle = {
            "schema_version": str(base_bundle.get("schema_version", "1.0.0")),
            "bundle_id": bundle_id,
            "description": "Test bundle without worldgen constraints pack.",
            "pack_ids": packs,
        }
        _write_json(bundle_path, test_bundle)

        fixture = _fixture(repo_root)
        result = create_session_spec(
            repo_root=repo_root,
            save_id="save.testx.no.constraints.pack",
            bundle_id=bundle_id,
            scenario_id=str(fixture.get("scenario_id", "scenario.lab.galaxy_nav")),
            mission_id="",
            experience_id=str(fixture.get("experience_id", "profile.lab.developer")),
            law_profile_id=str(fixture.get("law_profile_id", "law.lab.unrestricted")),
            parameter_bundle_id=str(fixture.get("parameter_bundle_id", "params.lab.placeholder")),
            budget_policy_id=str(fixture.get("budget_policy_id", "policy.budget.default_lab")),
            fidelity_policy_id=str(fixture.get("fidelity_policy_id", "policy.fidelity.default_lab")),
            constraints_id="constraints.lab.navigation.default",
            constraints_file="",
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
    finally:
        if os.path.isdir(bundle_dir):
            shutil.rmtree(bundle_dir)

    if result.get("result") != "refused":
        return {"status": "fail", "message": "missing constraints pack must refuse selected constraints_id"}
    reason_code = str((result.get("refusal") or {}).get("reason_code", ""))
    if reason_code != "REFUSE_WORLDGEN_CONSTRAINTS_NOT_REGISTERED":
        return {"status": "fail", "message": "unexpected refusal code for missing constraints pack"}
    return {"status": "pass", "message": "runtime safety refusal for missing constraints pack passed"}
