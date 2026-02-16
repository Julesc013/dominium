"""STRICT test: observer perception hash remains deterministic with real-data registries loaded."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.observer.real_data_path_hash"
TEST_TAGS = ["strict", "session", "registry"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _load_fixture(repo_root: str, rel_path: str):
    return _load_json(os.path.join(repo_root, rel_path.replace("/", os.sep)))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.creator import create_session_spec
    from tools.xstack.sessionx.observation import build_truth_model, observe_truth

    session_fixture = _load_fixture(repo_root, "tools/xstack/testdata/session/session_create_input.fixture.json")
    save_id = str(session_fixture.get("save_id", "save.testx.session.fixture")) + ".observer.real_data"
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
        privilege_level="observer",
        compile_outputs=True,
        saves_root_rel="saves",
    )
    if created.get("result") != "complete":
        return {"status": "fail", "message": "session create failed before observer real-data hash test"}

    save_root = os.path.join(repo_root, "saves", save_id)
    universe_identity = _load_json(os.path.join(save_root, "universe_identity.json"))
    universe_state = _load_json(os.path.join(save_root, "universe_state.json"))
    lockfile = _load_json(os.path.join(repo_root, "build", "lockfile.json"))
    law_profile = _load_json(
        os.path.join(repo_root, "packs", "law", "pack.law.observe_only", "data", "law_profile.observe_only.json")
    )
    lens_profile = _load_json(
        os.path.join(repo_root, "packs", "domain", "pack.domain.navigation", "data", "lens.sensor.json")
    )
    registries = {
        "astronomy_catalog_index": _load_json(os.path.join(repo_root, "build", "registries", "astronomy.catalog.index.json")),
        "site_registry_index": _load_json(os.path.join(repo_root, "build", "registries", "site.registry.index.json")),
        "ephemeris_registry": _load_json(os.path.join(repo_root, "build", "registries", "ephemeris.registry.json")),
        "terrain_tile_registry": _load_json(os.path.join(repo_root, "build", "registries", "terrain.tile.registry.json")),
        "epistemic_policy_registry": _load_json(os.path.join(repo_root, "build", "registries", "epistemic_policy.registry.json")),
        "retention_policy_registry": _load_json(os.path.join(repo_root, "build", "registries", "retention_policy.registry.json")),
    }
    truth_model = build_truth_model(
        universe_identity=universe_identity,
        universe_state=universe_state,
        lockfile_payload=lockfile,
        identity_path="saves/{}/universe_identity.json".format(save_id),
        state_path="saves/{}/universe_state.json".format(save_id),
        registry_payloads=registries,
    )
    authority_context = {
        "authority_origin": "client",
        "experience_id": "profile.lab.developer",
        "law_profile_id": "law.lab.observe_only",
        "entitlements": ["session.boot", "ui.window.lab.nav"],
        "epistemic_scope": {"scope_id": "epistemic.lab.placeholder", "visibility_level": "observer"},
        "privilege_level": "observer",
    }

    first = observe_truth(
        truth_model=truth_model,
        lens=lens_profile,
        law_profile=law_profile,
        authority_context=authority_context,
        viewpoint_id="viewpoint.observer.real_data",
    )
    second = observe_truth(
        truth_model=truth_model,
        lens=lens_profile,
        law_profile=law_profile,
        authority_context=authority_context,
        viewpoint_id="viewpoint.observer.real_data",
    )
    if first.get("result") != "complete" or second.get("result") != "complete":
        return {"status": "fail", "message": "observer real-data observation failed"}
    if str(first.get("perceived_model_hash", "")) != str(second.get("perceived_model_hash", "")):
        return {"status": "fail", "message": "observer real-data perceived hash mismatch across repeated observe()"}

    perceived = dict(first.get("perceived_model") or {})
    navigation = dict(perceived.get("navigation") or {})
    hierarchy = list(navigation.get("hierarchy") or [])
    object_ids = sorted(set(str(item.get("object_id", "")).strip() for item in hierarchy if isinstance(item, dict)))
    if "object.sol" not in object_ids or "object.earth" not in object_ids:
        return {"status": "fail", "message": "observer hierarchy missing object.sol/object.earth entries"}

    ephemeris_tables = list(navigation.get("ephemeris_tables") or [])
    ephemeris_body_ids = sorted(set(str(item.get("body_id", "")).strip() for item in ephemeris_tables if isinstance(item, dict)))
    if "object.sol" not in ephemeris_body_ids or "object.earth" not in ephemeris_body_ids:
        return {"status": "fail", "message": "observer navigation missing Sol/Earth ephemeris table summaries"}

    terrain_tiles = list(navigation.get("terrain_tiles") or [])
    terrain_tile_ids = sorted(set(str(item.get("tile_id", "")).strip() for item in terrain_tiles if isinstance(item, dict)))
    if not terrain_tile_ids or "tile.0.0.0" not in terrain_tile_ids:
        return {"status": "fail", "message": "observer navigation missing deterministic terrain tile rows"}

    return {"status": "pass", "message": "observer real-data path hash and registry visibility checks passed"}
