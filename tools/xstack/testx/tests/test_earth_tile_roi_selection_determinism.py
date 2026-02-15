"""STRICT test: ROI terrain tile selection remains deterministic for Earth traversal."""

from __future__ import annotations

import json
import os
import sys


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
    from tools.xstack.sessionx.script_runner import run_intent_script

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

    spec_abs = os.path.join(repo_root, str(created.get("session_spec_path", "")).replace("/", os.sep))
    first = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=str(session_fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
        workers=1,
        write_state=False,
    )
    second = run_intent_script(
        repo_root=repo_root,
        session_spec_path=spec_abs,
        script_path=script_path,
        bundle_id=str(session_fixture.get("bundle_id", "bundle.base.lab")),
        compile_if_missing=False,
        workers=1,
        write_state=False,
    )
    if first.get("result") != "complete" or second.get("result") != "complete":
        return {"status": "fail", "message": "region traversal script execution failed"}

    for key in ("final_state_hash", "deterministic_fields_hash", "pack_lock_hash"):
        if str(first.get(key, "")) != str(second.get(key, "")):
            return {"status": "fail", "message": "ROI replay mismatch for '{}'".format(key)}

    perf_a = dict(first.get("performance_state") or {})
    perf_b = dict(second.get("performance_state") or {})
    tiles_a = list(perf_a.get("selected_terrain_tiles") or [])
    tiles_b = list(perf_b.get("selected_terrain_tiles") or [])
    if not tiles_a:
        return {"status": "fail", "message": "no selected_terrain_tiles were emitted in performance_state"}
    if tiles_a != tiles_b:
        return {"status": "fail", "message": "selected_terrain_tiles mismatch across repeated traversal"}

    expected_prefix = _sorted_tile_ids(repo_root)[: len(tiles_a)]
    if tiles_a != expected_prefix:
        return {"status": "fail", "message": "selected_terrain_tiles order mismatch against deterministic tile ordering"}

    return {"status": "pass", "message": "Earth ROI terrain tile selection determinism passed"}
