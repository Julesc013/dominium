"""STRICT meta-test: full-stack determinism envelope remains stable for identical inputs."""

from __future__ import annotations

import hashlib
import json
import os
import sys


TEST_ID = "test_determinism_envelope_full_stack"
TEST_TAGS = ["strict", "determinism", "session", "bundle", "registry"]


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1 << 16)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _lock_key_rows(result: dict):
    rows = dict(result.get("registry_hashes") or {})
    return {
        "worldgen_constraints_registry_hash": str(rows.get("worldgen_constraints_registry_hash", "")),
        "ephemeris_registry_hash": str(rows.get("ephemeris_registry_hash", "")),
        "terrain_tile_registry_hash": str(rows.get("terrain_tile_registry_hash", "")),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.packagingx import run_lab_build_validation

    save_id = "save.testx.envelope.locked"
    first = run_lab_build_validation(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        dist_a="build/dist.envelope.a1",
        dist_b="build/dist.envelope.a2",
        save_id=save_id,
    )
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "first envelope run failed"}

    second = run_lab_build_validation(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        dist_a="build/dist.envelope.b1",
        dist_b="build/dist.envelope.b2",
        save_id=save_id,
    )
    if str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "second envelope run failed"}

    if str(first.get("composite_hash_anchor", "")) != str(second.get("composite_hash_anchor", "")):
        return {"status": "fail", "message": "composite hash anchor diverged between identical envelope runs"}
    if str(first.get("pack_lock_hash", "")) != str(second.get("pack_lock_hash", "")):
        return {"status": "fail", "message": "pack_lock_hash diverged between identical envelope runs"}
    if dict(first.get("registry_hashes") or {}) != dict(second.get("registry_hashes") or {}):
        return {"status": "fail", "message": "registry hash map diverged between identical envelope runs"}

    first_worldgen_ephemeris_tile = _lock_key_rows(first)
    second_worldgen_ephemeris_tile = _lock_key_rows(second)
    if first_worldgen_ephemeris_tile != second_worldgen_ephemeris_tile:
        return {"status": "fail", "message": "worldgen/ephemeris/tile registry anchors diverged"}

    real_data_files = {
        "ephemeris_table": os.path.join(
            repo_root,
            "packs",
            "derived",
            "org.dominium.sol.ephemeris",
            "data",
            "sol_ephemeris_table.json",
        ),
        "terrain_tile_pyramid": os.path.join(
            repo_root,
            "packs",
            "derived",
            "org.dominium.earth.tiles",
            "data",
            "earth_tile_pyramid.json",
        ),
    }
    real_hashes = {}
    for key in sorted(real_data_files.keys()):
        path = real_data_files[key]
        if not os.path.isfile(path):
            return {"status": "fail", "message": "missing real-data artifact '{}'".format(key)}
        real_hashes[key] = _sha256(path)

    envelope_view = {
        "composite_hash_anchor": str(first.get("composite_hash_anchor", "")),
        "pack_lock_hash": str(first.get("pack_lock_hash", "")),
        "registry_hashes": dict(first.get("registry_hashes") or {}),
        "worldgen_ephemeris_tile_hashes": first_worldgen_ephemeris_tile,
        "real_data_artifact_hashes": real_hashes,
    }
    return {
        "status": "pass",
        "message": "determinism envelope full-stack verification passed",
        "envelope": envelope_view,
    }
