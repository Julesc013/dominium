"""STRICT test: player diegetic default workspace exposes no non-diegetic windows."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.diegetic.player_default_no_nondiegetic_windows"
TEST_TAGS = ["strict", "ui", "session", "diegetic"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.registry_compile.compiler import compile_bundle
    from tools.xstack.sessionx.ui_host import available_windows

    compiled = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=False,
    )
    if str(compiled.get("result", "")) != "complete":
        return {"status": "fail", "message": "compile_bundle failed before player workspace gating test"}

    ui_registry = _load_json(os.path.join(repo_root, "build", "registries", "ui.registry.json"))
    law_profile = _load_json(
        os.path.join(
            repo_root,
            "packs",
            "law",
            "law.player.diegetic_default",
            "data",
            "law_profile.player.diegetic_default.json",
        )
    )
    authority_context = {
        "authority_origin": "client",
        "experience_id": "profile.player.default",
        "law_profile_id": "law.player.diegetic_default",
        "entitlements": [
            "session.boot",
            "ui.window.lab.nav",
            "entitlement.agent.move",
            "entitlement.agent.rotate",
            "entitlement.control.camera",
            "entitlement.control.possess",
            "entitlement.diegetic.notebook_write",
            "entitlement.diegetic.radio_use",
        ],
        "epistemic_scope": {"scope_id": "scope.player", "visibility_level": "diegetic"},
        "privilege_level": "observer",
    }
    perceived = {
        "lens_id": "lens.diegetic.sensor",
        "navigation": {"search_results": []},
        "sites": {},
    }

    listed = available_windows(
        ui_registry=ui_registry,
        law_profile=law_profile,
        authority_context=authority_context,
        perceived_model=perceived,
    )
    if str(listed.get("result", "")) != "complete":
        return {"status": "fail", "message": "available_windows failed under player diegetic default law"}

    available_ids = sorted(str((row or {}).get("window_id", "")) for row in list(listed.get("available_windows") or []))
    if not available_ids:
        return {"status": "fail", "message": "player diegetic workspace listed zero available windows"}

    expected_ids = [
        "window.player.instrument.clock",
        "window.player.instrument.compass",
        "window.player.instrument.map_local",
        "window.player.instrument.notebook",
        "window.player.instrument.radio_text",
    ]
    for window_id in expected_ids:
        if window_id not in available_ids:
            return {"status": "fail", "message": "missing expected diegetic player window '{}'".format(window_id)}

    forbidden_prefixes = ("window.tool.", "window.observer.", "window.spectator.")
    for window_id in available_ids:
        if any(window_id.startswith(prefix) for prefix in forbidden_prefixes):
            return {"status": "fail", "message": "forbidden non-diegetic window leaked into player workspace: {}".format(window_id)}

    return {"status": "pass", "message": "player diegetic workspace blocks non-diegetic windows deterministically"}
