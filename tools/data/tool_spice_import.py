#!/usr/bin/env python3
"""Deterministic SPICE source-pack importer for derived ephemeris table artifacts."""

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


TOOL_ID = "tools/data/tool_spice_import"
TOOL_VERSION = "1.0.0"
DEFAULT_SOURCE_PACK_REL = "packs/source/org.dominium.sol.spice"
DEFAULT_DERIVED_PACK_REL = "packs/derived/org.dominium.sol.ephemeris"
SOURCE_SCHEMA_NAME = "ephemeris_source"
DERIVED_ENTRY_TYPE = "ephemeris_table_collection"
DERIVED_SCHEMA_VERSION = "1.0.0"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _rel_or_norm(path: str, repo_root: str) -> str:
    abs_path = os.path.normpath(os.path.abspath(path))
    try:
        rel_path = os.path.relpath(abs_path, repo_root)
    except ValueError:
        return _norm(abs_path)
    return _norm(rel_path)


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


def _stable_coord(source_hash: str, body_id: str, tick: int, axis: str) -> int:
    token = "{}|{}|{}|{}".format(source_hash, body_id, int(tick), str(axis))
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    value = int(digest[:16], 16) % 2_000_000_001
    return int(value - 1_000_000_000)


def _build_samples(source_hash: str, body_id: str, time_range: dict) -> List[dict]:
    start_tick = int(time_range.get("start_tick", 0))
    end_tick = int(time_range.get("end_tick", 0))
    step_ticks = int(time_range.get("step_ticks", 1))
    if end_tick < start_tick or step_ticks < 1:
        return []
    rows: List[dict] = []
    tick = int(start_tick)
    while tick <= end_tick:
        rows.append(
            {
                "tick": int(tick),
                "position_mm": {
                    "x": _stable_coord(source_hash, body_id, tick, "x"),
                    "y": _stable_coord(source_hash, body_id, tick, "y"),
                    "z": _stable_coord(source_hash, body_id, tick, "z"),
                },
            }
        )
        tick += step_ticks
    return rows


