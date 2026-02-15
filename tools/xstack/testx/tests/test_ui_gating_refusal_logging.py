"""STRICT test: UI window gating refuses deterministically and logs refusal details."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.ui.gating.refusal_logging"
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


def _authority_missing_teleport() -> dict:
    return {
        "authority_origin": "client",
        "experience_id": "profile.lab.developer",
        "law_profile_id": "law.lab.unrestricted",
        "entitlements": [
            "session.boot",
            "lens.nondiegetic.access",
        ],
        "epistemic_scope": {"scope_id": "epistemic.lab.placeholder", "visibility_level": "placeholder"},
        "privilege_level": "operator",
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.registry_compile.compiler import compile_bundle
    from tools.xstack.sessionx.ui_host import available_windows, dispatch_window_action, with_search_results

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
        return {"status": "fail", "message": "compile_bundle failed before UI gating test"}

    ui_registry = _load_json(os.path.join(repo_root, "build", "registries", "ui.registry.json"))
    perceived_fixture = _load_json(os.path.join(repo_root, "tools", "xstack", "testdata", "ui", "perceived_model.fixture.json"))
    perceived = with_search_results(perceived_fixture, query="earth")
    law = _lab_law()
    authority = _authority_missing_teleport()

    listed = available_windows(ui_registry=ui_registry, law_profile=law, authority_context=authority, perceived_model=perceived)
    if str(listed.get("result", "")) != "complete":
        return {"status": "fail", "message": "available_windows failed"}
    unavailable = sorted(
        list(listed.get("unavailable_windows") or []),
        key=lambda row: str((row or {}).get("window_id", "")),
    )
    goto_rows = [row for row in unavailable if str((row or {}).get("window_id", "")) == "window.tool.goto"]
    if not goto_rows:
        return {"status": "fail", "message": "window.tool.goto should be unavailable without entitlement.teleport"}
    if str((goto_rows[0] or {}).get("reason_code", "")) != "ENTITLEMENT_MISSING":
        return {"status": "fail", "message": "window.tool.goto unavailable reason must be ENTITLEMENT_MISSING"}

    kwargs = {
        "ui_registry": ui_registry,
        "window_id": "window.tool.goto",
        "widget_id": "goto.teleport",
        "perceived_model": perceived,
        "universe_state": _minimal_universe_state(),
        "law_profile": law,
        "authority_context": authority,
        "navigation_indices": {
            "astronomy_catalog_index": _load_json(os.path.join(repo_root, "build", "registries", "astronomy.catalog.index.json")),
            "site_registry_index": _load_json(os.path.join(repo_root, "build", "registries", "site.registry.index.json")),
        },
        "widget_state": {"goto.query": "earth"},
        "selection": {"object_id": "object.earth", "site_id": ""},
        "sequence": 2,
        "tool_log": [],
    }
    first = dispatch_window_action(**kwargs)
    second = dispatch_window_action(**kwargs)

    if first.get("result") != "refused" or second.get("result") != "refused":
        return {"status": "fail", "message": "goto action must refuse when teleport entitlement is missing"}
    first_refusal = dict(first.get("refusal") or {})
    second_refusal = dict(second.get("refusal") or {})
    if str(first_refusal.get("reason_code", "")) != "ENTITLEMENT_MISSING":
        return {"status": "fail", "message": "goto refusal reason must be ENTITLEMENT_MISSING"}
    if first_refusal != second_refusal:
        return {"status": "fail", "message": "goto refusal payload changed across identical dispatches"}

    tool_log = list(first.get("tool_log") or [])
    if not tool_log:
        return {"status": "fail", "message": "refusal dispatch did not emit tool_log entry"}
    last_entry = dict(tool_log[-1] or {})
    if str(last_entry.get("reason_code", "")) != "ENTITLEMENT_MISSING":
        return {"status": "fail", "message": "tool_log reason_code mismatch for entitlement refusal"}

    return {"status": "pass", "message": "ui gating refusal logging is deterministic"}
