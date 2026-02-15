#!/usr/bin/env python3
"""Deterministic SRTM source-pack importer for derived terrain tile pyramids."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from typing import Dict, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402
from tools.xstack.compatx.validator import validate_instance  # noqa: E402


TOOL_ID = "tools/data/tool_srtm_import"
TOOL_VERSION = "1.0.0"
DEFAULT_SOURCE_PACK_REL = "packs/source/org.dominium.earth.srtm"
DEFAULT_DERIVED_PACK_REL = "packs/derived/org.dominium.earth.tiles"
SOURCE_SCHEMA_NAME = "dem_source"
DERIVED_ENTRY_TYPE = "terrain_tile_pyramid"
DERIVED_SCHEMA_VERSION = "1.0.0"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json_object(path: str) -> Tuple[dict, str]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return payload, ""


def _file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1 << 16)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _write_canonical_json(path: str, payload: Dict[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(payload))
        handle.write("\n")


def _refusal(code: str, message: str, path: str, **meta) -> Dict[str, object]:
    row = {
        "result": "refused",
        "errors": [
            {
                "code": str(code),
                "message": str(message),
                "path": str(path),
            }
        ],
    }
    if meta:
        row["meta"] = {str(key): value for key, value in sorted(meta.items())}
    return row


def _parse_dem_tile(path: str) -> Tuple[List[List[int]], str]:
    out: List[List[int]] = []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for raw in handle.readlines():
                line = str(raw).strip()
                if not line:
                    continue
                values = [int(token) for token in line.split()]
                if values:
                    out.append(values)
    except (OSError, ValueError):
        return [], "invalid dem tile"
    if not out:
        return [], "empty dem tile"
    width = len(out[0])
    for row in out:
        if len(row) != width:
            return [], "inconsistent row width"
    return out, ""


def _tile_stats(grid: List[List[int]]) -> dict:
    values = [int(value) for row in grid for value in row]
    total = sum(values)
    count = len(values)
    mean = int((total + (count // 2)) // count) if count else 0
    return {
        "sample_count": int(count),
        "min_height_mm": int(min(values) if values else 0),
        "max_height_mm": int(max(values) if values else 0),
        "mean_height_mm": int(mean),
    }


def _source_payload(repo_root: str, source_pack_rel: str) -> Tuple[dict, str, List[dict], List[dict], Dict[str, object]]:
    source_pack_abs = os.path.join(repo_root, source_pack_rel.replace("/", os.sep))
    manifest_path = os.path.join(source_pack_abs, "pack.json")
    manifest, err = _read_json_object(manifest_path)
    if err:
        return {}, "", [], [], _refusal(
            "refusal.data_source_missing",
            "source pack manifest is missing or invalid",
            "$.source_pack",
            source_pack=_norm(source_pack_rel),
        )

    source_pack_id = str(manifest.get("pack_id", "")).strip()
    if not source_pack_id:
        return {}, "", [], [], _refusal(
            "refusal.data_schema_invalid",
            "source pack manifest missing pack_id",
            "$.source_pack.pack_id",
            source_pack=_norm(source_pack_rel),
        )

    contributions = manifest.get("contributions")
    if not isinstance(contributions, list):
        return {}, "", [], [], _refusal(
            "refusal.data_schema_invalid",
            "source pack manifest missing contributions[]",
            "$.source_pack.contributions",
            source_pack_id=source_pack_id,
        )

    source_rel = ""
    for row in contributions:
        if not isinstance(row, dict):
            continue
        if str(row.get("type", "")).strip() != "dem_source":
            continue
        source_rel = str(row.get("path", "")).strip()
        if source_rel:
            break
    if not source_rel:
        return {}, "", [], [], _refusal(
            "refusal.data_schema_invalid",
            "source pack does not declare dem_source contribution",
            "$.source_pack.contributions",
            source_pack_id=source_pack_id,
        )

    source_abs = os.path.join(source_pack_abs, source_rel.replace("/", os.sep))
    source_payload, source_err = _read_json_object(source_abs)
    if source_err:
        return {}, "", [], [], _refusal(
            "refusal.data_source_missing",
            "dem source payload is missing or invalid",
            "$.source_payload",
            source_path=_norm(os.path.relpath(source_abs, repo_root)),
        )

    checked = validate_instance(
        repo_root=repo_root,
        schema_name=SOURCE_SCHEMA_NAME,
        payload=source_payload,
        strict_top_level=True,
    )
    if not bool(checked.get("valid", False)):
        first = (checked.get("errors") or [{}])[0]
        return {}, "", [], [], _refusal(
            "refusal.data_schema_invalid",
            "dem source payload failed schema validation",
            str(first.get("path", "$")),
            detail=str(first.get("message", "")),
        )

    tile_rel_paths = [str(item).strip() for item in (source_payload.get("tiles") or []) if str(item).strip()]
    if not tile_rel_paths:
        raw_root = os.path.join(source_pack_abs, "data", "raw")
        for name in sorted(os.listdir(raw_root)) if os.path.isdir(raw_root) else []:
            if str(name).lower().endswith(".asc"):
                tile_rel_paths.append("data/raw/{}".format(name))
    if not tile_rel_paths:
        return {}, "", [], [], _refusal(
            "refusal.data_source_missing",
            "no DEM tiles were declared or discovered for import",
            "$.source_payload.tiles",
            source_pack_id=source_pack_id,
        )

    hashes: List[dict] = []
    tiles: List[dict] = []
    for idx, rel in enumerate(sorted(set(tile_rel_paths))):
        abs_path = os.path.join(source_pack_abs, rel.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            return {}, "", [], [], _refusal(
                "refusal.data_source_missing",
                "DEM tile declared by source payload is missing",
                "$.source_payload.tiles",
                source_pack_id=source_pack_id,
                tile_path=_norm(os.path.relpath(abs_path, repo_root)),
            )
        grid, parse_err = _parse_dem_tile(abs_path)
        if parse_err:
            return {}, "", [], [], _refusal(
                "refusal.data_import_failed",
                "failed to parse DEM tile data",
                "$.source_payload.tiles",
                source_pack_id=source_pack_id,
                tile_path=_norm(os.path.relpath(abs_path, repo_root)),
            )
        hashes.append({"path": _norm(rel), "sha256": _file_sha256(abs_path)})
        tiles.append(
            {
                "tile_index": int(idx),
                "source_path": _norm(rel),
                "grid": grid,
            }
        )
    return source_payload, source_pack_id, hashes, tiles, {"result": "complete"}


def _level0_tiles(tiles: List[dict]) -> List[dict]:
    out: List[dict] = []
    for idx, row in enumerate(tiles):
        grid = list(row.get("grid") or [])
        stats = _tile_stats(grid)
        out.append(
            {
                "tile_id": "tile.0.{}.0".format(int(idx)),
                "z": 0,
                "x": int(idx),
                "y": 0,
                "source_path": str(row.get("source_path", "")),
                "stats": stats,
            }
        )
    return sorted(out, key=lambda item: str(item.get("tile_id", "")))


def _coarse_levels(level0: List[dict]) -> List[dict]:
    if not level0:
        return []
    min_h = min(int((row.get("stats") or {}).get("min_height_mm", 0)) for row in level0)
    max_h = max(int((row.get("stats") or {}).get("max_height_mm", 0)) for row in level0)
    total_samples = sum(int((row.get("stats") or {}).get("sample_count", 0)) for row in level0)
    total_mean_mass = sum(
        int((row.get("stats") or {}).get("mean_height_mm", 0)) * int((row.get("stats") or {}).get("sample_count", 0))
        for row in level0
    )
    mean_h = int((total_mean_mass + (total_samples // 2)) // max(1, total_samples))
    return [
        {
            "tile_id": "tile.1.0.0",
            "z": 1,
            "x": 0,
            "y": 0,
            "stats": {
                "sample_count": int(total_samples),
                "min_height_mm": int(min_h),
                "max_height_mm": int(max_h),
                "mean_height_mm": int(mean_h),
            },
            "children": [str(row.get("tile_id", "")) for row in level0],
        }
    ]


def run_import(
    repo_root: str,
    source_pack: str,
    derived_pack: str,
    pack_lock_hash: str,
    write_manifest: bool,
) -> Dict[str, object]:
    source_payload, source_pack_id, source_hashes, tiles, loaded = _source_payload(repo_root=repo_root, source_pack_rel=source_pack)
    if loaded.get("result") != "complete":
        return loaded

    source_hash = canonical_sha256(
        {
            "source_pack_id": source_pack_id,
            "source_payload": source_payload,
            "tile_hashes": source_hashes,
        }
    )
    input_merkle_hash = canonical_sha256(
        {
            "source_hash": source_hash,
            "source_pack_id": source_pack_id,
            "tool_id": TOOL_ID,
            "tool_version": TOOL_VERSION,
            "tiles": source_hashes,
        }
    )

    level0 = _level0_tiles(tiles)
    level1 = _coarse_levels(level0)
    levels = [
        {"z": 0, "tiles": level0},
        {"z": 1, "tiles": level1},
    ]
    derived_payload = {
        "entry_type": DERIVED_ENTRY_TYPE,
        "schema_version": DERIVED_SCHEMA_VERSION,
        "source_id": str(source_payload.get("source_id", "")),
        "tile_id_format": "tile.<z>.<x>.<y>",
        "levels": levels,
        "provenance": {
            "artifact_type_id": "artifact.terrain.tile_pyramid",
            "source_pack_id": source_pack_id,
            "source_hash": source_hash,
            "generator_tool_id": TOOL_ID,
            "generator_tool_version": TOOL_VERSION,
            "schema_version": DERIVED_SCHEMA_VERSION,
            "input_merkle_hash": input_merkle_hash,
            "pack_lock_hash": str(pack_lock_hash),
            "deterministic": True,
        },
    }
    provenance_check = validate_instance(
        repo_root=repo_root,
        schema_name="derived_provenance",
        payload=dict(derived_payload.get("provenance") or {}),
        strict_top_level=True,
    )
    if not bool(provenance_check.get("valid", False)):
        first = (provenance_check.get("errors") or [{}])[0]
        return _refusal(
            "refusal.provenance_missing",
            "derived provenance payload failed schema validation",
            str(first.get("path", "$.provenance")),
            detail=str(first.get("message", "")),
        )

    derived_pack_abs = os.path.join(repo_root, derived_pack.replace("/", os.sep))
    pyramid_path = os.path.join(derived_pack_abs, "data", "earth_tile_pyramid.json")
    _write_canonical_json(pyramid_path, derived_payload)

    if write_manifest:
        manifest_path = os.path.join(derived_pack_abs, "pack.json")
        if not os.path.isfile(manifest_path):
            manifest_payload = {
                "schema_version": "1.0.0",
                "pack_id": "org.dominium.earth.tiles",
                "version": "1.0.0",
                "compatibility": {
                    "session_spec_min": "1.0.0",
                    "session_spec_max": "1.0.0",
                },
                "dependencies": [],
                "contribution_types": [
                    "registry_entries",
                ],
                "contributions": [
                    {
                        "type": "registry_entries",
                        "id": "registry.terrain.earth.tiles",
                        "path": "data/earth_tile_pyramid.json",
                    }
                ],
                "canonical_hash": "placeholder.org.dominium.earth.tiles.v1",
                "signature_status": "signed",
            }
            _write_canonical_json(manifest_path, manifest_payload)

    return {
        "result": "complete",
        "source_pack_id": source_pack_id,
        "source_hash": source_hash,
        "input_merkle_hash": input_merkle_hash,
        "derived_pack": _norm(derived_pack),
        "output_path": _norm(os.path.relpath(pyramid_path, repo_root)),
        "output_hash": canonical_sha256(derived_payload),
        "level_count": len(levels),
        "tile_count": sum(len(list(level.get("tiles") or [])) for level in levels),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Import deterministic SRTM source pack data into terrain tile pyramids.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--source-pack", default=DEFAULT_SOURCE_PACK_REL)
    parser.add_argument("--derived-pack", default=DEFAULT_DERIVED_PACK_REL)
    parser.add_argument("--pack-lock-hash", default="placeholder.pack_lock_hash")
    parser.add_argument("--write-manifest", default="on", choices=("on", "off"))
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = run_import(
        repo_root=repo_root,
        source_pack=str(args.source_pack),
        derived_pack=str(args.derived_pack),
        pack_lock_hash=str(args.pack_lock_hash),
        write_manifest=str(args.write_manifest).strip().lower() != "off",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
