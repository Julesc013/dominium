"""STRICT test: ROI terrain tile selection remains deterministic for Earth traversal."""

from __future__ import annotations

import json
import os
import sys
import copy


TEST_ID = "testx.session.earth_tile_roi_selection_determinism"
TEST_TAGS = ["strict", "session", "registry"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _load_fixture(repo_root: str, rel_path: str):
    return _load_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))


def _sorted_tile_ids(repo_root: str):
    payload = _load_json(os.path.join(repo_root, "build", "registries", "terrain.tile.registry.json"))
    rows = []
    for item in (payload.get("tiles") or []):
        if not isinstance(item, dict):
            continue
        tile_id = str(item.get("tile_id", "")).strip()
        if not tile_id:
            continue
        rows.append(
            (
                int(item.get("z", 0) or 0),
                int(item.get("x", 0) or 0),
                int(item.get("y", 0) or 0),
                tile_id,
            )
        )
    rows = sorted(rows)
    return [row[3] for row in rows]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.compatx.canonical_json import canonical_sha256

    session_fixture = _load_fixture(repo_root, "tools/xstack/testdata/session/session_create_input.fixture.json")
    script_path = os.path.join(repo_root, "tools", "xstack", "testdata", "session", "script.region_traversal.fixture.json")
    save_id = str(session_fixture.get("save_id", "save.testx.session.fixture")) + ".earth.tile.roi"
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
        return {"status": "fail", "message": "session create failed before ROI terrain determinism test"}

    session_spec_path = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    session_spec = _load_json(session_spec_path)
    universe_state = _load_json(os.path.join(repo_root, str(created.get("universe_state_path", "")).replace("/", os.sep)))
    law_registry = _load_json(os.path.join(repo_root, "build", "registries", "law.registry.json"))
    activation_registry = _load_json(os.path.join(repo_root, "build", "registries", "activation_policy.registry.json"))
    budget_registry = _load_json(os.path.join(repo_root, "build", "registries", "budget_policy.registry.json"))
    fidelity_registry = _load_json(os.path.join(repo_root, "build", "registries", "fidelity_policy.registry.json"))
    script_payload = _load_json(script_path)
    intents = list(script_payload.get("intents") or [])

    law_profile = {}
    for row in (law_registry.get("law_profiles") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("law_profile_id", "")).strip() == str(session_spec.get("authority_context", {}).get("law_profile_id", "")).strip():
            law_profile = dict(row)
            break
    if not law_profile:
        return {"status": "fail", "message": "failed to resolve law profile for ROI terrain test"}

    budget_policy = {}
    for row in (budget_registry.get("budget_policies") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("policy_id", "")).strip() == str(session_spec.get("budget_policy_id", "")).strip():
            budget_policy = dict(row)
            break
    fidelity_policy = {}
    for row in (fidelity_registry.get("fidelity_policies") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("policy_id", "")).strip() == str(session_spec.get("fidelity_policy_id", "")).strip():
            fidelity_policy = dict(row)
            break
    activation_policy = {}
    for row in (activation_registry.get("activation_policies") or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("policy_id", "")).strip() == str(budget_policy.get("activation_policy_id", "")).strip():
            activation_policy = dict(row)
            break
    if not budget_policy or not fidelity_policy or not activation_policy:
        return {"status": "fail", "message": "failed to resolve policy context for ROI terrain test"}

    authority_context = dict(session_spec.get("authority_context") or {})
    navigation_indices = {
        "astronomy_catalog_index": _load_json(os.path.join(repo_root, "build", "registries", "astronomy.catalog.index.json")),
        "site_registry_index": _load_json(os.path.join(repo_root, "build", "registries", "site.registry.index.json")),
        "ephemeris_registry": _load_json(os.path.join(repo_root, "build", "registries", "ephemeris.registry.json")),
        "terrain_tile_registry": _load_json(os.path.join(repo_root, "build", "registries", "terrain.tile.registry.json")),
    }
    policy_context = {
        "activation_policy": activation_policy,
        "budget_policy": budget_policy,
        "fidelity_policy": fidelity_policy,
    }

    def _run_once():
        local_state = copy.deepcopy(universe_state)
        selections = []
        for intent in intents:
            if not isinstance(intent, dict):
                return {"result": "fail", "message": "script contains non-object intent row"}
            executed = execute_intent(
                state=local_state,
                intent=intent,
                law_profile=law_profile,
                authority_context=authority_context,
                navigation_indices=navigation_indices,
                policy_context=policy_context,
            )
            if executed.get("result") != "complete":
                return executed
            if str(intent.get("process_id", "")).strip() == "process.region_management_tick":
                selections.append(list(executed.get("selected_terrain_tiles") or []))
        return {
            "result": "complete",
            "final_state_hash": canonical_sha256(local_state),
            "terrain_selections": selections,
        }

    first = _run_once()
    second = _run_once()
    if first.get("result") != "complete" or second.get("result") != "complete":
        return {"status": "fail", "message": "region traversal execution failed for ROI terrain selection determinism"}
    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "ROI traversal final state hash mismatch across repeated runs"}

    selections_a = list(first.get("terrain_selections") or [])
    selections_b = list(second.get("terrain_selections") or [])
    if not selections_a:
        return {"status": "fail", "message": "no region-management tile selections were emitted"}
    if selections_a != selections_b:
        return {"status": "fail", "message": "terrain tile selections mismatch across repeated runs"}

    ordered_tile_ids = _sorted_tile_ids(repo_root)
    for selection in selections_a:
        expected_prefix = ordered_tile_ids[: len(selection)]
        if list(selection) != expected_prefix:
            return {"status": "fail", "message": "terrain selection does not match deterministic sorted tile prefix"}

    return {"status": "pass", "message": "Earth ROI terrain tile selection determinism passed"}
