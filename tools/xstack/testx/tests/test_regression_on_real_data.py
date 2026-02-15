"""STRICT test: real-data hash snapshot lock remains stable for ephemeris and terrain registries."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.regression.real_data_hashes"
TEST_TAGS = ["strict", "regression", "registry", "bundle"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.registry_compile.compiler import compile_bundle

    baseline = _load_json(os.path.join(repo_root, "data", "regression", "observer_baseline.json"))
    compiled = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        use_cache=True,
    )
    if compiled.get("result") != "complete":
        return {"status": "fail", "message": "registry compile failed for real-data regression check"}

    lockfile = _load_json(os.path.join(repo_root, "build", "lockfile.json"))
    registry_hashes = dict(lockfile.get("registries") or {})
    expected = dict(baseline.get("registry_hashes") or {})
    for key in ("ephemeris_registry_hash", "terrain_tile_registry_hash"):
        if str(registry_hashes.get(key, "")) != str(expected.get(key, "")):
            return {"status": "fail", "message": "real-data registry hash mismatch for '{}'".format(key)}
    return {"status": "pass", "message": "real-data registry hash regression lock passed"}
