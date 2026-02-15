"""FAST test: astronomy and site registry indices compile deterministically."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.registry.astronomy_site_index_determinism"
TEST_TAGS = ["smoke", "registry", "pack"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.registry_compile.compiler import compile_bundle

    compile1 = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=False,
    )
    compile2 = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=False,
    )
    if compile1.get("result") != "complete" or compile2.get("result") != "complete":
        return {"status": "fail", "message": "bundle compile failed for astronomy/site determinism test"}

    hashes1 = dict(compile1.get("registry_hashes") or {})
    hashes2 = dict(compile2.get("registry_hashes") or {})
    for key in ("astronomy_catalog_index_hash", "site_registry_index_hash"):
        if str(hashes1.get(key, "")) != str(hashes2.get(key, "")):
            return {"status": "fail", "message": "registry hash drift detected for '{}'".format(key)}

    astronomy_path = os.path.join(repo_root, "build", "registries", "astronomy.catalog.index.json")
    site_path = os.path.join(repo_root, "build", "registries", "site.registry.index.json")
    if not os.path.isfile(astronomy_path) or not os.path.isfile(site_path):
        return {"status": "fail", "message": "compiled astronomy/site registry artifacts are missing"}

    astronomy_payload = _load_json(astronomy_path)
    site_payload = _load_json(site_path)
    if str(astronomy_payload.get("registry_hash", "")) != str(hashes2.get("astronomy_catalog_index_hash", "")):
        return {"status": "fail", "message": "astronomy catalog index hash mismatch against lock output"}
    if str(site_payload.get("registry_hash", "")) != str(hashes2.get("site_registry_index_hash", "")):
        return {"status": "fail", "message": "site registry index hash mismatch against lock output"}

    return {"status": "pass", "message": "astronomy/site index determinism check passed"}
