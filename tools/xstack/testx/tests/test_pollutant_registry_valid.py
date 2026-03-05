"""FAST test: pollutant registry declares required POLL-0 pollutant ids."""

from __future__ import annotations

import json
import os


TEST_ID = "test_pollutant_registry_valid"
TEST_TAGS = ["fast", "pollution", "registry"]


_REQUIRED_IDS = {
    "pollutant.smoke_particulate",
    "pollutant.co2_stub",
    "pollutant.toxic_gas_stub",
    "pollutant.oil_spill_stub",
}
_ALLOWED_MEDIA = {"air", "water", "soil", "multi"}


def run(repo_root: str):
    rel_path = "data/registries/pollutant_type_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "pollutant type registry missing or invalid"}

    rows = list(((payload.get("record") or {}).get("pollutant_types") or []))
    if not rows:
        return {"status": "fail", "message": "pollutant type registry has no rows"}

    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        pollutant_id = str(row.get("pollutant_id", "")).strip()
        if not pollutant_id:
            return {"status": "fail", "message": "pollutant row missing pollutant_id"}
        seen.add(pollutant_id)
        medium = str(row.get("medium", "")).strip()
        if medium not in _ALLOWED_MEDIA:
            return {"status": "fail", "message": "pollutant '{}' has invalid medium '{}'".format(pollutant_id, medium)}
        if not str(row.get("default_decay_model_id", "")).strip():
            return {"status": "fail", "message": "pollutant '{}' missing default_decay_model_id".format(pollutant_id)}
        if not str(row.get("default_dispersion_policy_id", "")).strip():
            return {"status": "fail", "message": "pollutant '{}' missing default_dispersion_policy_id".format(pollutant_id)}

    missing = sorted(_REQUIRED_IDS - seen)
    if missing:
        return {"status": "fail", "message": "missing required pollutant ids: {}".format(",".join(missing))}
    return {"status": "pass", "message": "pollutant registry valid"}