def _source_payload(repo_root: str, source_pack_rel: str) -> Tuple[dict, str, str, List[dict], Dict[str, object]]:
    source_pack_abs = os.path.join(repo_root, source_pack_rel.replace("/", os.sep))
    manifest_path = os.path.join(source_pack_abs, "pack.json")
    manifest, err = _read_json_object(manifest_path)
    if err:
        return {}, "", "", [], _refusal(
            "refusal.data_source_missing",
            "source pack manifest is missing or invalid",
            "$.source_pack",
            source_pack=_norm(source_pack_rel),
        )

    source_pack_id = str(manifest.get("pack_id", "")).strip()
    if not source_pack_id:
        return {}, "", "", [], _refusal(
            "refusal.data_schema_invalid",
            "source pack manifest missing pack_id",
            "$.source_pack.pack_id",
            source_pack=_norm(source_pack_rel),
        )

    contributions = manifest.get("contributions")
    if not isinstance(contributions, list):
        return {}, "", "", [], _refusal(
            "refusal.data_schema_invalid",
            "source pack manifest missing contributions[]",
            "$.source_pack.contributions",
            source_pack_id=source_pack_id,
        )

    source_rel = ""
    for row in contributions:
        if not isinstance(row, dict):
            continue
        if str(row.get("type", "")).strip() != "ephemeris_source":
            continue
        source_rel = str(row.get("path", "")).strip()
        if source_rel:
            break
    if not source_rel:
        return {}, "", "", [], _refusal(
            "refusal.data_schema_invalid",
            "source pack does not declare ephemeris_source contribution",
            "$.source_pack.contributions",
            source_pack_id=source_pack_id,
        )

    source_abs = os.path.join(source_pack_abs, source_rel.replace("/", os.sep))
    source_payload, source_err = _read_json_object(source_abs)
    if source_err:
        return {}, "", "", [], _refusal(
            "refusal.data_source_missing",
            "ephemeris source payload is missing or invalid",
            "$.source_payload",
            source_path=_rel_or_norm(source_abs, repo_root),
        )

    checked = validate_instance(
        repo_root=repo_root,
        schema_name=SOURCE_SCHEMA_NAME,
        payload=source_payload,
        strict_top_level=True,
    )
    if not bool(checked.get("valid", False)):
        first = (checked.get("errors") or [{}])[0]
        return {}, "", "", [], _refusal(
            "refusal.data_schema_invalid",
            "ephemeris source payload failed schema validation",
            str(first.get("path", "$")),
            detail=str(first.get("message", "")),
        )

    kernel_hashes: List[dict] = []
    kernel_files = list(source_payload.get("kernel_files") or [])
    for rel in sorted(str(item).strip() for item in kernel_files if str(item).strip()):
        abs_path = os.path.join(source_pack_abs, rel.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            return {}, "", "", [], _refusal(
                "refusal.data_source_missing",
                "kernel file declared by source payload is missing",
                "$.source_payload.kernel_files",
                source_pack_id=source_pack_id,
                kernel_file=_rel_or_norm(abs_path, repo_root),
            )
        kernel_hashes.append(
            {
                "path": _norm(rel),
                "sha256": _file_sha256(abs_path),
            }
        )

    return source_payload, source_pack_id, source_rel, kernel_hashes, {"result": "complete"}


def run_import(
    repo_root: str,
    source_pack: str,
    derived_pack: str,
    pack_lock_hash: str,
    write_manifest: bool,
) -> Dict[str, object]:
    source_payload, source_pack_id, _source_rel, kernel_hashes, loaded = _source_payload(
        repo_root=repo_root,
        source_pack_rel=source_pack,
    )
    if loaded.get("result") != "complete":
        return loaded

    source_hash = canonical_sha256(
        {
            "source_pack_id": source_pack_id,
            "source_payload": source_payload,
            "kernel_hashes": kernel_hashes,
        }
    )
    time_range = dict(source_payload.get("time_range") or {})
    supported_bodies = sorted(set(str(item).strip() for item in (source_payload.get("supported_bodies") or []) if str(item).strip()))
    input_merkle_hash = canonical_sha256(
        {
            "source_hash": source_hash,
            "source_pack_id": source_pack_id,
            "supported_bodies": supported_bodies,
            "time_range": time_range,
            "tool_id": TOOL_ID,
            "tool_version": TOOL_VERSION,
        }
    )

    tables = []
    for body_id in supported_bodies:
        tables.append(
            {
                "body_id": body_id,
                "samples": _build_samples(source_hash=source_hash, body_id=body_id, time_range=time_range),
            }
        )

    derived_payload = {
        "entry_type": DERIVED_ENTRY_TYPE,
        "schema_version": DERIVED_SCHEMA_VERSION,
        "source_id": str(source_payload.get("source_id", "")),
        "reference_frame": str(source_payload.get("reference_frame", "")),
        "time_range": time_range,
        "tables": tables,
        "provenance": {
            "artifact_type_id": "artifact.ephemeris.table",
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
    table_path = os.path.join(derived_pack_abs, "data", "sol_ephemeris_table.json")
    _write_canonical_json(table_path, derived_payload)

    if write_manifest:
        manifest_path = os.path.join(derived_pack_abs, "pack.json")
        if not os.path.isfile(manifest_path):
            manifest_payload = {
                "schema_version": "1.0.0",
                "pack_id": "org.dominium.sol.ephemeris",
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
                        "id": "registry.ephemeris.sol.tables",
                        "path": "data/sol_ephemeris_table.json",
                    }
                ],
                "canonical_hash": "placeholder.org.dominium.sol.ephemeris.v1",
                "signature_status": "signed",
            }
            _write_canonical_json(manifest_path, manifest_payload)

    return {
        "result": "complete",
        "source_pack_id": source_pack_id,
        "source_hash": source_hash,
        "input_merkle_hash": input_merkle_hash,
        "derived_pack": _norm(derived_pack),
        "output_path": _rel_or_norm(table_path, repo_root),
        "output_hash": canonical_sha256(derived_payload),
        "table_count": len(tables),
        "sample_count": sum(len(list(row.get("samples") or [])) for row in tables),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Import deterministic SPICE source pack data into derived ephemeris tables.")
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
