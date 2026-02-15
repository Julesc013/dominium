"""FAST test: real-data registry compile inputs yield deterministic cache hits when unchanged."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.data.cache_hit_real_data"
TEST_TAGS = ["smoke", "registry", "pack"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.registry_compile.compiler import compile_bundle

    first = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=True,
    )
    if first.get("result") != "complete":
        return {"status": "fail", "message": "first compile failed in real-data cache-hit test"}
    second = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=True,
    )
    if second.get("result") != "complete":
        return {"status": "fail", "message": "second compile failed in real-data cache-hit test"}

    if str(first.get("cache_key", "")) != str(second.get("cache_key", "")):
        return {"status": "fail", "message": "cache key mismatch across unchanged real-data compile inputs"}
    if not bool(second.get("cache_hit", False)):
        return {"status": "fail", "message": "second compile expected cache_hit=true for unchanged real-data inputs"}

    lockfile = _load_json(os.path.join(repo_root, "build", "lockfile.json"))
    registries = dict(lockfile.get("registries") or {})
    for key in ("ephemeris_registry_hash", "terrain_tile_registry_hash"):
        if not str(registries.get(key, "")).strip():
            return {"status": "fail", "message": "lockfile missing '{}' after cache-hit compile".format(key)}

    return {"status": "pass", "message": "real-data compile cache-hit checks passed"}
