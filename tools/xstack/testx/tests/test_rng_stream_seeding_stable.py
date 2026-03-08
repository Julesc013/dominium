"""FAST test: GEO-8 worldgen named RNG stream seeding is stable."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_rng_stream_seeding_stable"
TEST_TAGS = ["fast", "geo", "worldgen", "rng"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.geo import RNG_WORLDGEN_GALAXY, RNG_WORLDGEN_PLANET, RNG_WORLDGEN_SURFACE, RNG_WORLDGEN_SYSTEM, worldgen_rng_stream_policy
    from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_cell_key

    state = seed_worldgen_state()
    identity = dict(state.get("universe_identity") or {})
    cell_key = worldgen_cell_key([11, -7, 4])
    first = worldgen_rng_stream_policy(universe_identity=identity, geo_cell_key=cell_key)
    second = worldgen_rng_stream_policy(universe_identity=identity, geo_cell_key=cell_key)
    if first != second:
        return {"status": "fail", "message": "worldgen named RNG stream policy drifted across repeated runs"}
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "worldgen named RNG stream policy did not complete"}
    streams = list(first.get("streams") or [])
    expected_names = [RNG_WORLDGEN_GALAXY, RNG_WORLDGEN_PLANET, RNG_WORLDGEN_SURFACE, RNG_WORLDGEN_SYSTEM]
    observed_names = sorted(str(dict(row).get("stream_name", "")).strip() for row in streams if isinstance(row, dict))
    if observed_names != sorted(expected_names):
        return {"status": "fail", "message": "worldgen named RNG streams did not match canonical stream set"}
    for row in streams:
        if not isinstance(row, dict):
            continue
        if not _HASH64.fullmatch(str(row.get("stream_seed", "")).strip().lower()):
            return {"status": "fail", "message": "worldgen stream seed was missing or not 64 hex"}
    return {"status": "pass", "message": "GEO-8 named RNG stream seeding stable"}
