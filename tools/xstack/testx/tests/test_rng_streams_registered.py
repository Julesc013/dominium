"""FAST test: worldgen RNG streams used in source are covered by the lock registry."""

from __future__ import annotations

import json
import os
import re


TEST_ID = "test_rng_streams_registered"
TEST_TAGS = ["fast", "worldgen", "lock", "rng"]

STREAM_RE = re.compile(r"rng\.worldgen\.[a-z0-9_.]+")
STREAM_SOURCE_RELS = (
    os.path.join("geo", "worldgen", "worldgen_engine.py"),
    os.path.join("worldgen", "galaxy", "galaxy_object_stub_generator.py"),
    os.path.join("worldgen", "mw", "mw_system_refiner_l2.py"),
    os.path.join("worldgen", "mw", "mw_surface_refiner_l3.py"),
    os.path.join("worldgen", "earth", "earth_surface_generator.py"),
)
LOCK_REGISTRY_REL = os.path.join("data", "registries", "worldgen_lock_registry.json")


def _read_text(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _source_streams(repo_root: str):
    observed = set()
    for rel_path in STREAM_SOURCE_RELS:
        text = _read_text(os.path.join(repo_root, rel_path))
        if not text:
            continue
        if "rng.worldgen.system.planet." in text:
            observed.add("rng.worldgen.system.planet.{planet_index}")
        for token in STREAM_RE.findall(text):
            cleaned = str(token).rstrip(".")
            if cleaned == "rng.worldgen.system.planet":
                continue
            observed.add(cleaned)
    return sorted(observed)


def run(repo_root: str):
    registry_path = os.path.join(repo_root, LOCK_REGISTRY_REL)
    try:
        registry_payload = json.load(open(registry_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "worldgen lock registry missing or invalid"}

    record = dict(registry_payload.get("record") or {})
    registered = sorted(str(item).strip() for item in list(record.get("rng_streams") or []) if str(item).strip())
    observed = _source_streams(repo_root)
    missing = sorted(set(observed) - set(registered))
    extra = sorted(set(registered) - set(observed))
    if missing or extra:
        parts = []
        if missing:
            parts.append("missing={}".format(",".join(missing[:4])))
        if extra:
            parts.append("extra={}".format(",".join(extra[:4])))
        return {"status": "fail", "message": "worldgen RNG registry mismatch ({})".format("; ".join(parts))}
    return {"status": "pass", "message": "worldgen RNG streams are registered"}
