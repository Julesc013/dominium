"""FAST test: generated SRTM tile pyramid has deterministic structural consistency."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.data.tile_pyramid_consistency"
TEST_TAGS = ["smoke", "registry", "pack"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.data.tool_srtm_import import run_import

    imported = run_import(
        repo_root=repo_root,
        source_pack="packs/source/org.dominium.earth.srtm",
        derived_pack="packs/derived/org.dominium.earth.tiles",
        pack_lock_hash="placeholder.pack_lock_hash",
        write_manifest=True,
    )
    if imported.get("result") != "complete":
        return {"status": "fail", "message": "SRTM import failed before consistency checks"}

    payload = _load_json(os.path.join(repo_root, "packs", "derived", "org.dominium.earth.tiles", "data", "earth_tile_pyramid.json"))
    if str(payload.get("entry_type", "")) != "terrain_tile_pyramid":
        return {"status": "fail", "message": "tile pyramid entry_type mismatch"}

    levels = list(payload.get("levels") or [])
    if len(levels) < 2:
        return {"status": "fail", "message": "tile pyramid must include at least two levels"}
    level0 = dict(levels[0] if isinstance(levels[0], dict) else {})
    level1 = dict(levels[1] if isinstance(levels[1], dict) else {})
    tiles0 = list(level0.get("tiles") or [])
    tiles1 = list(level1.get("tiles") or [])
    if not tiles0 or not tiles1:
        return {"status": "fail", "message": "tile pyramid levels missing tiles"}

    for row in tiles0 + tiles1:
        if not isinstance(row, dict):
            return {"status": "fail", "message": "tile row must be object"}
        tile_id = str(row.get("tile_id", ""))
        if not tile_id.startswith("tile."):
            return {"status": "fail", "message": "tile_id format mismatch: {}".format(tile_id)}
        stats = dict(row.get("stats") or {})
        min_h = int(stats.get("min_height_mm", 0) or 0)
        max_h = int(stats.get("max_height_mm", 0) or 0)
        mean_h = int(stats.get("mean_height_mm", 0) or 0)
        if min_h > max_h:
            return {"status": "fail", "message": "tile stats min_height_mm exceeds max_height_mm"}
        if mean_h < min_h or mean_h > max_h:
            return {"status": "fail", "message": "tile stats mean_height_mm out of min/max range"}

    parent = dict(tiles1[0] if isinstance(tiles1[0], dict) else {})
    children = sorted(str(token).strip() for token in (parent.get("children") or []) if str(token).strip())
    child_ids = sorted(str(row.get("tile_id", "")).strip() for row in tiles0 if isinstance(row, dict))
    if children != child_ids:
        return {"status": "fail", "message": "parent level children list does not match level0 tile ids"}

    return {"status": "pass", "message": "tile pyramid consistency verified"}

