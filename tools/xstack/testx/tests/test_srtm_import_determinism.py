"""FAST test: deterministic SRTM import yields stable tile pyramid hashes."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile


TEST_ID = "testx.data.srtm_import_determinism"
TEST_TAGS = ["smoke", "pack", "registry"]


def _read_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.data.tool_srtm_import import run_import

    temp_root = tempfile.mkdtemp(prefix="dominium_srtm_import_")
    try:
        derived_a = os.path.join(temp_root, "derived_a")
        derived_b = os.path.join(temp_root, "derived_b")
        first = run_import(
            repo_root=repo_root,
            source_pack="packs/source/org.dominium.earth.srtm",
            derived_pack=derived_a,
            pack_lock_hash="hash.lock.test.srtm",
            write_manifest=True,
        )
        second = run_import(
            repo_root=repo_root,
            source_pack="packs/source/org.dominium.earth.srtm",
            derived_pack=derived_b,
            pack_lock_hash="hash.lock.test.srtm",
            write_manifest=True,
        )
        if first.get("result") != "complete" or second.get("result") != "complete":
            return {"status": "fail", "message": "SRTM import failed to complete deterministically"}
        if str(first.get("source_hash", "")) != str(second.get("source_hash", "")):
            return {"status": "fail", "message": "SRTM source hash drift detected"}
        if str(first.get("output_hash", "")) != str(second.get("output_hash", "")):
            return {"status": "fail", "message": "SRTM output hash drift detected"}

        a_json = _read_json(os.path.join(derived_a, "data", "earth_tile_pyramid.json"))
        b_json = _read_json(os.path.join(derived_b, "data", "earth_tile_pyramid.json"))
        if a_json != b_json:
            return {"status": "fail", "message": "SRTM derived payload differs across identical imports"}

        prov = dict(a_json.get("provenance") or {})
        if not bool(prov.get("deterministic", False)):
            return {"status": "fail", "message": "SRTM provenance deterministic flag is missing"}
        return {"status": "pass", "message": "SRTM import determinism verified"}
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

