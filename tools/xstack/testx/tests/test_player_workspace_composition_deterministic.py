"""STRICT test: player diegetic workspace composition is deterministic for identical lockfile inputs."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.diegetic.player_workspace_composition_deterministic"
TEST_TAGS = ["strict", "ui", "registry", "diegetic"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _workspace_digest(ui_registry: dict, lockfile_payload: dict, canonical_sha256_fn) -> str:
    windows = [dict(row) for row in list(ui_registry.get("windows") or []) if isinstance(row, dict)]
    player_windows = [
        row
        for row in windows
        if str(row.get("window_id", "")).startswith("window.player.instrument.")
    ]
    reduced = [
        {
            "window_id": str(row.get("window_id", "")),
            "required_entitlements": sorted(str(item) for item in (row.get("required_entitlements") or []) if str(item).strip()),
            "required_lenses": sorted(str(item) for item in (row.get("required_lenses") or []) if str(item).strip()),
            "pack_id": str(row.get("pack_id", "")),
        }
        for row in sorted(player_windows, key=lambda item: str(item.get("window_id", "")))
    ]
    payload = {
        "pack_lock_hash": str(lockfile_payload.get("pack_lock_hash", "")),
        "player_workspace_windows": reduced,
    }
    return str(canonical_sha256_fn(payload))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.registry_compile.compiler import compile_bundle

    first = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=False,
    )
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "first compile_bundle failed for player workspace determinism test"}
    ui_first = _load_json(os.path.join(repo_root, "build", "registries", "ui.registry.json"))
    lock_first = _load_json(os.path.join(repo_root, "build", "lockfile.json"))
    digest_first = _workspace_digest(ui_registry=ui_first, lockfile_payload=lock_first, canonical_sha256_fn=canonical_sha256)

    second = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=False,
    )
    if str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "second compile_bundle failed for player workspace determinism test"}
    ui_second = _load_json(os.path.join(repo_root, "build", "registries", "ui.registry.json"))
    lock_second = _load_json(os.path.join(repo_root, "build", "lockfile.json"))
    digest_second = _workspace_digest(ui_registry=ui_second, lockfile_payload=lock_second, canonical_sha256_fn=canonical_sha256)

    if digest_first != digest_second:
        return {"status": "fail", "message": "player workspace composition hash changed across identical compiles"}

    windows = [dict(row) for row in list(ui_second.get("windows") or []) if isinstance(row, dict)]
    player_ids = sorted(
        str(row.get("window_id", ""))
        for row in windows
        if str(row.get("window_id", "")).startswith("window.player.instrument.")
    )
    if player_ids != sorted(player_ids):
        return {"status": "fail", "message": "player workspace windows are not deterministically ordered"}
    if len(player_ids) < 5:
        return {"status": "fail", "message": "expected player workspace instrument windows are missing"}

    return {"status": "pass", "message": "player workspace composition is deterministic under identical lockfile inputs"}
