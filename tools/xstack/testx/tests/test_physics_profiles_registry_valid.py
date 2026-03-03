"""FAST test: physics profile registry declares required PHYS-0 profiles."""

from __future__ import annotations

import json
import os


TEST_ID = "testx.physics.profiles_registry_valid"
TEST_TAGS = ["fast", "physics", "registry"]


_REQUIRED_PROFILE_IDS = {
    "phys.realistic.default",
    "phys.realistic.rank_strict",
    "phys.fantasy.permissive",
    "phys.lab.exotic",
}

_ALLOWED_INVARIANTS = {"mass", "energy", "momentum", "charge", "custom"}


def run(repo_root: str):
    rel_path = "data/registries/physics_profile_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "physics profile registry missing or invalid"}

    rows = list(((payload.get("record") or {}).get("physics_profiles") or []))
    if not rows:
        return {"status": "fail", "message": "physics profile registry has no rows"}

    ids = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        profile_id = str(row.get("physics_profile_id", "")).strip()
        if not profile_id:
            return {"status": "fail", "message": "physics profile row missing physics_profile_id"}
        ids.add(profile_id)
        for key in ("invariants_enforced", "invariants_track_only"):
            values = list(row.get(key) or [])
            bad = sorted(token for token in values if str(token) not in _ALLOWED_INVARIANTS)
            if bad:
                return {
                    "status": "fail",
                    "message": "profile '{}' contains unsupported {} values: {}".format(
                        profile_id,
                        key,
                        ",".join(bad),
                    ),
                }

    missing = sorted(_REQUIRED_PROFILE_IDS - ids)
    if missing:
        return {"status": "fail", "message": "missing required physics profiles: {}".format(",".join(missing))}
    return {"status": "pass", "message": "physics profile registry valid"}
