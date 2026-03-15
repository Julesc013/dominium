"""Deterministic helper subprocess for DIST-1 runtime bytecode compilation."""

from __future__ import annotations

import argparse
import json
import os
import py_compile
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json_list(raw: str) -> list[str]:
    try:
        payload = json.loads(str(raw or "").strip() or "[]")
    except ValueError as exc:
        raise SystemExit("invalid JSON list") from exc
    if not isinstance(payload, list):
        raise SystemExit("invalid JSON list")
    return [str(item).strip() for item in payload if str(item).strip()]


def _source_is_excluded(rel_path: str, *, excluded_prefixes: tuple[str, ...], excluded_basenames: set[str]) -> bool:
    token = _norm(rel_path)
    if any(token == prefix or token.startswith(prefix + "/") for prefix in excluded_prefixes):
        return True
    parts = [part for part in token.split("/") if part]
    return any(part in excluded_basenames for part in parts)


def _compile_runtime_tree(
    source_root: str,
    target_root: str,
    *,
    runtime_roots: tuple[str, ...],
    excluded_prefixes: tuple[str, ...],
    excluded_basenames: set[str],
    excluded_files: set[str],
) -> dict:
    compiled: list[str] = []
    invalidation_mode = py_compile.PycInvalidationMode.UNCHECKED_HASH
    for root_rel in runtime_roots:
        abs_root = os.path.join(source_root, root_rel.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for current_root, dirnames, filenames in os.walk(abs_root):
            rel_root = _norm(os.path.relpath(current_root, source_root))
            dirnames[:] = [
                name
                for name in sorted(dirnames)
                if not _source_is_excluded(
                    _norm(os.path.join(rel_root, name)),
                    excluded_prefixes=excluded_prefixes,
                    excluded_basenames=excluded_basenames,
                )
            ]
            for name in sorted(filenames):
                if not name.endswith(".py"):
                    continue
                rel_path = _norm(os.path.join(rel_root, name))
                if rel_path in excluded_files:
                    continue
                if _source_is_excluded(
                    rel_path,
                    excluded_prefixes=excluded_prefixes,
                    excluded_basenames=excluded_basenames,
                ):
                    continue
                src_path = os.path.join(source_root, rel_path.replace("/", os.sep))
                dest_path = os.path.join(target_root, rel_path.replace("/", os.sep) + "c")
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                py_compile.compile(
                    src_path,
                    cfile=dest_path,
                    dfile=rel_path,
                    doraise=True,
                    invalidation_mode=invalidation_mode,
                )
                compiled.append(_norm(os.path.relpath(dest_path, target_root)))
    compiled = sorted(compiled)
    return {
        "compiled_count": len(compiled),
        "compiled_files": compiled,
        "compiled_hash": canonical_sha256({"compiled_files": compiled}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile DIST-1 runtime bytecode deterministically.")
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--target-root", required=True)
    parser.add_argument("--roots-json", required=True)
    parser.add_argument("--excluded-prefixes-json", required=True)
    parser.add_argument("--excluded-basenames-json", required=True)
    parser.add_argument("--excluded-files-json", required=True)
    args = parser.parse_args(argv)

    source_root = os.path.normpath(os.path.abspath(str(args.source_root).strip()))
    target_root = os.path.normpath(os.path.abspath(str(args.target_root).strip()))
    runtime_roots = tuple(_read_json_list(args.roots_json))
    excluded_prefixes = tuple(_read_json_list(args.excluded_prefixes_json))
    excluded_basenames = set(_read_json_list(args.excluded_basenames_json))
    excluded_files = set(_read_json_list(args.excluded_files_json))
    payload = _compile_runtime_tree(
        source_root,
        target_root,
        runtime_roots=runtime_roots,
        excluded_prefixes=excluded_prefixes,
        excluded_basenames=excluded_basenames,
        excluded_files=excluded_files,
    )
    print(canonical_json_text(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
