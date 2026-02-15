"""FAST test: SRTM height rounding remains deterministic and integer-stable."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.data.height_value_rounding_stability"
TEST_TAGS = ["smoke", "registry", "pack"]


def _load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _first_level0_mean(payload: dict) -> int:
    levels = list(payload.get("levels") or [])
    if not levels:
        return -1
    level0 = dict(levels[0] if isinstance(levels[0], dict) else {})
    rows = list(level0.get("tiles") or [])
    if not rows:
        return -1
    stats = dict((rows[0] if isinstance(rows[0], dict) else {}).get("stats") or {})
    return int(stats.get("mean_height_mm", -1) or -1)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.data.tool_srtm_import import run_import

    first = run_import(
        repo_root=repo_root,
        source_pack="packs/source/org.dominium.earth.srtm",
        derived_pack="packs/derived/org.dominium.earth.tiles",
        pack_lock_hash="placeholder.pack_lock_hash",
        write_manifest=True,
    )
    second = run_import(
        repo_root=repo_root,
        source_pack="packs/source/org.dominium.earth.srtm",
        derived_pack="packs/derived/org.dominium.earth.tiles",
        pack_lock_hash="placeholder.pack_lock_hash",
        write_manifest=True,
    )
    if first.get("result") != "complete" or second.get("result") != "complete":
        return {"status": "fail", "message": "SRTM import failed for rounding stability test"}
    if str(first.get("output_hash", "")) != str(second.get("output_hash", "")):
        return {"status": "fail", "message": "SRTM output hash drift indicates unstable rounding"}

    payload = _load_json(os.path.join(repo_root, "packs", "derived", "org.dominium.earth.tiles", "data", "earth_tile_pyramid.json"))
    mean_height = _first_level0_mean(payload)
    if mean_height < 0:
        return {"status": "fail", "message": "unable to resolve level0 mean_height_mm"}

    # fixture raw grid mean = round((100+110+120+130+98+108+118+128+95+105+115+125+90+100+110+120)/16)
    # deterministic integer rounding rule is (sum + count//2) // count => 111.
    if int(mean_height) != 111:
        return {"status": "fail", "message": "unexpected deterministic rounded mean_height_mm value: {}".format(mean_height)}

    return {"status": "pass", "message": "height rounding stability verified"}

