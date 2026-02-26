#!/usr/bin/env python3
"""Capture deterministic render snapshot artifacts from RenderModel input."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.client.render.snapshot_capture import capture_render_snapshot, load_render_model_from_artifact


def _repo_root(value: str) -> str:
    token = str(value or "").strip()
    if token:
        return os.path.normpath(os.path.abspath(token))
    return REPO_ROOT_HINT


def run_capture(
    *,
    repo_root: str,
    renderer: str,
    input_path: str,
    out_dir: str,
    cache_dir: str,
    width: int,
    height: int,
    wireframe: bool,
) -> dict:
    repo_root = _repo_root(repo_root)
    input_path = os.path.normpath(os.path.abspath(str(input_path)))
    render_model, load_err = load_render_model_from_artifact(input_path)
    if load_err:
        return {
            "result": "refusal",
            "code": "refusal.render.capture_input_invalid",
            "message": str(load_err),
        }

    out_root = str(out_dir or "").strip()
    if not out_root:
        out_root = os.path.join(repo_root, "run_meta", "render_snapshots")
    out_root = os.path.normpath(os.path.abspath(out_root))
    os.makedirs(out_root, exist_ok=True)
    cache_root = str(cache_dir or "").strip()
    if not cache_root:
        cache_root = os.path.join(repo_root, ".xstack_cache", "render_snapshots")
    cache_root = os.path.normpath(os.path.abspath(cache_root))
    os.makedirs(cache_root, exist_ok=True)

    return capture_render_snapshot(
        renderer_id=str(renderer),
        render_model=render_model,
        out_dir=out_root,
        width=int(max(0, int(width))),
        height=int(max(0, int(height))),
        wireframe=bool(wireframe),
        cache_dir=cache_root,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture deterministic render snapshots from RenderModel artifacts.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--renderer", default="null", choices=("null", "software"))
    parser.add_argument("--input", required=True, help="Path to RenderModel JSON artifact.")
    parser.add_argument("--out", default="", help="Output directory root for snapshots.")
    parser.add_argument("--cache-dir", default="", help="Derived snapshot cache directory.")
    parser.add_argument("--width", type=int, default=0)
    parser.add_argument("--height", type=int, default=0)
    parser.add_argument("--wireframe", action="store_true")
    args = parser.parse_args()

    result = run_capture(
        repo_root=str(args.repo_root),
        renderer=str(args.renderer),
        input_path=str(args.input),
        out_dir=str(args.out),
        cache_dir=str(args.cache_dir),
        width=int(args.width),
        height=int(args.height),
        wireframe=bool(args.wireframe),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
