"""FAST test: time mapping registry is deterministic and TEMP-0 compliant."""

from __future__ import annotations

import json
import os


TEST_ID = "test_time_mapping_registry_valid"
TEST_TAGS = ["fast", "time", "registry", "temp0"]

_REQUIRED_MAPPING_IDS = {
    "mapping.proper_default_stub",
    "mapping.civil_calendar_stub",
    "mapping.warp_session_stub",
}

_ALLOWED_SCOPE_SELECTORS = {
    "global",
    "per_spatial",
    "per_assembly",
    "per_session",
}


def _load_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return {}, "invalid json"


def run(repo_root: str):
    domain_payload, domain_error = _load_json(repo_root, "data/registries/temporal_domain_registry.json")
    if domain_error:
        return {"status": "fail", "message": "temporal domain registry missing/invalid"}
    mapping_payload, mapping_error = _load_json(repo_root, "data/registries/time_mapping_registry.json")
    if mapping_error:
        return {"status": "fail", "message": "time mapping registry missing/invalid"}

    declared_domains = {
        str(row.get("temporal_domain_id", "")).strip()
        for row in list(((domain_payload.get("record") or {}).get("temporal_domains") or []))
        if isinstance(row, dict) and str(row.get("temporal_domain_id", "")).strip()
    }
    if "time.canonical_tick" not in declared_domains:
        return {"status": "fail", "message": "time.canonical_tick missing from temporal domain registry"}

    rows = list(((mapping_payload.get("record") or {}).get("time_mappings") or []))
    if not rows:
        return {"status": "fail", "message": "time mapping registry has no rows"}

    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        mapping_id = str(row.get("mapping_id", "")).strip()
        if not mapping_id:
            return {"status": "fail", "message": "mapping row missing mapping_id"}
        if mapping_id in seen:
            return {"status": "fail", "message": "duplicate mapping_id '{}'".format(mapping_id)}
        seen.add(mapping_id)
        if str(row.get("schema_version", "")).strip() != "1.0.0":
            return {"status": "fail", "message": "mapping '{}' missing schema_version=1.0.0".format(mapping_id)}
        if str(row.get("from_domain_id", "")).strip() != "time.canonical_tick":
            return {
                "status": "fail",
                "message": "mapping '{}' must use from_domain_id=time.canonical_tick".format(mapping_id),
            }
        to_domain_id = str(row.get("to_domain_id", "")).strip()
        if not to_domain_id:
            return {"status": "fail", "message": "mapping '{}' missing to_domain_id".format(mapping_id)}
        if to_domain_id not in declared_domains:
            return {"status": "fail", "message": "mapping '{}' targets unknown domain '{}'".format(mapping_id, to_domain_id)}
        if not str(row.get("model_id", "")).strip():
            return {"status": "fail", "message": "mapping '{}' missing model_id".format(mapping_id)}
        scope_selector = str(row.get("scope_selector", "")).strip()
        if scope_selector not in _ALLOWED_SCOPE_SELECTORS:
            return {"status": "fail", "message": "mapping '{}' invalid scope_selector '{}'".format(mapping_id, scope_selector)}
        if not isinstance(row.get("parameters"), dict):
            return {"status": "fail", "message": "mapping '{}' must declare object parameters".format(mapping_id)}
        if "extensions" not in row:
            return {"status": "fail", "message": "mapping '{}' missing extensions".format(mapping_id)}

    missing = sorted(_REQUIRED_MAPPING_IDS - seen)
    if missing:
        return {"status": "fail", "message": "missing required mappings: {}".format(",".join(missing))}
    return {"status": "pass", "message": "time mapping registry valid"}
