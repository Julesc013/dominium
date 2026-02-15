"""FAST test: packaging remains reproducible with derived real-data packs included."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.packaging.real_data_reproducibility"
TEST_TAGS = ["smoke", "bundle", "registry"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.packagingx import build_dist_layout, validate_dist_layout

    out_a = "build/dist.testx.real_data.a"
    out_b = "build/dist.testx.real_data.b"
    build_a = build_dist_layout(repo_root=repo_root, bundle_id="bundle.base.lab", out_dir=out_a, use_cache=True)
    if build_a.get("result") != "complete":
        return {"status": "fail", "message": "first real-data packaging build failed"}
    build_b = build_dist_layout(repo_root=repo_root, bundle_id="bundle.base.lab", out_dir=out_b, use_cache=True)
    if build_b.get("result") != "complete":
        return {"status": "fail", "message": "second real-data packaging build failed"}

    validate_a = validate_dist_layout(repo_root=repo_root, dist_root=out_a)
    validate_b = validate_dist_layout(repo_root=repo_root, dist_root=out_b)
    if validate_a.get("result") != "complete" or validate_b.get("result") != "complete":
        return {"status": "fail", "message": "real-data packaging validation failed"}

    for key in ("canonical_content_hash", "manifest_hash", "lockfile_hash", "pack_lock_hash"):
        if str(build_a.get(key, "")) != str(build_b.get(key, "")):
            return {"status": "fail", "message": "repeated real-data packaging mismatch for '{}'".format(key)}
    if dict(build_a.get("registry_hashes") or {}) != dict(build_b.get("registry_hashes") or {}):
        return {"status": "fail", "message": "registry hashes differ across repeated real-data builds"}

    manifest = _load_json(os.path.join(repo_root, out_a.replace("/", os.sep), "manifest.json"))
    resolved_rows = list(manifest.get("resolved_packs") or [])
    pack_ids = sorted(set(str(row.get("pack_id", "")).strip() for row in resolved_rows if isinstance(row, dict)))
    required_derived = {"org.dominium.sol.ephemeris", "org.dominium.earth.tiles"}
    missing = sorted(token for token in required_derived if token not in pack_ids)
    if missing:
        return {"status": "fail", "message": "dist manifest missing derived packs: {}".format(", ".join(missing))}

    forbidden_source = {"org.dominium.sol.spice", "org.dominium.earth.srtm"}
    leaked_source = sorted(token for token in forbidden_source if token in pack_ids)
    if leaked_source:
        return {"status": "fail", "message": "dist manifest unexpectedly includes source packs: {}".format(", ".join(leaked_source))}

    for row in resolved_rows:
        if not isinstance(row, dict):
            continue
        rel_path = str(row.get("path", "")).strip()
        if rel_path.startswith("packs/source/"):
            return {"status": "fail", "message": "dist resolved pack path leaks source pack content"}

    return {"status": "pass", "message": "real-data packaging reproducibility checks passed"}
