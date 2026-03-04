"""FAST test: temporal domain registry exposes required TEMP-0 domains."""

from __future__ import annotations

import json
import os


TEST_ID = "test_temporal_domains_registry_valid"
TEST_TAGS = ["fast", "time", "registry", "temp0"]

_REQUIRED_DOMAIN_IDS = {
    "time.canonical_tick",
    "time.proper",
    "time.civil",
    "time.warp",
    "time.replay",
}

_ALLOWED_SCOPE_KINDS = {
    "global",
    "per_spatial",
    "per_assembly",
    "per_session",
}


def run(repo_root: str):
    rel_path = "data/registries/temporal_domain_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "temporal domain registry missing or invalid"}

    rows = list(((payload.get("record") or {}).get("temporal_domains") or []))
    if not rows:
        return {"status": "fail", "message": "temporal domain registry has no rows"}

    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        domain_id = str(row.get("temporal_domain_id", "")).strip()
        if not domain_id:
            return {"status": "fail", "message": "temporal domain row missing temporal_domain_id"}
        if domain_id in seen:
            return {"status": "fail", "message": "duplicate temporal_domain_id '{}'".format(domain_id)}
        seen.add(domain_id)
        if str(row.get("schema_version", "")).strip() != "1.0.0":
            return {"status": "fail", "message": "domain '{}' missing schema_version=1.0.0".format(domain_id)}
        scope_kind = str(row.get("scope_kind", "")).strip()
        if scope_kind not in _ALLOWED_SCOPE_KINDS:
            return {"status": "fail", "message": "domain '{}' has invalid scope_kind '{}'".format(domain_id, scope_kind)}
        if not str(row.get("description", "")).strip():
            return {"status": "fail", "message": "domain '{}' missing description".format(domain_id)}
        if "extensions" not in row:
            return {"status": "fail", "message": "domain '{}' missing extensions".format(domain_id)}

    missing = sorted(_REQUIRED_DOMAIN_IDS - seen)
    if missing:
        return {"status": "fail", "message": "missing required temporal domains: {}".format(",".join(missing))}
    return {"status": "pass", "message": "temporal domain registry valid"}
