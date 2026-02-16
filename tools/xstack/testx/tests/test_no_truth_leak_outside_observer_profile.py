"""STRICT test: non-observer law profile must not leak hidden truth fields into PerceivedModel."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.observation.no_truth_leak_outside_observer_profile"
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
    save_id = str(session_fixture.get("save_id", "save.testx.session.fixture")) + ".no_truth_leak"
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
        return {"status": "fail", "message": "session create failed before truth-leak observation test"}

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

    # Populate hidden-state candidates in local state copy; observe_only law must still redact them.
    for camera in (universe_state.get("camera_assemblies") or []):
        if not isinstance(camera, dict):
            continue
        if str(camera.get("assembly_id", "")).strip() != "camera.main":
            continue
        camera["position_mm"] = {"x": 111, "y": 222, "z": 333}
        camera["orientation_mdeg"] = {"yaw": 1, "pitch": 2, "roll": 3}
    universe_state["time_control"] = {"rate_permille": 2345, "paused": True}

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
    observed = observe_truth(
        truth_model=truth_model,
        lens=lens_profile,
        law_profile=law_profile,
        authority_context=authority_context,
        viewpoint_id="viewpoint.no_truth_leak",
    )
    if observed.get("result") != "complete":
        return {"status": "fail", "message": "observe_truth failed for no-truth-leak test"}

    perceived = dict(observed.get("perceived_model") or {})
    truth_overlay = dict(perceived.get("truth_overlay") or {})
    if truth_overlay:
        return {"status": "fail", "message": "truth_overlay channels leaked under observe_only law"}

    observed_fields = list(perceived.get("observed_fields") or [])
    field_ids = sorted(str(item.get("field_id", "")).strip() for item in observed_fields if isinstance(item, dict))
    if any(token.startswith("time_control.") for token in field_ids):
        return {"status": "fail", "message": "observed_fields leaked time_control.* under observe_only law"}

    performance = dict(perceived.get("performance") or {})
    budget = dict(performance.get("budget") or {})
    if bool(budget.get("visible", True)):
        return {"status": "fail", "message": "performance.budget.visible should be false outside hidden-state observer law"}
    if str(budget.get("summary", "")) != "redacted":
        return {"status": "fail", "message": "performance budget summary should be redacted outside hidden-state observer law"}

    return {"status": "pass", "message": "observe_only law redacted hidden truth fields as expected"}
