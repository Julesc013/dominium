#!/usr/bin/env python3
"""Deterministic MAT-3 blueprint compiler CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.materials.blueprint_engine import (  # noqa: E402
    BlueprintCompileError,
    compile_blueprint_artifacts,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


CACHE_ROOT_REL = os.path.join(".xstack_cache", "blueprint_compile_cache")


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: str, payload: Dict[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent:
        _ensure_dir(parent)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _load_registry_payload(repo_root: str, rel_path: str, *, required: bool) -> tuple[dict, dict]:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    payload = _read_json(abs_path)
    if payload:
        return payload, {}
    if required:
        return {}, {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.blueprint.invalid_graph",
                    "message": "required registry JSON is missing or invalid",
                    "path": _norm(rel_path),
                }
            ],
        }
    return {}, {}


def _load_parameters(args: argparse.Namespace) -> tuple[dict, dict]:
    if str(args.params_file).strip():
        payload = _read_json(os.path.abspath(str(args.params_file)))
        if not payload:
            return {}, {
                "result": "refused",
                "errors": [
                    {
                        "code": "refusal.blueprint.parameter_invalid",
                        "message": "params file is missing or invalid JSON object",
                        "path": "$.params_file",
                    }
                ],
            }
        return payload, {}
    text = str(args.params_json).strip() or "{}"
    try:
        payload = json.loads(text)
    except ValueError:
        payload = {}
    if not isinstance(payload, dict):
        return {}, {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.blueprint.parameter_invalid",
                    "message": "params-json must decode to object JSON",
                    "path": "$.params_json",
                }
            ],
        }
    return dict(payload), {}


def _resolve_pack_lock_hash(repo_root: str, args: argparse.Namespace) -> tuple[str, dict]:
    explicit = str(args.pack_lock_hash).strip()
    if explicit:
        return explicit, {}
    lockfile_rel = str(args.lockfile_path).strip() or os.path.join("build", "lockfile.json")
    lockfile_abs = os.path.join(repo_root, lockfile_rel.replace("/", os.sep))
    lock_payload = _read_json(lockfile_abs)
    token = str(lock_payload.get("pack_lock_hash", "")).strip()
    if token:
        return token, {}
    return "", {
        "result": "refused",
        "errors": [
            {
                "code": "refusal.blueprint.invalid_graph",
                "message": "pack_lock_hash missing (provide --pack-lock-hash or valid lockfile)",
                "path": "$.pack_lock_hash",
            }
        ],
    }


def _cache_paths(repo_root: str, cache_key: str) -> dict:
    root = os.path.join(repo_root, CACHE_ROOT_REL, str(cache_key))
    return {
        "root": root,
        "bom": os.path.join(root, "compiled_bom.json"),
        "ag": os.path.join(root, "compiled_ag.json"),
        "header": os.path.join(root, "compilation_header.json"),
        "manifest": os.path.join(root, "manifest.json"),
    }


def _write_cache(
    *,
    repo_root: str,
    cache_key: str,
    compiled: dict,
) -> None:
    paths = _cache_paths(repo_root, cache_key)
    _ensure_dir(paths["root"])
    bom = dict(compiled.get("compiled_bom_artifact") or {})
    ag = dict(compiled.get("compiled_ag_artifact") or {})
    header = dict(compiled.get("compilation_provenance_header") or {})
    _write_json(paths["bom"], bom)
    _write_json(paths["ag"], ag)
    _write_json(paths["header"], header)
    _write_json(
        paths["manifest"],
        {
            "schema_version": "1.0.0",
            "cache_key": str(cache_key),
            "compiled_bom_hash": canonical_sha256(bom),
            "compiled_ag_hash": canonical_sha256(ag),
            "header_hash": canonical_sha256(header),
        },
    )


def _read_cache(repo_root: str, cache_key: str) -> dict:
    paths = _cache_paths(repo_root, cache_key)
    bom = _read_json(paths["bom"])
    ag = _read_json(paths["ag"])
    header = _read_json(paths["header"])
    if not bom or not ag or not header:
        return {}
    return {
        "compiled_bom_artifact": bom,
        "compiled_ag_artifact": ag,
        "compilation_provenance_header": header,
    }


def run_compile(args: argparse.Namespace) -> Dict[str, object]:
    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root or REPO_ROOT_HINT)))
    blueprint_id = str(args.blueprint_id).strip()
    if not blueprint_id:
        return {
            "result": "refused",
            "errors": [
                {
                    "code": "refusal.blueprint.invalid_graph",
                    "message": "--blueprint-id is required",
                    "path": "$.blueprint_id",
                }
            ],
        }

    parameter_values, parameter_error = _load_parameters(args)
    if parameter_error:
        return parameter_error
    pack_lock_hash, lock_error = _resolve_pack_lock_hash(repo_root, args)
    if lock_error:
        return lock_error

    blueprint_registry, blueprint_registry_error = _load_registry_payload(
        repo_root,
        "data/registries/blueprint_registry.json",
        required=True,
    )
    if blueprint_registry_error:
        return blueprint_registry_error
    part_class_registry, part_class_registry_error = _load_registry_payload(
        repo_root,
        "data/registries/part_class_registry.json",
        required=True,
    )
    if part_class_registry_error:
        return part_class_registry_error
    connection_type_registry, connection_type_registry_error = _load_registry_payload(
        repo_root,
        "data/registries/connection_type_registry.json",
        required=True,
    )
    if connection_type_registry_error:
        return connection_type_registry_error
    material_class_registry, _material_error = _load_registry_payload(
        repo_root,
        "data/registries/material_class_registry.json",
        required=False,
    )

    try:
        compiled = compile_blueprint_artifacts(
            repo_root=repo_root,
            blueprint_id=blueprint_id,
            parameter_values=parameter_values,
            pack_lock_hash=pack_lock_hash,
            blueprint_registry=blueprint_registry,
            part_class_registry=part_class_registry,
            connection_type_registry=connection_type_registry,
            material_class_registry=material_class_registry,
        )
    except BlueprintCompileError as exc:
        return {
            "result": "refused",
            "errors": [
                {
                    "code": str(exc.reason_code),
                    "message": str(exc),
                    "path": "$.blueprint_compile",
                }
            ],
            "details": dict(exc.details),
        }

    cache_key = str(compiled.get("cache_key", ""))
    cache_enabled = str(args.cache).strip().lower() != "off"
    cache_hit = False
    if cache_enabled:
        cached = _read_cache(repo_root, cache_key)
        if cached:
            cache_hit = True
            compiled["compiled_bom_artifact"] = dict(cached.get("compiled_bom_artifact") or {})
            compiled["compiled_ag_artifact"] = dict(cached.get("compiled_ag_artifact") or {})
            compiled["compilation_provenance_header"] = dict(cached.get("compilation_provenance_header") or {})
        else:
            _write_cache(repo_root=repo_root, cache_key=cache_key, compiled=compiled)

    out_dir_rel = str(args.out_dir).strip() or os.path.join("build", "blueprint_compile")
    out_dir_abs = os.path.join(repo_root, out_dir_rel.replace("/", os.sep))
    _ensure_dir(out_dir_abs)
    file_prefix = blueprint_id.replace("/", "_")
    bom_out_abs = os.path.join(out_dir_abs, "{}.compiled_bom.json".format(file_prefix))
    ag_out_abs = os.path.join(out_dir_abs, "{}.compiled_ag.json".format(file_prefix))
    header_out_abs = os.path.join(out_dir_abs, "{}.compilation_header.json".format(file_prefix))
    _write_json(bom_out_abs, dict(compiled.get("compiled_bom_artifact") or {}))
    _write_json(ag_out_abs, dict(compiled.get("compiled_ag_artifact") or {}))
    _write_json(header_out_abs, dict(compiled.get("compilation_provenance_header") or {}))

    return {
        "result": "complete",
        "tool_id": "tool.materials.tool_blueprint_compile",
        "blueprint_id": blueprint_id,
        "cache_key": cache_key,
        "cache_hit": bool(cache_hit),
        "params_hash": str(compiled.get("params_hash", "")),
        "pack_lock_hash": pack_lock_hash,
        "output_files": {
            "compiled_bom": _norm(os.path.relpath(bom_out_abs, repo_root)),
            "compiled_ag": _norm(os.path.relpath(ag_out_abs, repo_root)),
            "compilation_header": _norm(os.path.relpath(header_out_abs, repo_root)),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile deterministic MAT-3 blueprint into canonical BOM/AG artifacts.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--blueprint-id", required=True)
    parser.add_argument("--params-json", default="{}")
    parser.add_argument("--params-file", default="")
    parser.add_argument("--pack-lock-hash", default="")
    parser.add_argument("--lockfile-path", default=os.path.join("build", "lockfile.json"))
    parser.add_argument("--out-dir", default=os.path.join("build", "blueprint_compile"))
    parser.add_argument("--cache", choices=("on", "off"), default="on")
    args = parser.parse_args()

    result = run_compile(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
