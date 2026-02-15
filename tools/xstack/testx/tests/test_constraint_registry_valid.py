"""STRICT test: worldgen constraints registry and contributions are structurally valid."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.worldgen.constraint_registry_valid"
TEST_TAGS = ["strict", "worldgen", "schema"]


def _load_json(path: str) -> dict:
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.validator import validate_instance

    registry_path = os.path.join(repo_root, "data", "registries", "worldgen_constraints_registry.json")
    try:
        registry_payload = _load_json(registry_path)
    except (OSError, ValueError):
        return {"status": "fail", "message": "invalid worldgen constraints registry JSON"}

    entries = (((registry_payload.get("record") or {}).get("entries")) or [])
    if not isinstance(entries, list) or not entries:
        return {"status": "fail", "message": "worldgen constraints registry entries are missing"}

    pack_lookup = {}
    packs_root = os.path.join(repo_root, "packs")
    for root, dirs, files in os.walk(packs_root):
        dirs[:] = sorted(dirs)
        if "pack.json" not in files:
            continue
        manifest_path = os.path.join(root, "pack.json")
        try:
            manifest = _load_json(manifest_path)
        except (OSError, ValueError):
            continue
        pack_id = str(manifest.get("pack_id", "")).strip()
        for row in manifest.get("contributions") or []:
            if not isinstance(row, dict):
                continue
            if str(row.get("type", "")).strip() != "worldgen_constraints":
                continue
            contrib_id = str(row.get("id", "")).strip()
            contrib_path = str(row.get("path", "")).strip()
            rel_path = os.path.normpath(os.path.join(os.path.dirname(os.path.relpath(manifest_path, repo_root)), contrib_path))
            pack_lookup[contrib_id] = {
                "pack_id": pack_id,
                "path": rel_path.replace("\\", "/"),
            }

    for row in entries:
        if not isinstance(row, dict):
            continue
        constraints_id = str(row.get("constraints_id", "")).strip()
        pack_id = str(row.get("pack_id", "")).strip()
        if constraints_id not in pack_lookup:
            return {"status": "fail", "message": "constraints_id '{}' missing pack contribution".format(constraints_id)}
        mapped = dict(pack_lookup.get(constraints_id) or {})
        if pack_id != str(mapped.get("pack_id", "")):
            return {"status": "fail", "message": "constraints_id '{}' pack_id mismatch".format(constraints_id)}
        payload_path = os.path.join(repo_root, str(mapped.get("path", "")).replace("/", os.sep))
        try:
            payload = _load_json(payload_path)
        except (OSError, ValueError):
            return {"status": "fail", "message": "constraints payload is missing/invalid for '{}'".format(constraints_id)}
        checked = validate_instance(
            repo_root=repo_root,
            schema_name="worldgen_constraints",
            payload=payload,
            strict_top_level=True,
        )
        if not bool(checked.get("valid", False)):
            return {
                "status": "fail",
                "message": "worldgen constraints schema validation failed for '{}'".format(constraints_id),
            }

    return {"status": "pass", "message": "worldgen constraints registry validation passed"}
