"""FAST test: fluid profile registry declares required FLUID-0 profile ids."""

from __future__ import annotations

import json
import os


TEST_ID = "test_fluid_profiles_registry_valid"
TEST_TAGS = ["fast", "fluid", "registry"]


_REQUIRED_PROFILE_IDS = {
    "fluid.water",
    "fluid.air_stub",
    "fluid.oil_stub",
    "fluid.steam_stub",
}


def run(repo_root: str):
    rel_path = "data/registries/fluid_profile_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "fluid profile registry missing or invalid"}

    rows = list(((payload.get("record") or {}).get("fluid_profiles") or []))
    if not rows:
        return {"status": "fail", "message": "fluid profile registry has no rows"}

    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        profile_id = str(row.get("fluid_profile_id", "")).strip()
        if not profile_id:
            return {"status": "fail", "message": "fluid profile row missing fluid_profile_id"}
        seen.add(profile_id)
        if "compressible" not in row:
            return {"status": "fail", "message": "profile '{}' missing compressible".format(profile_id)}
        for key in ("density", "viscosity_proxy", "vapor_pressure_proxy"):
            value = row.get(key)
            if value is None:
                return {"status": "fail", "message": "profile '{}' missing {}".format(profile_id, key)}

    missing = sorted(_REQUIRED_PROFILE_IDS - seen)
    if missing:
        return {"status": "fail", "message": "missing required fluid profiles: {}".format(",".join(missing))}
    return {"status": "pass", "message": "fluid profile registry valid"}
