"""FAST test: deterministic astronomy/site search index ordering for known keys."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.registry.astronomy_search_ordering"
TEST_TAGS = ["smoke", "registry"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _is_sorted(items):
    return list(items) == sorted(str(item) for item in items)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.registry_compile.compiler import compile_bundle

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
        return {"status": "fail", "message": "bundle compile failed before search-order check"}

    astronomy_payload = _load_json(os.path.join(repo_root, "build", "registries", "astronomy.catalog.index.json"))
    site_payload = _load_json(os.path.join(repo_root, "build", "registries", "site.registry.index.json"))
    astronomy_index = astronomy_payload.get("search_index") or {}
    site_index = site_payload.get("search_index") or {}

    sol_ids = astronomy_index.get("sol")
    if sol_ids != ["astro.catalog.sol", "object.sol", "object.sol_system"]:
        return {"status": "fail", "message": "unexpected deterministic search ordering for astronomy key 'sol'"}

    expected_reference_sites = [
        "site.earth.earth_core_center",
        "site.earth.geostationary_reference",
        "site.earth.greenwich",
        "site.earth.low_earth_orbit_reference",
        "site.earth.mantle_reference",
        "site.earth.mt_everest",
        "site.earth.north_pole",
        "site.earth.south_pole",
        "site.earth.stratosphere_reference",
    ]
    if site_index.get("reference") != expected_reference_sites:
        return {"status": "fail", "message": "unexpected deterministic search ordering for site key 'reference'"}

    for key in sorted(astronomy_index.keys()):
        if not _is_sorted(astronomy_index.get(key) or []):
            return {"status": "fail", "message": "astronomy search index ids not sorted for key '{}'".format(key)}
    for key in sorted(site_index.keys()):
        if not _is_sorted(site_index.get(key) or []):
            return {"status": "fail", "message": "site search index ids not sorted for key '{}'".format(key)}

    return {"status": "pass", "message": "astronomy/site search ordering check passed"}
