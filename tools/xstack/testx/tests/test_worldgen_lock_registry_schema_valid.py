"""FAST test: worldgen lock registry structure and fingerprint are valid."""

from __future__ import annotations

import sys


TEST_ID = "test_worldgen_lock_registry_schema_valid"
TEST_TAGS = ["fast", "worldgen", "lock", "registry"]

EXPECTED_STREAM_ORDER = [
    "rng.worldgen.galaxy",
    "rng.worldgen.galaxy_objects",
    "rng.worldgen.system",
    "rng.worldgen.system.primary_star",
    "rng.worldgen.system.planet_count",
    "rng.worldgen.system.planet.{planet_index}",
    "rng.worldgen.planet",
    "rng.worldgen.surface",
    "rng.worldgen.surface.tile",
    "rng.worldgen.surface.generator",
    "rng.worldgen.surface.elevation",
    "rng.worldgen.surface.earth.elevation",
]
EXPECTED_STAGE_ORDER = [
    "L0.galaxy_coarse_structure",
    "L1.star_distribution",
    "L2.sol_system_derivation",
    "L3.earth_terrain_projection",
]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.worldgen.worldgen_lock_common import load_worldgen_lock_registry, registry_record_hash

    payload = load_worldgen_lock_registry(repo_root)
    record = dict(payload.get("record") or {})
    if str(payload.get("schema_id", "")).strip() != "dominium.schema.governance.worldgen_lock_registry":
        return {"status": "fail", "message": "worldgen lock registry schema_id mismatch"}
    if str(payload.get("schema_version", "")).strip() != "1.0.0":
        return {"status": "fail", "message": "worldgen lock registry schema_version mismatch"}
    if str(record.get("worldgen_lock_id", "")).strip() != "worldgen_lock.v0_0_0":
        return {"status": "fail", "message": "worldgen_lock_id mismatch"}
    try:
        worldgen_lock_version = int(record.get("worldgen_lock_version", -1))
    except (TypeError, ValueError):
        worldgen_lock_version = -1
    if worldgen_lock_version != 0:
        return {"status": "fail", "message": "worldgen_lock_version mismatch"}
    if str(record.get("stability_class", "")).strip() != "stable":
        return {"status": "fail", "message": "stability_class mismatch"}
    streams = [str(item).strip() for item in list(record.get("rng_streams") or []) if str(item).strip()]
    if streams != EXPECTED_STREAM_ORDER:
        return {"status": "fail", "message": "rng_streams order/content mismatch"}
    stages = [str(item).strip() for item in list(record.get("refinement_stages") or []) if str(item).strip()]
    if stages != EXPECTED_STAGE_ORDER:
        return {"status": "fail", "message": "refinement_stages order/content mismatch"}
    fingerprint = str(record.get("deterministic_fingerprint", "")).strip()
    if fingerprint != registry_record_hash(record):
        return {"status": "fail", "message": "registry deterministic_fingerprint mismatch"}
    return {"status": "pass", "message": "worldgen lock registry structure valid"}
