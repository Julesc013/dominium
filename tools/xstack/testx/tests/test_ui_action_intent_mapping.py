"""STRICT test: headless UI action maps deterministically to expected intent payload."""

from __future__ import annotations

import copy
import json
import os
import sys


TEST_ID = "testx.ui.action.intent_mapping"
TEST_TAGS = ["strict", "ui", "session"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _minimal_universe_state() -> dict:
    return {
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "camera_assemblies": [
            {
                "assembly_id": "camera.main",
                "frame_id": "frame.world",
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
                "lens_id": "lens.diegetic.sensor",
            }
        ],
        "time_control": {"rate_permille": 1000, "paused": False, "accumulator_permille": 0},
        "process_log": [],
        "history_anchors": [],
    }


def _lab_law() -> dict:
    return {
        "law_profile_id": "law.lab.unrestricted",
        "allowed_processes": [
            "process.camera_teleport",
        ],
        "forbidden_processes": [],
        "allowed_lenses": [
            "lens.diegetic.sensor",
            "lens.nondiegetic.debug",
        ],
        "epistemic_limits": {"max_view_radius_km": 1000000000, "allow_hidden_state_access": True},
        "debug_allowances": {"allow_nondiegetic_overlays": True},
        "process_entitlement_requirements": {"process.camera_teleport": "entitlement.teleport"},
        "process_privilege_requirements": {"process.camera_teleport": "operator"},
    }


def _authority() -> dict:
    return {
        "authority_origin": "client",
        "experience_id": "profile.lab.developer",
        "law_profile_id": "law.lab.unrestricted",
        "entitlements": [
            "session.boot",
            "entitlement.teleport",
            "lens.nondiegetic.access",
        ],
        "epistemic_scope": {"scope_id": "epistemic.lab.placeholder", "visibility_level": "placeholder"},
        "privilege_level": "operator",
    }


def _window_by_id(ui_registry: dict, window_id: str) -> dict:
    for row in ui_registry.get("windows") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("window_id", "")) == window_id:
            return row
    return {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.registry_compile.compiler import compile_bundle
    from tools.xstack.sessionx.ui_host import dispatch_window_action, with_search_results

    compiled = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=True,
    )
    if compiled.get("result") != "complete":
        return {"status": "fail", "message": "compile_bundle failed before UI action test"}

    ui_registry = _load_json(os.path.join(repo_root, "build", "registries", "ui.registry.json"))
    goto_window = _window_by_id(ui_registry, "window.tool.goto")
    if not goto_window:
        return {"status": "fail", "message": "window.tool.goto not found in compiled ui.registry"}

    perceived_fixture = _load_json(os.path.join(repo_root, "tools", "xstack", "testdata", "ui", "perceived_model.fixture.json"))
    perceived = with_search_results(perceived_fixture, query="earth")

    navigation_indices = {
        "astronomy_catalog_index": _load_json(os.path.join(repo_root, "build", "registries", "astronomy.catalog.index.json")),
        "site_registry_index": _load_json(os.path.join(repo_root, "build", "registries", "site.registry.index.json")),
    }

    expected_intent = {
        "intent_id": "intent.ui.goto.teleport.0001",
        "process_id": "process.camera_teleport",
        "authority_context_ref": {
            "authority_origin": "client",
            "law_profile_id": "law.lab.unrestricted",
        },
        "inputs": {
            "target_object_id": "object.earth",
        },
    }
    kwargs = {
        "ui_registry": ui_registry,
        "window_id": "window.tool.goto",
        "widget_id": "goto.teleport",
        "perceived_model": perceived,
        "universe_state": _minimal_universe_state(),
        "law_profile": _lab_law(),
        "authority_context": _authority(),
        "navigation_indices": navigation_indices,
        "widget_state": {"goto.query": "earth"},
        "selection": {"object_id": "object.earth", "site_id": ""},
        "sequence": 1,
        "tool_log": [],
    }
    first = dispatch_window_action(**kwargs)
    second = dispatch_window_action(**kwargs)

    if first.get("result") != "complete" or second.get("result") != "complete":
        return {"status": "fail", "message": "goto teleport action must execute successfully under lab authority"}
    if dict(first.get("intent") or {}) != expected_intent:
        return {"status": "fail", "message": "emitted goto intent payload does not match expected deterministic mapping"}
    if dict(second.get("intent") or {}) != expected_intent:
        return {"status": "fail", "message": "second emitted goto intent payload does not match expected mapping"}
    if dict(first.get("intent") or {}) != dict(second.get("intent") or {}):
        return {"status": "fail", "message": "goto intent payload changed across identical dispatches"}

    first_exec = dict(first.get("execution") or {})
    second_exec = dict(second.get("execution") or {})
    if str(first_exec.get("state_hash_anchor", "")) != str(second_exec.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "execution state hash anchor changed across identical dispatches"}

    first_state = dict(first.get("universe_state") or {})
    camera_rows = list(first_state.get("camera_assemblies") or [])
    if not camera_rows:
        return {"status": "fail", "message": "camera assemblies missing after goto teleport action"}
    camera = copy.deepcopy(camera_rows[0])
    if str(camera.get("frame_id", "")).strip() == "":
        return {"status": "fail", "message": "camera frame_id missing after goto teleport action"}

    return {"status": "pass", "message": "headless goto action intent mapping is deterministic"}
